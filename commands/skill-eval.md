---
description: Validate and audit quality of AI agent slash commands and skills — checks YAML frontmatter, description length, jargon, directive verbs, and duplicates. Run after adding or editing commands.
---
Run the skill quality evaluator on the project's commands directory:

```bash
node .claude/skills/skill-quality-eval/scripts/run-eval.js
```

Read the output and present the results to the user. If there are failures, explain each issue and suggest fixes.
