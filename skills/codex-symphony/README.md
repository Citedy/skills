# Codex Symphony

Portable OpenAI Symphony bootstrap for any Git repository.

This package installs a local Symphony + Linear orchestration setup into the current repository without requiring a fixed absolute path. It is designed for developers who want to:

- run Symphony locally against a repo
- use Linear as the issue queue
- let Codex pick up `Todo` issues and work them in isolated workspaces
- reopen Codex later and restart everything with one command

## What It Installs

Inside the target repository:

- `WORKFLOW.symphony.md`
- `scripts/symphony/start-local.sh`
- `scripts/symphony/start-background.sh`
- `scripts/symphony/status.sh`
- `.env.symphony.example`

Inside the user environment:

- `~/.local/bin/codex-symphony`
- `~/.codex/skills/codex-symphony` symlink

## Quick Install

### From `Citedy/skills` Monorepo

If this package is published as a folder inside `github.com/Citedy/skills`, install it like this:

```bash
git clone https://github.com/Citedy/skills.git
cd /path/to/your-target-repo
bash /path/to/skills/codex-symphony/scripts/install.sh
```

Or explicitly target another repo:

```bash
bash /path/to/skills/codex-symphony/scripts/install.sh /absolute/path/to/your/repo
```

### From a Standalone Repo

If this package is later published as its own repository, the flow becomes:

```bash
git clone https://github.com/Citedy/codex-symphony.git
cd /path/to/your-target-repo
bash /path/to/codex-symphony/scripts/install.sh
```

### Direct Local Usage

Clone this package somewhere on disk, then from the repository you want to automate:

```bash
bash /path/to/codex-symphony/scripts/install.sh
```

Or explicitly target a repo path:

```bash
bash /path/to/codex-symphony/scripts/install.sh /absolute/path/to/your/repo
```

## Required Environment Variables

Copy `.env.symphony.example` into your repo env setup and set:

```bash
LINEAR_API_KEY=
LINEAR_PROJECT_SLUG=
SOURCE_REPO_URL=
SYMPHONY_WORKSPACE_ROOT=
SYMPHONY_PORT=4080
```

Optional:

```bash
GH_TOKEN=
```

## Start

From inside the target repository:

```bash
codex-symphony
```

That will:

1. start Symphony in the background if it is not already running
2. print the dashboard URL
3. open Codex in the current shell

## Dashboard

Default:

```text
http://127.0.0.1:4080/
```

## Status

```bash
./scripts/symphony/status.sh
```

## Notes

- This package writes `WORKFLOW.symphony.md`, not `WORKFLOW.md`, to avoid collisions with repo-specific files.
- The workflow assumes active Linear states `Todo` and `In Progress`.
- If your team uses different state names, edit `WORKFLOW.symphony.md`.
- The package is structured so it can live either inside `Citedy/skills` or in a dedicated `Citedy/codex-symphony` repository without internal file changes.

## Future Distribution

This package is ready for two share modes:

1. `github.com/Citedy/skills` as `codex-symphony/`
2. standalone repo `github.com/Citedy/codex-symphony`

Once the standalone repo exists, you can also expose it through your normal skill distribution channels such as `skill-installer` and `openskills`.
