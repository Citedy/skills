# Token Usage Analyzer

Analyze Claude Code token consumption and estimated costs across projects and sessions. Detects model (Opus/Sonnet/Haiku) automatically and applies correct pricing.

## Install

```bash
npx @citedy/skills install token-usage
```

## Usage

```
/token-usage              # all time
/token-usage today        # today only
/token-usage week         # last 7 days
/token-usage month        # last 30 days
/token-usage 3            # last 3 days
/token-usage 2026-04-01   # since date
/token-usage --compare week   # this week vs last week
```

## Example: Weekly Summary

```
/token-usage week
```

```
======================================================================
  1,612,366,482 tokens | $5,192.51 est. | 16 sessions | 4 projects
======================================================================

  By model:
    opus      1,611,667,726 tokens   $3,158.63  (61%)
    haiku           698,756 tokens       $0.53  (0%)

Project                                  Sessions         Tokens       Cost  Agents
-----------------------------------------------------------------------------------
my-saas-app                                    11  1,347,520,766  $4,647.07     125
data-pipeline                                   1    162,512,163    $311.63      29
marketing-site                                  3    101,634,797    $233.28      18
side-project                                    1        698,756      $0.53       0

Top 5 costliest sessions:
  [2026-04-04] my-saas-app: $1,106.34 (opus) — code review + PR analysis
  [2026-03-31] my-saas-app: $463.06 (opus) — feature implementation sprint
  [2026-04-02] my-saas-app: $432.93 (opus) — refactoring + tests
  [2026-04-03] data-pipeline: $290.17 (opus) — sentry error triage
  [2026-04-02] my-saas-app: $238.41 (opus) — brainstorming + design doc
```

## Example: Period Comparison

```
/token-usage --compare week
```

```
======================================================================
  COMPARISON: Current vs Previous Period
======================================================================
                              Current       Previous     Change
  ------------------------------------------------------------
                  Cost      $5,192.51      $4,494.44      ▲ 16%
                Tokens  1,612,366,482  1,808,585,488      ▼ 11%
              Sessions             16             17       ▼ 6%

  By project:
    my-saas-app                     $4,647.07 vs  $3,553.93       ▲ 31%
    data-pipeline                     $311.63 vs      $8.41     ▲ 3607%
    marketing-site                    $233.28 vs    $932.10       ▼ 75%
    side-project                        $0.53 vs      $0.00         NEW
```

## Example: Markdown Report

Saved to `~/.claude/token-usage-reports/token_report.md`:

```markdown
## Grand Totals

- **Estimated cost**: $5,192.51
- **Sessions**: 16 (172 subagents)
- **Total tokens**: 1,612,366,482

### By Model

| Model | Tokens | Cost | % of Total |
|-------|--------|------|------------|
| opus | 1,611,667,726 | $3,158.63 | 61% |
| haiku | 698,756 | $0.53 | 0% |

### vs Previous Period

| Metric | Current | Previous | Change |
|--------|---------|----------|--------|
| Cost | $5,192.51 | $4,494.44 | ▲ 16% |
| Tokens | 1,612,366,482 | 1,808,585,488 | ▼ 11% |
| Sessions | 16 | 17 | ▼ 6% |
```

## Features

- **Per-model pricing** — detects Opus/Sonnet/Haiku from session logs, applies correct rates
- **Period comparison** — `--compare` shows current vs previous period with ▲/▼ arrows
- **Project breakdown** — tokens and cost per project directory
- **Session ranking** — costliest sessions with first prompt preview
- **Subagent tracking** — counts and costs for spawned subagents
- **Time filtering** — today, week, month, N days, or specific date

## Pricing (per million tokens)

| Model | Input | Cache Create | Cache Read | Output |
|-------|-------|-------------|------------|--------|
| Opus | $15.00 | $18.75 | $1.50 | $75.00 |
| Sonnet | $3.00 | $3.75 | $0.30 | $15.00 |
| Haiku | $0.80 | $1.00 | $0.08 | $4.00 |

Model is detected automatically from the `model` field in each assistant message.

## Tips for Reducing Costs

- **Cache read is cheap** ($1.50/M vs $15/M input) — longer conversations benefit from caching
- **Subagents are expensive** — each spawns fresh context without cache. Use sparingly
- **Review costliest sessions** — often one runaway session costs more than a week of normal use
- **Switch to Sonnet for routine work** — 5x cheaper than Opus for non-critical tasks

## Requirements

- Python 3.8+
- Claude Code (session files in `~/.claude/projects/`)
- No external dependencies (stdlib only)

## Credit

Based on [kieranklaassen/token-analyzer](https://gist.github.com/kieranklaassen/7b2ebb39cbbb78cc2831497605d76cc6) with per-model pricing, period comparison, and skill packaging.
