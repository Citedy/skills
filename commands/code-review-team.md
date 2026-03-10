---
description: Parallel multi-agent code review with 4 specialized reviewers (requires Claude Code Agent Teams)
---
Treat `$1` as optional PR number or review target.

Read `.claude/skills/code-review-agent-team/SKILL.md` and follow the full workflow:
1. Determine review target (uncommitted, staged, PR, last commit)
2. Capture diff
3. Spawn 4 reviewer agents in parallel
4. Collect findings and present unified report
