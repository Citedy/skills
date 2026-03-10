---
description: Auto-detect TikTok, Instagram, or YouTube URL and extract all available public data via AnyCrawl
---
Treat `$1` as a required public social URL.

If `$1` is missing, ask the user for the link and stop.

Run:

```bash
node .claude/skills/anycrawl-social-extractor/scripts/run.js "$1"
```

Then:

1. Read the JSON summary printed by the script.
2. Open the `outputPath` artifact if you need fuller details.
3. Summarize the key extracted data for the user in a concise way.
4. Mention any platform limitations or missing fields that AnyCrawl could not derive.
