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

| Name | Slash Command | Description |
|------|---------------|-------------|
| `youtube` | `/any-youtube` | Extract structured metadata from any public YouTube video |
| `instagram` | `/any-instagram` | Extract public Instagram profile, post, and reel data |
| `tiktok` | `/any-tiktok` | Extract public TikTok video, profile, and hashtag data |
| `social` | `/any-social` | Auto-detect platform and route to the correct extractor |

More skills coming soon — SEO analysis, content generation, competitor research, and more.

All current skills use the [AnyCrawl](https://anycrawl.dev) Scrape API for LLM-powered structured data extraction.

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
