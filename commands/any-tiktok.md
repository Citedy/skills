---
description: Extract all available public TikTok data from a URL via AnyCrawl
---
Treat `$1` as a required public TikTok URL.

If `$1` is missing, ask the user for the link and stop.

Run:

```bash
node .claude/skills/anycrawl-tiktok-scraper/scripts/run.js "$1"
```

Then:

1. Read the JSON summary printed by the script.
2. Open the `outputPath` artifact if you need fuller details.
3. Summarize the TikTok page type, caption, author/profile, stats, hashtags, and screenshot URL.
4. Mention any missing fields or access limitations.
