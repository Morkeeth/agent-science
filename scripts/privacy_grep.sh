#!/usr/bin/env bash
# Fail if tracked files leak home paths, vault paths, or ~/CODE/<project> strings.
# Run: bash scripts/privacy_grep.sh
#
# 2026-09-02: rewritten on `git grep`. The previous version piped `git ls-files | xargs rg`
# with stderr silenced and `|| true` — on a machine where `rg` is a shell function (not a
# binary xargs can exec) it printed PRIVACY OK on zero files scanned. A check that cannot
# fail is not a check; this one exits 2 if the scan itself produces no candidate list.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

# Bracketed last letters keep this file itself from matching a literal grep for the strings.
PATTERN='~/CODE/|/Users/[A-Za-z0-9._-]+/|hack-agent-scienc[e]|vault `|vault/01 Projects|Obsidian LIF[E]|\.claude/project[s]'
# Exclude binary assets and frozen corpus text (documentary "vault" is content, not a path leak)
EXCLUDE='\.png$|\.jpg$|cache/documents\.json|fixtures/scripts/|scripts/privacy_grep\.sh|scripts/scrub_privacy_paths\.py'

scanned="$(git ls-files | grep -Ev "$EXCLUDE" | wc -l | tr -d ' ')"
if [ "$scanned" -eq 0 ]; then
  echo "PRIVACY ERROR: scanned 0 tracked files — the control did not run" >&2
  exit 2
fi

hits="$(git grep -nE "$PATTERN" -- . | grep -Ev "^($EXCLUDE)" | grep -Ev "^[^:]*($EXCLUDE)" || true)"
count="$(printf '%s\n' "$hits" | grep -c . || true)"

if [ "$count" -gt 0 ]; then
  echo "PRIVACY FAIL: $count hit(s) in tracked files (scanned $scanned)" >&2
  printf '%s\n' "$hits" | head -40 >&2
  [ "$count" -gt 40 ] && echo "... and $((count - 40)) more" >&2
  exit 1
fi

echo "PRIVACY OK: 0 hits in $scanned tracked files (home paths, ~/CODE, vault paths)"
exit 0
