#!/usr/bin/env node

const fs = require("fs");
const path = require("path");

const PLATFORM = "instagram";
const DEFAULT_TIMEOUT = 120000;
const FULL_FORMATS = ["json", "markdown"];
const LITE_FORMATS = ["json", "markdown"];

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
    throw new Error("Usage: node run.js <instagram-url> [output-path]");
  }

  const value = new URL(input);
  if (!value.hostname.includes("instagram.com")) {
    throw new Error("Expected an Instagram URL.");
  }

  const pathname = value.pathname;
  const isProfile = /^\/[^/]+\/?$/.test(pathname) && !pathname.startsWith("/reel/") && !pathname.startsWith("/p/");
  const isReel = /^\/reel\/[^/]+/.test(pathname);
  const isPost = /^\/p\/[^/]+/.test(pathname);

  if (!isProfile && !isReel && !isPost) {
    throw new Error(
      "Unsupported Instagram URL. Use a public profile, reel, or post URL."
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
      shortcode: nullable("string"),
      caption: nullable("string"),
      createdAtISO: nullable("string"),
      hashtags: arrayOf({ type: "string" }),
      mentions: arrayOf({ type: "string" }),
      owner: {
        type: "object",
        additionalProperties: false,
        properties: {
          username: nullable("string"),
          fullName: nullable("string"),
          profileUrl: nullable("string"),
          profilePicUrl: nullable("string"),
          biography: nullable("string"),
          isVerified: nullable("boolean"),
          isPrivate: nullable("boolean"),
        },
      },
      profile: {
        type: "object",
        additionalProperties: false,
        properties: {
          username: nullable("string"),
          fullName: nullable("string"),
          profileUrl: nullable("string"),
          profilePicUrl: nullable("string"),
          biography: nullable("string"),
          followers: nullable("number"),
          following: nullable("number"),
          posts: nullable("number"),
          isVerified: nullable("boolean"),
          isPrivate: nullable("boolean"),
          isBusinessAccount: nullable("boolean"),
        },
      },
      media: {
        type: "object",
        additionalProperties: false,
        properties: {
          displayUrl: nullable("string"),
          videoUrl: nullable("string"),
          isVideo: nullable("boolean"),
          width: nullable("number"),
          height: nullable("number"),
          durationSeconds: nullable("number"),
        },
      },
      stats: {
        type: "object",
        additionalProperties: false,
        properties: {
          views: nullable("number"),
          likes: nullable("number"),
          comments: nullable("number"),
        },
      },
      location: {
        type: "object",
        additionalProperties: false,
        properties: {
          name: nullable("string"),
          address: nullable("string"),
        },
      },
      comments: arrayOf({
        type: "object",
        additionalProperties: false,
        properties: {
          username: nullable("string"),
          text: nullable("string"),
          createdAtISO: nullable("string"),
          likes: nullable("number"),
        },
      }),
      items: arrayOf({
        type: "object",
        additionalProperties: false,
        properties: {
          shortcode: nullable("string"),
          url: nullable("string"),
          caption: nullable("string"),
          displayUrl: nullable("string"),
          isVideo: nullable("boolean"),
          likes: nullable("number"),
          comments: nullable("number"),
        },
      }),
    },
    required: ["platform", "pageType", "sourceUrl"],
  };
}

function buildPayload(url, attempt) {
  return {
    url,
    engine: attempt.engine,
    proxy: attempt.proxy,
    formats: attempt.formats,
    timeout: attempt.timeout ?? DEFAULT_TIMEOUT,
    retry: true,
    only_main_content: false,
    max_age: 0,
    extract_source: "html",
    ...(attempt.waitFor ? { wait_for: attempt.waitFor } : {}),
    ...(attempt.waitUntil ? { wait_until: attempt.waitUntil } : {}),
    json_options: {
      schema_name: "instagram_public_page",
      schema_description:
        "Normalized public Instagram extraction for profile, reel, and post pages.",
      user_prompt:
        "Extract as much public Instagram data as the page reveals. Identify whether the URL is a profile, reel, or post page. Use null for missing scalar fields, [] for missing lists, and never invent values. Prefer numeric counts when the page makes them derivable.",
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

function detectAccessLimited(response) {
  const markdown = response?.data?.markdown ?? "";
  const title = response?.data?.title ?? "";
  const html = response?.data?.html ?? "";
  const loginHints = [
    "Log into Instagram",
    "Create an account or log in to Instagram",
    "accounts/login",
  ];

  return loginHints.some(
    (hint) => markdown.includes(hint) || html.includes(hint) || title.includes(hint)
  );
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
    {
      engine: "playwright",
      proxy: "stealth",
      formats: FULL_FORMATS,
      timeout: 120000,
      waitFor: 3000,
      waitUntil: "load",
    },
    {
      engine: "playwright",
      proxy: "stealth",
      formats: FULL_FORMATS,
      timeout: 120000,
      waitFor: 7000,
      waitUntil: "networkidle",
    },
    {
      engine: "cheerio",
      proxy: "base",
      formats: LITE_FORMATS,
      timeout: 60000,
    },
  ];

  let best = null;
  let lastError = null;

  for (let index = 0; index < attempts.length; index += 1) {
    const attempt = attempts[index];
    const payload = buildPayload(url, attempt);
    try {
      const response = await scrapeOnce(apiKey, payload);
      const normalized = response.data.json ?? null;
      const score = richnessScore(normalized);
      const accessLimited = detectAccessLimited(response);

      best = {
        attempt: index + 1,
        score,
        accessLimited,
        payload,
        response,
      };

      if ((score >= 8 && !accessLimited) || index === attempts.length - 1) {
        break;
      }
    } catch (error) {
      lastError = error;
    }
  }

  if (!best) {
    throw lastError ?? new Error("Instagram scrape failed without a response.");
  }

  const finalOutput = {
    platform: PLATFORM,
    inputUrl: url,
    finishedAt: new Date().toISOString(),
    request: best.payload,
    normalized: {
      ...(best.response.data.json ?? {}),
      screenshotUrl: best.response.data["screenshot@fullPage"] || null,
      accessLimited: best.accessLimited,
      limitationReason: best.accessLimited
        ? "Instagram returned a login or consent wall instead of full public profile content."
        : null,
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
