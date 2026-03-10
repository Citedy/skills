#!/usr/bin/env node

/**
 * Skill Quality Evaluator — standalone, zero-dependency Node.js script.
 * Validates .claude/commands/*.md files for frontmatter, description quality,
 * jargon, directive language, and duplicate detection.
 *
 * Usage:
 *   node run-eval.js [commands-dir]
 *   node run-eval.js                          # scans .claude/commands
 *   node run-eval.js /path/to/commands        # scans custom dir
 *
 * Exit codes: 0 = all pass, 1 = failures found
 */

const fs = require('node:fs');
const path = require('node:path');

// ─── Configuration ──────────────────────────────────────────────────────────

/** Patterns that should NEVER appear in user-facing descriptions */
const JARGON_PATTERNS = [
  { re: /dogfood/i, label: 'dogfood' },
  { re: /--dangerously/i, label: '--dangerously' },
  { re: /hard thinking/i, label: 'hard thinking' },
  { re: /MBA rules/i, label: 'MBA rules' },
  // Add your project-specific jargon here:
  // { re: /internal-term/i, label: 'internal-term' },
];

/** Description MUST match at least one of these — action verbs that improve trigger accuracy */
const DIRECTIVE_PATTERNS = [
  /\buse when\b/i, /\brun\b/i, /\bfix\b/i, /\baudit\b/i,
  /\bgenerate\b/i, /\banalyze\b/i, /\bset up\b/i, /\bapply\b/i,
  /\bcreate\b/i, /\bmanage\b/i, /\bbuild\b/i, /\bsolve\b/i,
  /\blaunch\b/i, /\bchallenge\b/i, /\bdeep/i, /\bimprove\b/i,
  /\bupdate\b/i, /\bfetch\b/i, /\bkill\b/i, /\bscan\b/i,
  /\bextract\b/i, /\bdetect\b/i, /\bdiagnos/i, /\boptimiz/i,
  /\bwrite\b/i, /\bstage\b/i, /\bprepare\b/i, /\bvalidat/i,
  /\breview\b/i, /\bcheck\b/i, /\bensure\b/i, /\bverif/i,
  /\btest\b/i, /\bdeploy\b/i, /\bmonitor\b/i, /\btrack\b/i,
  /\bstart\b/i, /\bstop\b/i, /\bopen\b/i, /\bclose\b/i,
  /\bsearch\b/i, /\bfind\b/i, /\bexplore\b/i, /\bdiscover\b/i,
  /\btransform\b/i, /\bconvert\b/i, /\bmigrate\b/i,
  /\bautomat/i, /\borchestrat/i, /\bschedul/i,
];

/**
 * Pairs of similar commands that MUST have distinct descriptions (first 30 chars normalized).
 * Add your own pairs here — these are examples:
 */
const DIFF_PAIRS = [
  // ['performance-audit.md', 'performance-check.md'],
  // ['debug-error.md', 'debug-investigate.md'],
  // ['code-review.md', 'validate-dev.md'],
];

const MIN_DESCRIPTION_LENGTH = 40;
const MIN_COMMAND_FILES = 1;

// ─── Helpers ────────────────────────────────────────────────────────────────

