#!/usr/bin/env bash
set -euo pipefail

SKILL_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEST_ROOT="${1:-}"

if [[ -z "$DEST_ROOT" ]]; then
  echo "Usage: bash scripts/export-standalone.sh /absolute/path/to/codex-symphony-repo" >&2
  exit 1
fi

mkdir -p "$DEST_ROOT"

cp "$SKILL_ROOT/README.md" "$DEST_ROOT/README.md"
cp "$SKILL_ROOT/SKILL.md" "$DEST_ROOT/SKILL.md"
mkdir -p "$DEST_ROOT/agents" "$DEST_ROOT/assets" "$DEST_ROOT/scripts"
cp "$SKILL_ROOT/agents/openai.yaml" "$DEST_ROOT/agents/openai.yaml"
cp "$SKILL_ROOT/assets/"* "$DEST_ROOT/assets/"
cp "$SKILL_ROOT/scripts/install.sh" "$DEST_ROOT/scripts/install.sh"
cp "$SKILL_ROOT/scripts/self-test.sh" "$DEST_ROOT/scripts/self-test.sh"

chmod +x "$DEST_ROOT/scripts/install.sh" "$DEST_ROOT/scripts/self-test.sh"

echo "Exported standalone repo scaffold to: $DEST_ROOT"
