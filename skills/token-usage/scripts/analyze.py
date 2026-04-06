#!/usr/bin/env python3
"""
Claude Code token usage analyzer.
Analyzes ~/.claude/projects/ JSONL files for token usage patterns.

Usage:
  python3 analyze.py                    # all time
  python3 analyze.py today              # today only
  python3 analyze.py week               # last 7 days
  python3 analyze.py month              # last 30 days
  python3 analyze.py 3                  # last 3 days
  python3 analyze.py 2026-04-01         # since specific date
  python3 analyze.py 2026-04-01 11:00   # since specific datetime
"""

import json
import os
import sys
from pathlib import Path
from collections import defaultdict
from datetime import datetime, timedelta, timezone

PROJECTS_DIR = Path.home() / ".claude" / "projects"
OUTPUT_DIR = Path.home() / ".claude" / "token-usage-reports"

# Pricing per million tokens (Opus 4, as of 2026-04)
PRICE_INPUT = 15.00
PRICE_CACHE_CREATE = 18.75
PRICE_CACHE_READ = 1.50
PRICE_OUTPUT = 75.00


def parse_time_arg(args):
    """Parse CLI arguments into a UTC cutoff datetime."""
    if not args:
        return None

    arg = " ".join(args).strip()
    if arg == "today":
        now = datetime.now(timezone.utc)
        return now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif arg == "week":
        return datetime.now(timezone.utc) - timedelta(days=7)
    elif arg == "month":
        return datetime.now(timezone.utc) - timedelta(days=30)
    elif arg.isdigit():
        return datetime.now(timezone.utc) - timedelta(days=int(arg))
    else:
        try:
            return datetime.fromisoformat(arg).replace(tzinfo=timezone.utc)
        except ValueError:
            print(f"Unknown time argument: {arg}", file=sys.stderr)
            return None


def estimate_cost(usage):
    """Estimate cost in USD from token usage dict."""
    input_t = usage.get("input_tokens", 0)
    cache_create = usage.get("cache_creation_input_tokens", 0)
    cache_read = usage.get("cache_read_input_tokens", 0)
    output_t = usage.get("output_tokens", 0)

    cost = (
        (input_t / 1_000_000) * PRICE_INPUT
        + (cache_create / 1_000_000) * PRICE_CACHE_CREATE
        + (cache_read / 1_000_000) * PRICE_CACHE_READ
        + (output_t / 1_000_000) * PRICE_OUTPUT
    )
    return cost