function parseFrontmatter(content) {
  const match = content.match(/^---\n([\s\S]*?)\n---/);
  if (!match) return null;
  const fields = {};
  for (const line of match[1].split('\n')) {
    const colonIdx = line.indexOf(':');
    if (colonIdx > 0) {
      const key = line.slice(0, colonIdx).trim();
      const value = line.slice(colonIdx + 1).trim().replace(/^["']|["']$/g, '');
      fields[key] = value;
    }
  }
  return fields;
}

function normalizeDesc(desc) {
  return desc.toLowerCase().replace(/[^a-z0-9 ]/g, '').slice(0, 30);
}

// ─── Colors (ANSI) ─────────────────────────────────────────────────────────

const C = {
  reset: '\x1b[0m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  cyan: '\x1b[36m',
  dim: '\x1b[2m',
  bold: '\x1b[1m',
};

// ─── Main ───────────────────────────────────────────────────────────────────

function main() {
  const commandsDir = path.resolve(process.argv[2] || '.claude/commands');

  if (!fs.existsSync(commandsDir)) {
    console.error(`${C.red}Directory not found: ${commandsDir}${C.reset}`);
    process.exit(1);
  }

  const files = fs.readdirSync(commandsDir)
    .filter(f => f.endsWith('.md'))
    .map(f => path.join(commandsDir, f));

  console.log(`\n${C.bold}Skill Quality Eval${C.reset} ${C.dim}(${files.length} command files in ${commandsDir})${C.reset}\n`);

  if (files.length < MIN_COMMAND_FILES) {
    console.log(`${C.yellow}WARNING: Only ${files.length} command files found (expected >= ${MIN_COMMAND_FILES})${C.reset}\n`);
  }

  let totalPass = 0;
  let totalFail = 0;
  const failures = [];
  const descriptions = new Map(); // basename -> normalized desc

  for (const file of files) {
    const basename = path.basename(file);
    const content = fs.readFileSync(file, 'utf-8');
    const fileIssues = [];

    // 1. Frontmatter exists
    if (!content.startsWith('---\n') || content.indexOf('\n---', 4) <= 4) {
      fileIssues.push('Missing YAML frontmatter (must start with --- block)');
    }

    const fm = parseFrontmatter(content);

    // 2. Description exists
    if (!fm || !fm.description) {
      fileIssues.push('Missing "description:" field in frontmatter');
    } else {
      // 3. Description length
      if (fm.description.length < MIN_DESCRIPTION_LENGTH) {
        fileIssues.push(`Description too short: ${fm.description.length} chars (min ${MIN_DESCRIPTION_LENGTH})`);
      }

      // 4. Jargon check
      for (const { re, label } of JARGON_PATTERNS) {
        if (re.test(fm.description)) {
          fileIssues.push(`Jargon detected: "${label}" — replace with user-facing language`);
        }
      }

      // 5. Directive language
      const hasDirective = DIRECTIVE_PATTERNS.some(p => p.test(fm.description));
      if (!hasDirective) {
        fileIssues.push('No directive verb found — add action verbs (Run, Fix, Scan, Use when...)');
      }

      // Store for dedup
      descriptions.set(basename, normalizeDesc(fm.description));
    }

    if (fileIssues.length === 0) {
      totalPass++;
      console.log(`  ${C.green}PASS${C.reset} ${basename}`);
    } else {
      totalFail++;
      console.log(`  ${C.red}FAIL${C.reset} ${basename}`);
      for (const issue of fileIssues) {
        console.log(`       ${C.dim}- ${issue}${C.reset}`);
        failures.push({ file: basename, issue });
      }
    }
  }

  // 6. Differentiation check
  if (DIFF_PAIRS.length > 0) {
    console.log(`\n${C.bold}Differentiation checks:${C.reset}`);
    let diffPass = 0;
    let diffFail = 0;

    for (const [a, b] of DIFF_PAIRS) {
      const descA = descriptions.get(a);
      const descB = descriptions.get(b);

      if (!descA || !descB) {
        console.log(`  ${C.dim}SKIP${C.reset} ${a} vs ${b} ${C.dim}(one or both not found)${C.reset}`);
        continue;
      }

      if (descA === descB) {
        diffFail++;
        console.log(`  ${C.red}FAIL${C.reset} ${a} vs ${b} — identical first 30 chars: "${descA}"`);
        failures.push({ file: `${a} vs ${b}`, issue: 'Duplicate descriptions (first 30 chars match)' });
      } else {
        diffPass++;
        console.log(`  ${C.green}PASS${C.reset} ${a} vs ${b}`);
      }
    }

    totalPass += diffPass;
    totalFail += diffFail;
  }

  // Summary
  console.log(`\n${C.bold}Results:${C.reset} ${C.green}${totalPass} passed${C.reset}, ${totalFail > 0 ? C.red : C.dim}${totalFail} failed${C.reset} (${files.length} files)\n`);

  if (totalFail > 0) {
    console.log(`${C.yellow}Fix suggestions:${C.reset}`);
    const uniqueIssues = [...new Set(failures.map(f => f.issue))];
    for (const issue of uniqueIssues) {
      const affected = failures.filter(f => f.issue === issue).map(f => f.file);
      console.log(`  ${C.cyan}${issue}${C.reset}`);
      for (const f of affected) {
        console.log(`    - ${f}`);
      }
    }
    console.log('');
    process.exit(1);
  }

  process.exit(0);
}

main();
