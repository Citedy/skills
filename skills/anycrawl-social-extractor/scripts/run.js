#!/usr/bin/env node

const { execFileSync } = require("child_process");
const path = require("path");

// Resolve sibling skill paths relative to this script's location
const SKILLS_DIR = path.resolve(__dirname, "../..");

const ROUTES = {
  tiktok: {
    match(url) {
      return url.hostname.includes("tiktok.com");
    },
    skill: "anycrawl-tiktok-scraper",
    script: path.join(SKILLS_DIR, "anycrawl-tiktok-scraper/scripts/run.js"),
  },
  instagram: {
    match(url) {
      return url.hostname.includes("instagram.com");
    },
    skill: "anycrawl-instagram-scraper",
    script: path.join(SKILLS_DIR, "anycrawl-instagram-scraper/scripts/run.js"),
  },
  youtube: {
    match(url) {
      return (
        (url.hostname.includes("youtube.com") && url.pathname === "/watch") ||
        url.hostname === "youtu.be"
      );
    },
    skill: "anycrawl-youtube-video-extractor",
    script: path.join(SKILLS_DIR, "anycrawl-youtube-video-extractor/scripts/run.js"),
  },
};

function usage() {
  throw new Error("Usage: node run.js <social-url> [output-path]");
}

function pickRoute(input) {
  if (!input) {
    usage();
  }

  const url = new URL(input);

  for (const [platform, config] of Object.entries(ROUTES)) {
    if (config.match(url)) {
      return { platform, url: url.toString(), ...config };
    }
  }

  throw new Error(
    "Unsupported URL. Use a public TikTok, Instagram, or YouTube link."
  );
}

function runDelegatedScript(route, outputPath) {
  const args = [route.script, route.url];
  if (outputPath) {
    args.push(path.resolve(outputPath));
  }

  const stdout = execFileSync("node", args, {
    encoding: "utf8",
    stdio: ["ignore", "pipe", "pipe"],
  });

  return JSON.parse(stdout);
}

function main() {
  const route = pickRoute(process.argv[2]);
  const delegated = runDelegatedScript(route, process.argv[3]);

  const summary = {
    ok: true,
    platform: route.platform,
    routedSkill: route.skill,
    runnerScript: route.script,
    ...delegated,
  };

  process.stdout.write(`${JSON.stringify(summary, null, 2)}\n`);
}

main();
