# Agent Instructions — Citedy Skills

This file tells AI agents how to maintain and publish this package.

## Repository

- **GitHub**: https://github.com/Citedy/skills
- **npm**: https://www.npmjs.com/package/@citedy/skills
- **Local path**: `/Users/dmitrisergeev/Dev/citedy-skills`

## Directory Structure

```
citedy-skills/
├── package.json          # npm package config (bump version here)
├── bin/cli.js            # CLI installer (npx @citedy/skills install)
├── skills/               # All skills live here
│   ├── <skill-name>/
│   │   ├── SKILL.md      # Claude Code skill definition
│   │   ├── scripts/run.js # Executable extractor script
│   │   ├── references/    # Docs for the skill
│   │   └── agents/        # OpenAI/Codex agent configs
├── commands/              # Slash command templates
│   └── <command-name>.md
├── AGENTS.md              # This file
├── README.md              # Public documentation
├── LICENSE                # MIT
└── .env.example
```

## Adding a New Skill

### Skill Types

1. **Extraction skills** — have `scripts/run.js`, require API keys (e.g., AnyCrawl)
2. **Knowledge skills** — SKILL.md + references only, no scripts, no API keys (e.g., schema-markup, icon-design)
3. **Agent Team skills** — require Claude Code Agent Teams API (TeamCreate, TaskCreate, SendMessage)

### 1. Create skill directory

```
skills/<skill-name>/
├── SKILL.md              # Required — Claude Code reads this
├── scripts/run.js        # Optional — executable Node.js script (extraction skills)
├── references/           # Optional — docs, notes, checklists
└── agents/openai.yaml    # Optional — Codex/OpenAI config
```

### 2. Create slash command

Add `commands/<command-name>.md`:

```markdown
---
description: Short description of what the command does
---
Treat `$1` as a required URL/input.
If `$1` is missing, ask the user and stop.

Run:
\```bash
node .claude/skills/<skill-name>/scripts/run.js "$1"
\```

Then read the JSON summary and present key fields to the user.
```

### 3. Register in CLI catalog

Edit `bin/cli.js` — add entry to `CATALOG`:

```js
const CATALOG = {
  // ... existing entries
  newskill: {
    skill: "skill-directory-name",
    command: "command-name.md",
    description: "One-line description",
  },
};
```

### 4. Update README.md

Add the new skill to the table in README.md.

### 5. Bump version

In `package.json`, bump the version:
- New skill → minor bump (1.0.0 → 1.1.0)
- Fix/improvement → patch bump (1.0.0 → 1.0.1)

## Publishing Workflow

**Every change follows this exact sequence:**

```bash
# 1. Verify everything works
cd /Users/dmitrisergeev/Dev/citedy-skills
node bin/cli.js list

# 2. Commit and push to GitHub
git add -A
git commit -m "feat: add <skill-name> skill"
git push origin main

# 3. Publish to npm
npm publish --access public
```

### First-time npm setup

```bash
# Login to npm (one-time)
npm login

# Verify @citedy scope is available
npm whoami
```

### Version bumping shortcut

```bash
npm version patch   # 1.0.0 → 1.0.1 (fixes)
npm version minor   # 1.0.0 → 1.1.0 (new skills)
npm version major   # 1.0.0 → 2.0.0 (breaking changes)
```

## Script Requirements

All `scripts/run.js` files MUST:

1. **Read API keys from environment or `.env.local`** — never hardcode
2. **Use relative paths** — `path.resolve(__dirname, ...)` for sibling references
3. **Write output to `/tmp/`** — JSON artifact with full extraction
4. **Print compact JSON summary to stdout** — for Claude to parse
5. **Print errors to stderr** — `console.error()`, then `process.exit(1)`
6. **Handle non-JSON API responses** — try/catch around `JSON.parse`
7. **Work with Node.js 18+** — no ESM-only dependencies

## Sync to saas-blog

After publishing, sync updated skills back to saas-blog:

```bash
# From saas-blog root
for skill in skills/*/; do
  name=$(basename "$skill")
  cp -R /Users/dmitrisergeev/Dev/citedy-skills/skills/$name .claude/skills/$name
  cp -R /Users/dmitrisergeev/Dev/citedy-skills/skills/$name .agents/skills/$name
done
```
