---
description: Analyze Claude Code token usage and estimated costs
---
Run the token usage analyzer with the provided arguments.

`$ARGUMENTS` can be: `today`, `week`, `month`, a number of days (e.g. `3`), a date (`2026-04-01`), or empty for all time.

```bash
python3 .claude/skills/token-usage/scripts/analyze.py $ARGUMENTS
```

After running, read the output and present a concise summary to the user:
- Grand totals (tokens + estimated cost)
- Per-project breakdown
- Top 3 costliest sessions

The full report is saved to `~/.claude/token-usage-reports/token_report.md`.
