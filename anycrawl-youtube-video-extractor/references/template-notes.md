# AnyCrawl YouTube Video Template Notes

Official sources reviewed on March 10, 2026:

- MCP setup guide: `https://docs.anycrawl.dev/en/general/mcp-setup-guides/claude-code`
- Scrape API: `https://docs.anycrawl.dev/en/openapi/scraping`
- Template page: `https://anycrawl.dev/template/youtube-video-data-extractor`

Key template behavior:

- Focuses on a single public YouTube watch page.
- Template docs mention title, channel name and username, channel URL and ID, visibility, upload and publish dates, duration, views, likes, category, description, thumbnail, transcript or subtitles when available, endscreen recommendations, and age-restriction flag.
- Comments are explicitly not fetched by the official template.

Skill design choices:

- Use `POST /v1/scrape` because the user gives one public watch URL.
- Use `playwright` to render the watch page and `json_options` to request a structured extraction aligned with the template fields.
- Persist the full raw response so the agent can inspect transcript, HTML, markdown, links, and screenshot without forcing all of that into the chat context.
