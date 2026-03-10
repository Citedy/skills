---
description: Extract all available public Instagram data from a URL via AnyCrawl
---
Treat `$1` as a required public Instagram URL.

If `$1` is missing, ask the user for the link and stop.

Run:

```bash
node .claude/skills/anycrawl-instagram-scraper/scripts/run.js "$1"
```

Then:

1. Read the JSON summary printed by the script.
2. Open the `outputPath` artifact if you need fuller details.
3. Summarize the Instagram page type, profile/owner info, media, stats, and screenshot URL.
4. Call out login-wall, consent-wall, or access-limited behavior if present.
