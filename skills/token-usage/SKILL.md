---
name: token-usage
description: Analyze Claude Code token consumption and estimated costs across projects and sessions. Use when user asks about token usage, costs, spending, billing, how much they've used, or wants to optimize their Claude Code usage patterns.
---

# Token Usage Analyzer

Analyze token consumption patterns and estimate costs from Claude Code session files (`~/.claude/projects/`).

## What It Does

- Parses all JSONL session files to extract token metrics (input, cache creation, cache read, output)
- Groups usage by project and session
- Estimates costs based on Claude model pricing
- Identifies most expensive sessions and subagent usage
- Supports time range filtering (today, week, month, N days, specific date)
- Generates a detailed markdown report

## Usage

Run the analyzer with a time range argument:

```bash
python3 .claude/skills/token-usage/scripts/analyze.py $ARGUMENTS
```

### Arguments

| Argument | Example | Description |
|----------|---------|-------------|
| *(empty)* | | All time |
| `today` | `today` | Since midnight UTC |
| `week` | `week` | Last 7 days |
| `month` | `month` | Last 30 days |
| N (number) | `3` | Last N days |
| Date | `2026-04-01` | Since that date |
| Datetime | `2026-04-01 11:00` | Since that datetime |

### Output

The script prints a summary to stdout and saves a detailed report to:
```
~/.claude/plugins/token-usage/reports/token_report.md
```

## Cost Estimation

Estimates use Claude Opus 4 pricing (per million tokens):

| Token Type | Price/M |
|-----------|---------|
| Input | $15.00 |
| Cache creation | $18.75 |
| Cache read | $1.50 |
| Output | $75.00 |

> Actual costs may differ based on model (Sonnet = ~5x cheaper, Haiku = ~25x cheaper) and plan discounts.

## What the Report Includes

1. **Grand totals** — tokens, estimated cost, session count
2. **Per-project breakdown** — tokens, cost, subagent count per project
3. **Most costly sessions** — ranked by estimated cost with first prompt preview
4. **Subagent analysis** — which subagents consumed the most tokens

## Tips for Reducing Usage

- **Cache read is cheap** ($1.50/M vs $15/M for input) — long conversations benefit from cache
- **Subagents are expensive** — each spawns a fresh context. Use sparingly.
- **Review your costliest sessions** — often one runaway session costs more than a week of normal work
- **Use specific time ranges** to track daily/weekly spending patterns

## Requirements

- Python 3.8+
- Claude Code (session files in `~/.claude/projects/`)
- No external dependencies (stdlib only)
