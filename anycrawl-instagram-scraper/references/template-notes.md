# AnyCrawl Instagram Template Notes

Official sources reviewed on March 10, 2026:

- MCP setup guide: `https://docs.anycrawl.dev/en/general/mcp-setup-guides/claude-code`
- Scrape API: `https://docs.anycrawl.dev/en/openapi/scraping`
- Template page: `https://anycrawl.dev/template/instagram-scraper`

Key template behavior:

- Accepts one or more public Instagram URLs.
- Current documented coverage is strongest for public profiles, reels, and posts.
- Template notes also mention hashtags, places, comments, and broader pagination as roadmap or future-expansion items.
- Output is structured JSON plus Markdown where available.

Skill design choices:

- Use `POST /v1/scrape` because the request is a single URL, not a site crawl.
- Use `playwright` + `proxy: "stealth"` because Instagram frequently relies on dynamic rendering and consent walls.
- Ask AnyCrawl for normalized JSON via `json_options`, then persist the full raw response so the agent can inspect everything that was captured.
