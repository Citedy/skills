# Citedy Skills

Curated collection of [Claude Code](https://claude.com/claude-code) & [Codex](https://openai.com/codex) skills by [Citedy](https://www.citedy.com) — AI-powered SEO content automation.

> **This package is actively maintained.** We regularly add new skills and improve existing ones.
> Run `npx @citedy/skills update` to get the latest version at any time.

## Install

```bash
npx @citedy/skills install
```

That's it. All skills and slash commands are copied into your project's `.claude/` directory, ready to use.

### Install specific skills only

```bash
npx @citedy/skills install youtube tiktok
```

### Stay up to date

```bash
npx @citedy/skills@latest update
```

New skills are added regularly. Use `@latest` to make sure you always get the newest version — no stale cache.

### See what's available

```bash
npx @citedy/skills list
```

## Available Skills

### Extraction Skills

| Name | Slash Command | Description | Requires |
|------|---------------|-------------|----------|
| `youtube` | `/any-youtube` | Extract structured metadata from any public YouTube video | AnyCrawl API |
| `instagram` | `/any-instagram` | Extract public Instagram profile, post, and reel data | AnyCrawl API |
| `tiktok` | `/any-tiktok` | Extract public TikTok video, profile, and hashtag data | AnyCrawl API |
| `social` | `/any-social` | Auto-detect platform and route to the correct extractor | AnyCrawl API |

### Knowledge Skills (no API keys needed)

| Name | Slash Command | Description |
|------|---------------|-------------|
| `schema` | `/schema-markup` | Add, fix, or optimize schema.org JSON-LD structured data |
| `icons` | `/icon-design` | Select semantically appropriate icons (Lucide/Heroicons/Phosphor) |
| `domains` | `/domain-hunter` | Search domains, compare prices, find promo codes |
| `skill-eval` | `/skill-eval` | Validate slash command quality (frontmatter, jargon, descriptions) |

### Agent Team Skills (Claude Code only)

| Name | Slash Command | Description |
|------|---------------|-------------|
| `spawning-plan` | `/spawning-plan` | Design and spawn optimal agent teams |
| `code-review` | `/code-review-team` | Parallel multi-agent code review with 4 reviewers |

> Agent Team skills require Claude Code with Agent Teams support (TeamCreate, TaskCreate, SendMessage).

Extraction skills use the [AnyCrawl](https://anycrawl.dev) Scrape API for LLM-powered structured data extraction.

## Setup

### 1. Get an AnyCrawl API key

Sign up at [anycrawl.dev](https://anycrawl.dev) and get your API key.

### 2. Add to your environment

```bash
# .env.local (or .env)
ANYCRAWL_API_KEY_DEV=ac-your-key-here
```

### 3. Install

```bash
npx @citedy/skills install
```

## Usage

Once installed, Claude Code automatically picks up skills when you provide a social media URL. Or invoke directly:

```
/any-youtube https://www.youtube.com/watch?v=VIDEO_ID
/any-instagram https://www.instagram.com/username/
/any-tiktok https://www.tiktok.com/@user/video/VIDEO_ID
/any-social <any-supported-url>
```

## What gets extracted

Each skill returns a structured JSON artifact saved to `/tmp/` with:

- **`normalized`** — Platform-specific structured data (title, stats, channel/author, description, etc.)
- **`anycrawl`** — Raw AnyCrawl response with markdown content
- **`request`** — The exact API payload used

## Requirements

- Node.js 18+
- [AnyCrawl](https://anycrawl.dev) API key
- [Claude Code](https://claude.com/claude-code) or [Codex](https://openai.com/codex)

## License

MIT — [Citedy](https://www.citedy.com)
