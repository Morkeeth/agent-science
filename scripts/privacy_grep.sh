#!/usr/bin/env bash
# Fail if tracked files leak home paths, vault paths, or ~/CODE/<project> strings.
# Run: bash scripts/privacy_grep.sh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

PATTERN='~/CODE/|/Users/[^/[:space:]]|hack-agent-science|vault `|vault/01 Projects'
# Exclude binary assets and frozen corpus text (documentary "vault" is content, not a path leak)
EXCLUDE='\.png$|\.jpg$|cache/documents\.json|fixtures/scripts/|scripts/privacy_grep\.sh|scripts/scrub_privacy_paths\.py'

hits="$(git ls-files | grep -Ev "$EXCLUDE" | xargs rg -n "$PATTERN" 2>/dev/null || true)"
count="$(printf '%s\n' "$hits" | grep -c . || true)"

if [ "$count" -gt 0 ]; then
  echo "PRIVACY FAIL: $count hit(s) in tracked files" >&2
  printf '%s\n' "$hits" | head -40 >&2
  [ "$count" -gt 40 ] && echo "... and $((count - 40)) more" >&2
  exit 1
fi

echo "PRIVACY OK: 0 hits (~/CODE, /Users/*, hack-agent-science, vault paths)"
exit 0