def extract_text_content(content):
    """Extract text from message content (string or list)."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict):
                if item.get("type") == "text":
                    parts.append(item.get("text", ""))
            elif isinstance(item, str):
                parts.append(item)
        return "\n".join(parts).strip()
    return ""


def is_human_prompt(msg_obj):
    """Check if this is a human-originated prompt (not tool result)."""
    content = msg_obj.get("message", {}).get("content", "")
    if isinstance(content, list):
        types = [i.get("type") for i in content if isinstance(i, dict)]
        if types and all(t == "tool_result" for t in types):
            return False
    return True


def parse_session(jsonl_path, is_subagent=False):
    """Parse a single JSONL session file."""
    usage_total = defaultdict(int)
    prompts = []
    agent_id = None
    session_id = None
    timestamp_start = None
    subagent_sessions = []

    try:
        with open(jsonl_path) as f:
            lines = f.readlines()
    except Exception:
        return None

    for line in lines:
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue

        msg_type = obj.get("type")
        ts = obj.get("timestamp")
        if ts and not timestamp_start:
            timestamp_start = ts

        if not agent_id:
            agent_id = obj.get("agentId")
        if not session_id:
            session_id = obj.get("sessionId")

        if msg_type == "assistant":
            usage = obj.get("message", {}).get("usage", {})
            usage_total["input_tokens"] += usage.get("input_tokens", 0)
            usage_total["cache_creation_input_tokens"] += usage.get("cache_creation_input_tokens", 0)
            usage_total["cache_read_input_tokens"] += usage.get("cache_read_input_tokens", 0)
            usage_total["output_tokens"] += usage.get("output_tokens", 0)

        elif msg_type == "user":
            user_type = obj.get("userType", "")
            is_sidechain = obj.get("isSidechain", False)
            content = obj.get("message", {}).get("content", "")
            text = extract_text_content(content)

            if text and not is_sidechain and is_human_prompt(obj) and user_type != "tool":
                prompts.append({
                    "text": text,
                    "timestamp": obj.get("timestamp"),
                    "entrypoint": obj.get("entrypoint", ""),
                })

    # Check for subagent sessions
    session_dir = jsonl_path.parent / jsonl_path.stem
    if session_dir.is_dir():
        subagents_dir = session_dir / "subagents"
        if subagents_dir.is_dir():
            for sub_file in subagents_dir.glob("*.jsonl"):
                sub_data = parse_session(sub_file, is_subagent=True)
                if sub_data:
                    sub_data["subagent_file"] = str(sub_file.name)
                    subagent_sessions.append(sub_data)

    total_tokens = sum(usage_total.values())

    return {
        "file": str(jsonl_path),
        "session_id": session_id or jsonl_path.stem,
        "agent_id": agent_id,
        "is_subagent": is_subagent,
        "timestamp_start": timestamp_start,
        "usage": dict(usage_total),
        "total_tokens": total_tokens,
        "cost": estimate_cost(usage_total),
        "prompts": prompts,
        "subagent_sessions": subagent_sessions,
    }


def get_project_name(project_dir_name):
    """Convert directory name to readable project name."""
    name = project_dir_name
    # Strip common home dir prefixes
    for prefix in ["-Users-", "Users-"]:
        idx = name.find(prefix)
        if idx >= 0:
            rest = name[idx + len(prefix):]
            # Skip username segment
            slash = rest.find("-")
            if slash > 0:
                name = rest[slash + 1:]
            break
    return name or project_dir_name


def session_in_range(session, cutoff):
    if not cutoff or not session["timestamp_start"]:
        return True
    try:
        ts = datetime.fromisoformat(session["timestamp_start"].replace("Z", "+00:00"))
        return ts >= cutoff
    except ValueError:
        return True


def analyze_all(cutoff):
    """Analyze all projects and sessions."""
    projects = defaultdict(list)

    for project_dir in sorted(PROJECTS_DIR.iterdir()):
        if not project_dir.is_dir():
            continue
        project_name = get_project_name(project_dir.name)

        for jsonl_file in sorted(project_dir.glob("*.jsonl")):
            session = parse_session(jsonl_file)
            if session and session["total_tokens"] > 0 and session_in_range(session, cutoff):
                projects[project_name].append(session)

    return projects


def fmt(n):
    return f"{n:,}"


def fmt_cost(c):
    return f"${c:,.2f}"


def summarize_projects(projects):
    summaries = []
    for project_name, sessions in projects.items():
        total = defaultdict(int)
        all_subagent_tokens = 0
        subagent_count = 0
        total_cost = 0.0

        for session in sessions:
            for k, v in session["usage"].items():
                total[k] += v
            total_cost += session["cost"]
            for sub in session["subagent_sessions"]:
                all_subagent_tokens += sub["total_tokens"]
                subagent_count += 1
                total_cost += sub["cost"]

        summaries.append({
            "project": project_name,
            "sessions": len(sessions),
            "usage": dict(total),
            "total_tokens": sum(total.values()),
            "cost": total_cost,
            "subagent_tokens": all_subagent_tokens,
            "subagent_count": subagent_count,
        })

    summaries.sort(key=lambda x: x["total_tokens"], reverse=True)
    return summaries


def find_costly_sessions(projects, top_n=20):
    all_sessions = []
    for project_name, sessions in projects.items():
        for session in sessions:
            all_sessions.append((project_name, session))
    all_sessions.sort(key=lambda x: x[1]["cost"], reverse=True)
    return all_sessions[:top_n]


def write_report(projects, summaries, cutoff):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    report_path = OUTPUT_DIR / "token_report.md"

    lines = []
    date_range = f"Since {cutoff.strftime('%Y-%m-%d %H:%M')}" if cutoff else "All time"
    lines.append("# Claude Code Token Usage Analysis")
    lines.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Range: {date_range}\n")

    grand_input = sum(s["usage"].get("input_tokens", 0) for s in summaries)
    grand_cache_create = sum(s["usage"].get("cache_creation_input_tokens", 0) for s in summaries)
    grand_cache_read = sum(s["usage"].get("cache_read_input_tokens", 0) for s in summaries)
    grand_output = sum(s["usage"].get("output_tokens", 0) for s in summaries)
    grand_total = sum(s["total_tokens"] for s in summaries)
    grand_cost = sum(s["cost"] for s in summaries)
    total_sessions = sum(s["sessions"] for s in summaries)
    total_subagent_tokens = sum(s["subagent_tokens"] for s in summaries)
    total_subagent_count = sum(s["subagent_count"] for s in summaries)

    lines.append("## Grand Totals\n")
    lines.append(f"- **Projects**: {len(summaries)}")
    lines.append(f"- **Sessions**: {total_sessions:,}")
    lines.append(f"- **Estimated cost**: {fmt_cost(grand_cost)}")
    lines.append(f"- **Total tokens**: {fmt(grand_total)}")
    lines.append(f"  - Input: {fmt(grand_input)} ({fmt_cost(grand_input / 1e6 * PRICE_INPUT)})")
    lines.append(f"  - Cache creation: {fmt(grand_cache_create)} ({fmt_cost(grand_cache_create / 1e6 * PRICE_CACHE_CREATE)})")
    lines.append(f"  - Cache read: {fmt(grand_cache_read)} ({fmt_cost(grand_cache_read / 1e6 * PRICE_CACHE_READ)})")
    lines.append(f"  - Output: {fmt(grand_output)} ({fmt_cost(grand_output / 1e6 * PRICE_OUTPUT)})")
    lines.append(f"- **Subagent sessions**: {total_subagent_count:,} ({fmt(total_subagent_tokens)} tokens)")
    lines.append("")

    lines.append("## By Project\n")
    lines.append("| Project | Sessions | Total Tokens | Est. Cost | Subagents |")
    lines.append("|---------|----------|-------------|-----------|-----------|")
    for s in summaries:
        lines.append(f"| {s['project']} | {s['sessions']} | {fmt(s['total_tokens'])} | {fmt_cost(s['cost'])} | {s['subagent_count']} |")
    lines.append("")

    lines.append("## Most Costly Sessions\n")
    costly = find_costly_sessions(projects, top_n=15)
    for i, (proj, session) in enumerate(costly, 1):
        ts = session["timestamp_start"][:10] if session["timestamp_start"] else "?"
        first_prompt = session["prompts"][0]["text"][:100].replace("\n", " ") if session["prompts"] else ""
        lines.append(f"{i}. **[{ts}] {proj}** — {fmt_cost(session['cost'])} ({fmt(session['total_tokens'])} tokens, {len(session['subagent_sessions'])} subagents)")
        if first_prompt:
            lines.append(f"   > {first_prompt}")
        lines.append("")

    with open(report_path, "w") as f:
        f.write("\n".join(lines))
    return report_path


def print_summary(summaries, projects):
    grand_total = sum(s["total_tokens"] for s in summaries)
    grand_cost = sum(s["cost"] for s in summaries)
    total_sessions = sum(s["sessions"] for s in summaries)

    print(f"\n{'='*70}")
    print(f"  {fmt(grand_total)} tokens | {fmt_cost(grand_cost)} est. | {total_sessions} sessions | {len(summaries)} projects")
    print(f"{'='*70}\n")

    print(f"{'Project':<40} {'Sessions':>8} {'Tokens':>14} {'Cost':>10} {'Agents':>7}")
    print("-" * 83)
    for s in summaries[:20]:
        print(f"{s['project'][:40]:<40} {s['sessions']:>8,} {fmt(s['total_tokens']):>14} {fmt_cost(s['cost']):>10} {s['subagent_count']:>7,}")

    print(f"\nTop 5 costliest sessions:")
    for proj, session in find_costly_sessions(projects, top_n=5):
        ts = session["timestamp_start"][:10] if session["timestamp_start"] else "?"
        first_prompt = session["prompts"][0]["text"][:60].replace("\n", " ") if session["prompts"] else ""
        print(f"  [{ts}] {proj[:30]}: {fmt_cost(session['cost'])} — {first_prompt}")


def main():
    cutoff = parse_time_arg(sys.argv[1:])
    if cutoff:
        print(f"Range: since {cutoff.strftime('%Y-%m-%d %H:%M')}")
    else:
        print("Range: all time")

    projects = analyze_all(cutoff)
    summaries = summarize_projects(projects)
    print_summary(summaries, projects)

    report_path = write_report(projects, summaries, cutoff)
    print(f"\nReport: {report_path}")


if __name__ == "__main__":
    main()
