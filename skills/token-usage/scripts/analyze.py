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
  python3 analyze.py --compare week     # this week vs previous week
  python3 analyze.py --compare 3        # last 3 days vs previous 3 days
"""

import json
import sys
from pathlib import Path
from collections import defaultdict
from datetime import datetime, timedelta, timezone

PROJECTS_DIR = Path.home() / ".claude" / "projects"
OUTPUT_DIR = Path.home() / ".claude" / "token-usage-reports"

# Pricing per million tokens by model family
MODEL_PRICING = {
    "opus": {"input": 15.00, "cache_create": 18.75, "cache_read": 1.50, "output": 75.00},
    "sonnet": {"input": 3.00, "cache_create": 3.75, "cache_read": 0.30, "output": 15.00},
    "haiku": {"input": 0.80, "cache_create": 1.00, "cache_read": 0.08, "output": 4.00},
}
DEFAULT_PRICING = MODEL_PRICING["opus"]


def classify_model(model_str):
    """Classify a model string into opus/sonnet/haiku."""
    if not model_str:
        return "opus"
    m = model_str.lower()
    if "haiku" in m:
        return "haiku"
    if "sonnet" in m:
        return "sonnet"
    return "opus"


def estimate_cost_for_model(usage, model_family):
    """Estimate cost using model-specific pricing."""
    pricing = MODEL_PRICING.get(model_family, DEFAULT_PRICING)
    return (
        (usage.get("input_tokens", 0) / 1e6) * pricing["input"]
        + (usage.get("cache_creation_input_tokens", 0) / 1e6) * pricing["cache_create"]
        + (usage.get("cache_read_input_tokens", 0) / 1e6) * pricing["cache_read"]
        + (usage.get("output_tokens", 0) / 1e6) * pricing["output"]
    )


def parse_time_arg(args):
    """Parse CLI arguments into (cutoff_datetime, period_days_for_compare)."""
    compare_mode = False
    filtered_args = []
    for a in args:
        if a == "--compare":
            compare_mode = True
        else:
            filtered_args.append(a)

    if not filtered_args:
        return None, compare_mode, None

    arg = " ".join(filtered_args).strip()
    now = datetime.now(timezone.utc)

    if arg == "today":
        cutoff = now.replace(hour=0, minute=0, second=0, microsecond=0)
        return cutoff, compare_mode, 1
    elif arg == "week":
        return now - timedelta(days=7), compare_mode, 7
    elif arg == "month":
        return now - timedelta(days=30), compare_mode, 30
    elif arg.isdigit():
        days = int(arg)
        return now - timedelta(days=days), compare_mode, days
    else:
        try:
            return datetime.fromisoformat(arg).replace(tzinfo=timezone.utc), compare_mode, None
        except ValueError:
            print(f"Unknown argument: {arg}", file=sys.stderr)
            return None, compare_mode, None


def extract_text_content(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict) and item.get("type") == "text":
                parts.append(item.get("text", ""))
            elif isinstance(item, str):
                parts.append(item)
        return "\n".join(parts).strip()
    return ""


def is_human_prompt(msg_obj):
    content = msg_obj.get("message", {}).get("content", "")
    if isinstance(content, list):
        types = [i.get("type") for i in content if isinstance(i, dict)]
        if types and all(t == "tool_result" for t in types):
            return False
    return True


def parse_session(jsonl_path, is_subagent=False):
    """Parse a single JSONL session file with per-model tracking."""
    usage_by_model = defaultdict(lambda: defaultdict(int))
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
            msg = obj.get("message", {})
            usage = msg.get("usage", {})
            model = classify_model(msg.get("model", ""))

            usage_by_model[model]["input_tokens"] += usage.get("input_tokens", 0)
            usage_by_model[model]["cache_creation_input_tokens"] += usage.get("cache_creation_input_tokens", 0)
            usage_by_model[model]["cache_read_input_tokens"] += usage.get("cache_read_input_tokens", 0)
            usage_by_model[model]["output_tokens"] += usage.get("output_tokens", 0)

        elif msg_type == "user":
            user_type = obj.get("userType", "")
            is_sidechain = obj.get("isSidechain", False)
            content = obj.get("message", {}).get("content", "")
            text = extract_text_content(content)

            if text and not is_sidechain and is_human_prompt(obj) and user_type != "tool":
                prompts.append({"text": text, "timestamp": obj.get("timestamp")})

    # Subagent sessions
    session_dir = jsonl_path.parent / jsonl_path.stem
    if session_dir.is_dir():
        subagents_dir = session_dir / "subagents"
        if subagents_dir.is_dir():
            for sub_file in subagents_dir.glob("*.jsonl"):
                sub_data = parse_session(sub_file, is_subagent=True)
                if sub_data:
                    sub_data["subagent_file"] = str(sub_file.name)
                    subagent_sessions.append(sub_data)

    # Compute totals
    total_usage = defaultdict(int)
    total_cost = 0.0
    for model, usage in usage_by_model.items():
        for k, v in usage.items():
            total_usage[k] += v
        total_cost += estimate_cost_for_model(usage, model)

    total_tokens = sum(total_usage.values())

    return {
        "file": str(jsonl_path),
        "session_id": session_id or jsonl_path.stem,
        "agent_id": agent_id,
        "is_subagent": is_subagent,
        "timestamp_start": timestamp_start,
        "usage": dict(total_usage),
        "usage_by_model": {k: dict(v) for k, v in usage_by_model.items()},
        "total_tokens": total_tokens,
        "cost": total_cost,
        "prompts": prompts,
        "subagent_sessions": subagent_sessions,
    }


def get_project_name(project_dir_name):
    name = project_dir_name
    for prefix in ["-Users-", "Users-"]:
        idx = name.find(prefix)
        if idx >= 0:
            rest = name[idx + len(prefix):]
            slash = rest.find("-")
            if slash > 0:
                name = rest[slash + 1:]
            break
    return name or project_dir_name


def session_in_range(session, cutoff, end=None):
    if not cutoff or not session["timestamp_start"]:
        return True
    try:
        ts = datetime.fromisoformat(session["timestamp_start"].replace("Z", "+00:00"))
        if ts < cutoff:
            return False
        if end and ts >= end:
            return False
        return True
    except ValueError:
        return True


def analyze_all(cutoff, end=None):
    projects = defaultdict(list)
    for project_dir in sorted(PROJECTS_DIR.iterdir()):
        if not project_dir.is_dir():
            continue
        project_name = get_project_name(project_dir.name)
        for jsonl_file in sorted(project_dir.glob("*.jsonl")):
            session = parse_session(jsonl_file)
            if session and session["total_tokens"] > 0 and session_in_range(session, cutoff, end):
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
        model_totals = defaultdict(lambda: defaultdict(int))
        all_subagent_tokens = 0
        subagent_count = 0
        total_cost = 0.0

        for session in sessions:
            for k, v in session["usage"].items():
                total[k] += v
            for model, usage in session["usage_by_model"].items():
                for k, v in usage.items():
                    model_totals[model][k] += v
            total_cost += session["cost"]
            for sub in session["subagent_sessions"]:
                all_subagent_tokens += sub["total_tokens"]
                subagent_count += 1
                total_cost += sub["cost"]

        summaries.append({
            "project": project_name,
            "sessions": len(sessions),
            "usage": dict(total),
            "model_breakdown": {k: dict(v) for k, v in model_totals.items()},
            "total_tokens": sum(total.values()),
            "cost": total_cost,
            "subagent_tokens": all_subagent_tokens,
            "subagent_count": subagent_count,
        })

    summaries.sort(key=lambda x: x["cost"], reverse=True)
    return summaries


def find_costly_sessions(projects, top_n=15):
    all_sessions = []
    for project_name, sessions in projects.items():
        for session in sessions:
            all_sessions.append((project_name, session))
    all_sessions.sort(key=lambda x: x[1]["cost"], reverse=True)
    return all_sessions[:top_n]


def print_summary(summaries, projects, label=""):
    grand_total = sum(s["total_tokens"] for s in summaries)
    grand_cost = sum(s["cost"] for s in summaries)
    total_sessions = sum(s["sessions"] for s in summaries)

    # Model breakdown
    model_costs = defaultdict(float)
    model_tokens = defaultdict(int)
    for s in summaries:
        for model, usage in s["model_breakdown"].items():
            model_tokens[model] += sum(usage.values())
            model_costs[model] += estimate_cost_for_model(usage, model)

    if label:
        print(f"\n{'='*70}")
        print(f"  {label}")
    print(f"{'='*70}")
    print(f"  {fmt(grand_total)} tokens | {fmt_cost(grand_cost)} est. | {total_sessions} sessions | {len(summaries)} projects")
    print(f"{'='*70}")

    # Model breakdown
    if len(model_costs) > 1:
        print(f"\n  By model:")
        for model in sorted(model_costs, key=model_costs.get, reverse=True):
            pct = (model_costs[model] / grand_cost * 100) if grand_cost > 0 else 0
            print(f"    {model:<8} {fmt(model_tokens[model]):>14} tokens  {fmt_cost(model_costs[model]):>10}  ({pct:.0f}%)")
    print()

    print(f"{'Project':<40} {'Sessions':>8} {'Tokens':>14} {'Cost':>10} {'Agents':>7}")
    print("-" * 83)
    for s in summaries[:20]:
        print(f"{s['project'][:40]:<40} {s['sessions']:>8,} {fmt(s['total_tokens']):>14} {fmt_cost(s['cost']):>10} {s['subagent_count']:>7,}")

    print(f"\nTop 5 costliest sessions:")
    for proj, session in find_costly_sessions(projects, top_n=5):
        ts = session["timestamp_start"][:10] if session["timestamp_start"] else "?"
        models = ", ".join(sorted(session["usage_by_model"].keys()))
        first_prompt = session["prompts"][0]["text"][:50].replace("\n", " ") if session["prompts"] else ""
        print(f"  [{ts}] {proj[:25]}: {fmt_cost(session['cost'])} ({models}) — {first_prompt}")


def print_comparison(current_summaries, prev_summaries):
    """Print period-over-period comparison."""
    curr_cost = sum(s["cost"] for s in current_summaries)
    prev_cost = sum(s["cost"] for s in prev_summaries)
    curr_tokens = sum(s["total_tokens"] for s in current_summaries)
    prev_tokens = sum(s["total_tokens"] for s in prev_summaries)
    curr_sessions = sum(s["sessions"] for s in current_summaries)
    prev_sessions = sum(s["sessions"] for s in prev_summaries)

    def arrow(curr, prev):
        if prev == 0:
            return "NEW" if curr > 0 else "—"
        pct = ((curr - prev) / prev) * 100
        sym = "▲" if pct > 0 else "▼" if pct < 0 else "="
        return f"{sym} {abs(pct):.0f}%"

    print(f"\n{'='*70}")
    print(f"  COMPARISON: Current vs Previous Period")
    print(f"{'='*70}")
    print(f"  {'':>20} {'Current':>14} {'Previous':>14} {'Change':>10}")
    print(f"  {'-'*60}")
    print(f"  {'Cost':>20} {fmt_cost(curr_cost):>14} {fmt_cost(prev_cost):>14} {arrow(curr_cost, prev_cost):>10}")
    print(f"  {'Tokens':>20} {fmt(curr_tokens):>14} {fmt(prev_tokens):>14} {arrow(curr_tokens, prev_tokens):>10}")
    print(f"  {'Sessions':>20} {curr_sessions:>14,} {prev_sessions:>14,} {arrow(curr_sessions, prev_sessions):>10}")

    # Per-project comparison
    all_projects = set()
    curr_by_proj = {s["project"]: s for s in current_summaries}
    prev_by_proj = {s["project"]: s for s in prev_summaries}
    all_projects.update(curr_by_proj.keys())
    all_projects.update(prev_by_proj.keys())

    if all_projects:
        print(f"\n  By project:")
        rows = []
        for p in all_projects:
            cc = curr_by_proj.get(p, {}).get("cost", 0)
            pc = prev_by_proj.get(p, {}).get("cost", 0)
            rows.append((p, cc, pc))
        rows.sort(key=lambda x: x[1], reverse=True)
        for p, cc, pc in rows[:10]:
            print(f"    {p[:30]:<30} {fmt_cost(cc):>10} vs {fmt_cost(pc):>10}  {arrow(cc, pc):>10}")
    print()


def write_report(projects, summaries, cutoff, prev_summaries=None):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    report_path = OUTPUT_DIR / "token_report.md"

    lines = []
    date_range = f"Since {cutoff.strftime('%Y-%m-%d %H:%M')}" if cutoff else "All time"
    lines.append("# Claude Code Token Usage Analysis")
    lines.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Range: {date_range}\n")

    grand_cost = sum(s["cost"] for s in summaries)
    grand_total = sum(s["total_tokens"] for s in summaries)
    total_sessions = sum(s["sessions"] for s in summaries)
    total_subagent_count = sum(s["subagent_count"] for s in summaries)
    total_subagent_tokens = sum(s["subagent_tokens"] for s in summaries)

    # Model breakdown
    model_costs = defaultdict(float)
    model_tokens = defaultdict(int)
    for s in summaries:
        for model, usage in s["model_breakdown"].items():
            model_tokens[model] += sum(usage.values())
            model_costs[model] += estimate_cost_for_model(usage, model)

    lines.append("## Grand Totals\n")
    lines.append(f"- **Estimated cost**: {fmt_cost(grand_cost)}")
    lines.append(f"- **Sessions**: {total_sessions:,} ({total_subagent_count:,} subagents)")
    lines.append(f"- **Total tokens**: {fmt(grand_total)}")

    if model_costs:
        lines.append("\n### By Model\n")
        lines.append("| Model | Tokens | Cost | % of Total |")
        lines.append("|-------|--------|------|------------|")
        for model in sorted(model_costs, key=model_costs.get, reverse=True):
            pct = (model_costs[model] / grand_cost * 100) if grand_cost > 0 else 0
            lines.append(f"| {model} | {fmt(model_tokens[model])} | {fmt_cost(model_costs[model])} | {pct:.0f}% |")

    if prev_summaries:
        prev_cost = sum(s["cost"] for s in prev_summaries)
        prev_tokens = sum(s["total_tokens"] for s in prev_summaries)
        prev_sessions = sum(s["sessions"] for s in prev_summaries)
        def arrow(c, p):
            if p == 0: return "—"
            pct = ((c - p) / p) * 100
            return f"{'▲' if pct > 0 else '▼'} {abs(pct):.0f}%"
        lines.append("\n### vs Previous Period\n")
        lines.append("| Metric | Current | Previous | Change |")
        lines.append("|--------|---------|----------|--------|")
        lines.append(f"| Cost | {fmt_cost(grand_cost)} | {fmt_cost(prev_cost)} | {arrow(grand_cost, prev_cost)} |")
        lines.append(f"| Tokens | {fmt(grand_total)} | {fmt(prev_tokens)} | {arrow(grand_total, prev_tokens)} |")
        lines.append(f"| Sessions | {total_sessions} | {prev_sessions} | {arrow(total_sessions, prev_sessions)} |")

    lines.append("\n## By Project\n")
    lines.append("| Project | Sessions | Tokens | Cost | Subagents |")
    lines.append("|---------|----------|--------|------|-----------|")
    for s in summaries:
        lines.append(f"| {s['project']} | {s['sessions']} | {fmt(s['total_tokens'])} | {fmt_cost(s['cost'])} | {s['subagent_count']} |")

    lines.append("\n## Most Costly Sessions\n")
    for i, (proj, session) in enumerate(find_costly_sessions(projects, top_n=15), 1):
        ts = session["timestamp_start"][:10] if session["timestamp_start"] else "?"
        models = ", ".join(sorted(session["usage_by_model"].keys()))
        first_prompt = session["prompts"][0]["text"][:120].replace("\n", " ") if session["prompts"] else ""
        lines.append(f"{i}. **[{ts}] {proj}** — {fmt_cost(session['cost'])} ({models}, {len(session['subagent_sessions'])} subagents)")
        if first_prompt:
            lines.append(f"   > {first_prompt}")
        lines.append("")

    with open(report_path, "w") as f:
        f.write("\n".join(lines))
    return report_path


def main():
    cutoff, compare_mode, period_days = parse_time_arg(sys.argv[1:])

    if cutoff:
        print(f"Range: since {cutoff.strftime('%Y-%m-%d %H:%M')}")
    else:
        print("Range: all time")

    projects = analyze_all(cutoff)
    summaries = summarize_projects(projects)
    print_summary(summaries, projects, "CURRENT PERIOD" if compare_mode else "")

    prev_summaries = None
    if compare_mode and period_days and cutoff:
        prev_end = cutoff
        prev_start = cutoff - timedelta(days=period_days)
        print(f"\nPrevious period: {prev_start.strftime('%Y-%m-%d')} to {prev_end.strftime('%Y-%m-%d')}")
        prev_projects = analyze_all(prev_start, prev_end)
        prev_summaries = summarize_projects(prev_projects)
        print_summary(prev_summaries, prev_projects, "PREVIOUS PERIOD")
        print_comparison(summaries, prev_summaries)

    report_path = write_report(projects, summaries, cutoff, prev_summaries)
    print(f"\nReport: {report_path}")


if __name__ == "__main__":
    main()
