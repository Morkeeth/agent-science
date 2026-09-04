#!/usr/bin/env bash
# Inspect the local evidence honestly. Live discovery is an explicit CLI action.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
QUERY="${1:-Do fresh agent sessions reduce repeated errors in long coding tasks?}"
python3 -m clearance visibility "$QUERY" --full --no-personal --root .
python3 -m clearance stack-fit "$QUERY" --root .
echo 'Create a saved evidence case with: python3 -m clearance case create "your question" --root . --live'
