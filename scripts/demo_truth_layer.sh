#!/usr/bin/env bash
# One-command truth layer demo — film scout or judge cold path.
# Usage: bash scripts/demo_truth_layer.sh [visibility-query] [lookup-query]
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
Q1="${1:-ralph loop agentic}"
Q2="${2:-ralph loop agentic practice}"
BASE="${HOSTED_URL:-https://agent-science-568004190078.us-central1.run.app}"

echo "=== Agent Science · truth layer demo ==="
echo
echo "--- 1 · Full visibility (CLI) ---"
python3 -m clearance.stack_cli visibility "$Q1" --full --no-personal | head -45
echo
echo "--- 2 · Lookup / contrary stamp ---"
python3 -m clearance.stack_cli lookup "$Q2"
echo
echo "--- 3 · Stack-fit ---"
python3 -m clearance.stack_cli stack-fit "science_lookup MCP fleet" || true
echo
echo "--- 4 · Hosted surfaces ---"
echo "  visibility UI: ${BASE}/visibility/ui?q=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$Q1'))")"
echo "  truths dash:   ${BASE}/truths/ui"
echo "  registry:      ${BASE}/registry"
echo
if curl -sf "${BASE}/health" >/dev/null 2>&1; then
  echo "--- 5 · Hosted visibility JSON (first keys) ---"
  curl -sf "${BASE}/visibility?q=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$Q1'))")" | python3 -c "import sys,json; d=json.load(sys.stdin); print('primary:', (d.get('primary') or {}).get('label')); print('transparency:', list((d.get('transparency') or {}).keys())[:5])" 2>/dev/null || echo "(deploy pending for /visibility)"
fi
echo
echo "=== done ==="
