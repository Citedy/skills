# Citedy Skills

Curated collection of [Claude Code](https://claude.com/claude-code) skills by [Citedy](https://www.citedy.com) — AI-powered SEO content automation.

## Quick Install

```bash
npx @citedy/skills install
```

This installs all skills + slash commands into your project's `.claude/` directory.

### Install specific skills

```bash
npx @citedy/skills install youtube tiktok
```

### Update existing skills

```bash
npx @citedy/skills update
```

## Available Skills

| Name | Skill | Slash Command | Description |
|------|-------|---------------|-------------|
| `youtube` | anycrawl-youtube-video-extractor | `/any-youtube` | Extract structured metadata from any public YouTube video |
| `instagram` | anycrawl-instagram-scraper | `/any-instagram` | Extract public Instagram profile, post, and reel data |
| `tiktok` | anycrawl-tiktok-scraper | `/any-tiktok` | Extract public TikTok video, profile, and hashtag data |
| `social` | anycrawl-social-extractor | `/any-social` | Auto-detect platform and route to the correct extractor |

All skills use the [AnyCrawl](https://anycrawl.dev) Scrape API for LLM-powered structured data extraction.

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

Or manually — clone and copy:

```bash
git clone https://github.com/Citedy/skills.git citedy-skills
cp -R citedy-skills/skills/anycrawl-youtube-video-extractor .claude/skills/
cp -R citedy-skills/commands/any-youtube.md .claude/commands/
```

## Usage

Once installed, Claude Code automatically uses skills when you provide a social media URL. Or invoke directly:

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
