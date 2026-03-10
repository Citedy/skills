# Citedy Skills

Curated collection of [Claude Code](https://claude.com/claude-code) skills by [Citedy](https://www.citedy.com) — AI-powered SEO content automation.

## Skills

| Skill | Description |
|-------|-------------|
| **anycrawl-youtube-video-extractor** | Extract structured metadata from any public YouTube video |
| **anycrawl-instagram-scraper** | Extract public Instagram profile, post, and reel data |
| **anycrawl-tiktok-scraper** | Extract public TikTok video, profile, and hashtag data |
| **anycrawl-social-extractor** | Auto-detect platform and route to the correct extractor |

All skills use the [AnyCrawl](https://anycrawl.dev) Scrape API to extract structured data via LLM-powered JSON extraction.

## Setup

### 1. Get an AnyCrawl API key

Sign up at [anycrawl.dev](https://anycrawl.dev) and grab your API key.

### 2. Add to your environment

```bash
# .env.local (or .env)
ANYCRAWL_API_KEY_DEV=ac-your-key-here
```

### 3. Install skills

Copy the skill folders into your project's `.claude/skills/` directory:

```bash
# Clone this repo
git clone https://github.com/Citedy/skills.git citedy-skills

# Copy the skills you need
cp -R citedy-skills/anycrawl-youtube-video-extractor .claude/skills/
cp -R citedy-skills/anycrawl-instagram-scraper .claude/skills/
cp -R citedy-skills/anycrawl-tiktok-scraper .claude/skills/
cp -R citedy-skills/anycrawl-social-extractor .claude/skills/
```

### 4. (Optional) Add slash commands

Create `.claude/commands/` files for quick access:

```markdown
<!-- .claude/commands/any-youtube.md -->
---
description: Extract YouTube video metadata via AnyCrawl
---
Treat `$1` as a required public YouTube watch URL.
If `$1` is missing, ask the user for the link and stop.

Run:
\```bash
node .claude/skills/anycrawl-youtube-video-extractor/scripts/run.js "$1"
\```

Then read the JSON summary and summarize the key fields.
```

## Usage

Once installed, Claude Code will automatically use the skills when you provide a social media URL. Or invoke directly:

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
- [Claude Code](https://claude.com/claude-code)

## License

MIT
