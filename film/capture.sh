#!/usr/bin/env bash
# Rehearsal — prints beats + opens URLs
set -euo pipefail
FILM_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$FILM_DIR/.." && pwd)"
# shellcheck source=film/numbers.env
source "$FILM_DIR/numbers.env"
cd "$ROOT"
PAUSE="${PAUSE_SEC:-6}"

beat() { printf '\n\033[1;34m▶ %s\033[0m\n' "$1"; sleep "$PAUSE"; }

echo "AGENT SCIENCE — film capture rehearsal"
echo "Visibility: $VISIBILITY_URL"
echo

n=0
while IFS= read -r line; do
  [ -z "$line" ] && continue
  n=$((n + 1))
  beat "Beat $n"
  echo "$line"
done < "$FILM_DIR/voiceover.txt"

echo
echo "Open: $VISIBILITY_URL"
echo "Run: bash scripts/demo_truth_layer.sh"
