#!/usr/bin/env bash
# Clearance desk demo for documentary producers — no local API keys.
# Calls hosted POST /clear with a public cold script (default: Google Books settlement).
# Usage: bash scripts/demo_clearance_desk.sh [script-file] [subject]
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
BASE="${HOSTED_URL:-https://agent-science-568004190078.us-central1.run.app}"
SCRIPT_FILE="${1:-docs/cold-scripts/google-books-settlement.txt}"
SUBJECT="${2:-cold-demo-$(date +%Y%m%d)}"

if [ ! -f "$SCRIPT_FILE" ]; then
  echo "missing script: $SCRIPT_FILE" >&2
  exit 1
fi

echo "=== Agent Science · clearance desk (hosted) ==="
echo "script:  $SCRIPT_FILE"
echo "subject: $SUBJECT"
echo "url:     $BASE/clear"
echo

START=$(date +%s)
RESP="$(python3 - "$SCRIPT_FILE" "$SUBJECT" "$BASE" <<'PY'
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

script_file, subject, base = sys.argv[1:4]
script = Path(script_file).read_text(encoding="utf-8")
payload = json.dumps({"script": script, "subject": subject}).encode()
req = urllib.request.Request(
    f"{base.rstrip('/')}/clear",
    data=payload,
    headers={"Content-Type": "application/json"},
    method="POST",
)
with urllib.request.urlopen(req, timeout=300) as resp:
    print(resp.read().decode())
PY
)"
END=$(date +%s)

printf '%s\n' "$RESP" | python3 -c "
import json, sys
d = json.load(sys.stdin)
print(f\"claims: {d.get('claims_extracted')} | sourced: {d.get('sourced')} | unsourced: {d.get('unsourced')}\")
print(f\"parallel_api_calls: {d.get('parallel_api_calls')} | engine: {d.get('engine')}\")
print()
for r in d.get('rows', []):
    print(f\"{r['claim_id']} · {r['label']} · {r.get('cause') or ''}\")
    print(f\"  {r['text']}\")
    if r.get('citation_url'):
        print(f\"  → {r['citation_url']}\")
    if r.get('quoted_terms'):
        print(f\"  {r['quoted_terms'][:160]}\")
    print(f\"  why: {r.get('why', '')}\")
    print()
"

echo "wall-clock: $((END - START))s"
echo "desk UI:    ${BASE}/"
echo "=== done ==="
