#!/usr/bin/env node

const fs = require("fs");
const path = require("path");

const PLATFORM = "tiktok";
const DEFAULT_TIMEOUT = 120000;
const FORMATS = ["json", "markdown"];

function findApiKey() {
  const direct =
    process.env.ANYCRAWL_API_KEY_DEV ||
    process.env.ANY_CRAWL_API_KEY_DEV;

  if (direct) {
    return direct.trim();
  }

  const searchRoots = [];
  let current = process.cwd();
  while (true) {
    searchRoots.push(current);
    const parent = path.dirname(current);
    if (parent === current) {
      break;
    }
    current = parent;
  }

  for (const root of searchRoots) {
    for (const filename of [".env.local", ".env"]) {
      const fullPath = path.join(root, filename);
      if (!fs.existsSync(fullPath)) {
        continue;
      }
      const file = fs.readFileSync(fullPath, "utf8");
      for (const key of [
        "ANYCRAWL_API_KEY_DEV",
        "ANY_CRAWL_API_KEY_DEV",
      ]) {
        const match = file.match(new RegExp(`^${key}=(.*)$`, "m"));
        if (match) {
          return match[1].trim().replace(/^['"]|['"]$/g, "");
        }
      }
    }
  }

  throw new Error(
    "Missing AnyCrawl API key. Set ANYCRAWL_API_KEY_DEV or ANY_CRAWL_API_KEY_DEV."
  );
}

function nullable(type) {
  return { type };
}

function arrayOf(itemSchema) {
  return { type: "array", items: itemSchema, default: [] };
}

function requireUrl(input) {
  if (!input) {
    throw new Error("Usage: node run.js <tiktok-url> [output-path]");
  }

  const value = new URL(input);
  if (!value.hostname.includes("tiktok.com")) {
    throw new Error("Expected a TikTok URL.");
  }

  const pathname = value.pathname;
  const isVideo = /^\/@[^/]+\/video\/\d+/.test(pathname);
  const isProfile = /^\/@[^/]+\/?$/.test(pathname);
  const isHashtag = /^\/tag\/[^/]+/.test(pathname);

  if (!isVideo && !isProfile && !isHashtag) {
    throw new Error(
      "Unsupported TikTok URL. Use a public video, profile, or hashtag URL."
    );
  }

  return value.toString();
}

function schema() {
  return {
    type: "object",
    additionalProperties: false,
    properties: {
      platform: { type: "string" },
      pageType: { type: "string" },
      sourceUrl: { type: "string" },
      videoId: nullable("string"),
      caption: nullable("string"),
      createdAtISO: nullable("string"),
      hashtags: arrayOf({ type: "string" }),
      author: {
        type: "object",
        additionalProperties: false,
        properties: {
          username: nullable("string"),
          displayName: nullable("string"),
          profileUrl: nullable("string"),
          avatarUrl: nullable("string"),
          bio: nullable("string"),
        },
      },
      profile: {
        type: "object",
        additionalProperties: false,
        properties: {
          username: nullable("string"),
          displayName: nullable("string"),
          profileUrl: nullable("string"),
          avatarUrl: nullable("string"),
          bio: nullable("string"),
          followers: nullable("number"),
          following: nullable("number"),
          likes: nullable("number"),
        },
      },
      hashtag: {
        type: "object",
        additionalProperties: false,
        properties: {
          name: nullable("string"),
          views: nullable("number"),
        },
      },
      music: {
        type: "object",
        additionalProperties: false,
        properties: {
          name: nullable("string"),
          artist: nullable("string"),
          url: nullable("string"),
        },
      },
      media: {
        type: "object",
        additionalProperties: false,
        properties: {
          coverUrl: nullable("string"),
          videoUrl: nullable("string"),
          durationText: nullable("string"),
          format: nullable("string"),
        },
      },
      stats: {
        type: "object",
        additionalProperties: false,
        properties: {
          views: nullable("number"),
          likes: nullable("number"),
          comments: nullable("number"),
          favorites: nullable("number"),
          shares: nullable("number"),
        },
      },
      items: arrayOf({
        type: "object",
        additionalProperties: false,
        properties: {
          id: nullable("string"),
          url: nullable("string"),
          caption: nullable("string"),
          coverUrl: nullable("string"),
          authorUsername: nullable("string"),
          likes: nullable("number"),
          comments: nullable("number"),
          shares: nullable("number"),
        },
      }),
    },
    required: ["platform", "pageType", "sourceUrl"],
  };
}

function buildPayload(url, attempt) {
  return {
    url,
    engine: "playwright",
    proxy: "stealth",
    formats: FORMATS,
    timeout: DEFAULT_TIMEOUT,
    retry: true,
    only_main_content: false,
    max_age: 0,
    extract_source: "html",
    wait_for: attempt.waitFor,
    wait_until: attempt.waitUntil,
    json_options: {
      schema_name: "tiktok_public_page",
      schema_description:
        "Normalized public TikTok extraction for video, profile, and hashtag pages.",
      user_prompt:
        "Extract as much public TikTok data as the page reveals. Identify whether the URL is a video, profile, or hashtag page. Use null for missing scalar fields, [] for missing lists, and never invent values. Prefer numeric counts when the page makes them derivable.",
      schema: schema(),
    },
  };
}

function richnessScore(value) {
  if (value == null) {
    return 0;
  }
  if (Array.isArray(value)) {
    return value.reduce((total, item) => total + richnessScore(item), value.length ? 1 : 0);
  }
  if (typeof value === "object") {
    return Object.values(value).reduce((total, item) => total + richnessScore(item), 0);
  }
  if (typeof value === "string") {
    return value.trim() ? 1 : 0;
  }
  return 1;
}

async function scrapeOnce(apiKey, payload) {
  const response = await fetch("https://api.anycrawl.dev/v1/scrape", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${apiKey}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  const text = await response.text();

  let json;
  try {
    json = JSON.parse(text);
  } catch {
    throw new Error(
      `AnyCrawl returned non-JSON response (${response.status}): ${text.slice(0, 200)}`
    );
  }

  if (!response.ok || !json.success) {
    throw new Error(`AnyCrawl scrape failed (${response.status}): ${text}`);
  }

  return json;
}

function outputPathFor(url, provided) {
  if (provided) {
    return path.resolve(provided);
  }

  const slug = url
    .replace(/^https?:\/\//, "")
    .replace(/[^a-zA-Z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "")
    .slice(0, 80);

  return path.join("/tmp", `${PLATFORM}-${slug}-${Date.now()}.json`);
}

async function main() {
  const url = requireUrl(process.argv[2]);
  const outputPath = outputPathFor(url, process.argv[3]);
  const apiKey = findApiKey();
  const attempts = [
    { waitFor: 3500, waitUntil: "load" },
    { waitFor: 6500, waitUntil: "networkidle" },
  ];

  let best = null;

  for (let index = 0; index < attempts.length; index += 1) {
    const attempt = attempts[index];
    const payload = buildPayload(url, attempt);
    const response = await scrapeOnce(apiKey, payload);
    const normalized = response.data.json ?? null;
    const score = richnessScore(normalized);

    best = {
      attempt: index + 1,
      score,
      payload,
      response,
    };

    if (score >= 8) {
      break;
    }
  }

  const finalOutput = {
    platform: PLATFORM,
    inputUrl: url,
    finishedAt: new Date().toISOString(),
    request: best.payload,
    normalized: {
      ...(best.response.data.json ?? {}),
      screenshotUrl: best.response.data["screenshot@fullPage"] || null,
    },
    anycrawl: best.response.data,
  };

  fs.writeFileSync(outputPath, JSON.stringify(finalOutput, null, 2));

  const summary = {
    ok: true,
    platform: PLATFORM,
    inputUrl: url,
    outputPath,
    attemptUsed: best.attempt,
    jobId: best.response.data.jobId,
    title: best.response.data.title ?? null,
    pageType: finalOutput.normalized.pageType ?? null,
    screenshotUrl: finalOutput.normalized.screenshotUrl,
    extractedKeys: Object.keys(best.response.data.json ?? {}),
  };

  process.stdout.write(`${JSON.stringify(summary, null, 2)}\n`);
}

main().catch((error) => {
  console.error(error.message);
  process.exit(1);
});
