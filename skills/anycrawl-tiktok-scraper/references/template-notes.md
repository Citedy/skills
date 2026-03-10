# AnyCrawl TikTok Template Notes

Official sources reviewed on March 10, 2026:

- MCP setup guide: `https://docs.anycrawl.dev/en/general/mcp-setup-guides/claude-code`
- Scrape API: `https://docs.anycrawl.dev/en/openapi/scraping`
- Template page: `https://anycrawl.dev/template/tiktok-scraper`

Key template behavior:

- Supports public TikTok video detail URLs, hashtag pages, and profile pages.
- Uses Playwright and returns Markdown, JSON, and a full-page screenshot.
- Template docs call out these fields when available:
  - Video detail: caption text, timestamp, author info, likes, comments, favorites, shares, music name, cover, hashtags
  - Hashtag page: first-screen items and hashtag views
  - Profile page: videos, reposts, liked tab items plus best-effort profile metadata
- The template only promises first-screen list extraction for hashtag/profile pages. No pagination or auto-scroll.

Skill design choices:

- Use `POST /v1/scrape` rather than `crawl` because the user supplies one public URL.
- Use `playwright` + `proxy: "stealth"` + `json_options` to ask AnyCrawl for normalized structured data.
- Persist the full AnyCrawl response plus the normalized JSON into an output file so the agent can inspect raw artifacts without bloating the active context.
