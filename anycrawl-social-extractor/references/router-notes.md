# AnyCrawl Social Router Notes

This skill routes public URLs to the existing canonical skills in this repo:

- TikTok: `.claude/skills/anycrawl-tiktok-scraper/scripts/run.js`
- Instagram: `.claude/skills/anycrawl-instagram-scraper/scripts/run.js`
- YouTube: `.claude/skills/anycrawl-youtube-video-extractor/scripts/run.js`

Supported URL families:

- `tiktok.com`
- `instagram.com`
- `youtube.com/watch`
- `youtu.be`

The router intentionally delegates to the platform-specific extractor so platform schemas and retry logic stay in one canonical place per platform.
