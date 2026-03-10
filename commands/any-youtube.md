---
description: Extract all available public YouTube watch-page data from a URL via AnyCrawl
---
Treat `$1` as a required public YouTube watch URL.

If `$1` is missing, ask the user for the link and stop.

Run:

```bash
node .claude/skills/anycrawl-youtube-video-extractor/scripts/run.js "$1"
```

Then:

1. Read the JSON summary printed by the script.
2. Open the `outputPath` artifact if you need fuller details.
3. Summarize the title, channel, visibility, dates, duration, stats, transcript availability, endscreen items, and screenshot URL.
4. Mention any fields that AnyCrawl could not derive.
