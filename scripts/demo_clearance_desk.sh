#!/usr/bin/env bash
# Clearance desk demo for documentary producers — no local API keys.
# Calls hosted POST /clear with a public cold script (default: Google Books settlement).
# Usage: bash scripts/demo_clearance_desk.sh [script-file] [subject]
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
BASE="${HOSTED_URL:-https://agent-science-568004190078.us-central1.run.app}"
SCRIPT_FILE="${1:-docs/cold-scripts/buyer-sourced-and-caught.txt}"
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

# Hosted may be private-workspaces (login required). Probe before burning a long POST.
HEALTH="$(curl -sS --max-time 20 "$BASE/health" || true)"
MODE="$(python3 -c "import json,sys; d=json.loads(sys.argv[1] or '{}'); print(d.get('mode') or '')" "$HEALTH" 2>/dev/null || true)"
if [ "$MODE" = "private-workspaces" ]; then
  echo "BLOCKED: hosted revision is mode=private-workspaces — unauthenticated /clear is not a stranger path."
  echo "health: $HEALTH"
  echo "Oscar door: restore a public judge surface, OR film from local:"
  echo "  python3 scripts/compound_exhibit_receipt.py"
  echo "  bash scripts/demo_truth_layer.sh"
  echo "  open docs/film/  # screenshots from last public desk"
  exit 2
fi

START=$(date +%s)
set +e
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
try:
    with urllib.request.urlopen(req, timeout=300) as resp:
        print(resp.read().decode())
except urllib.error.HTTPError as e:
    body = e.read().decode("utf-8", "replace")
    print(json.dumps({
        "error": f"HTTP {e.code}",
        "body": body[:500],
        "location": e.headers.get("Location"),
    }))
    sys.exit(1)
PY
)"
EC=$?
set -e
END=$(date +%s)

if [ "$EC" -ne 0 ]; then
  echo "BLOCKED: hosted POST /clear failed (exit $EC)."
  printf '%s\n' "$RESP"
  echo "Local stranger path still works: bash scripts/verify_cold_clone.sh"
  exit 2
fi

printf '%s\n' "$RESP" | python3 -c "
import json, sys
d = json.load(sys.stdin)
if d.get('error'):
    print('BLOCKED:', d.get('error'), d.get('location') or '')
    print(d.get('body') or '')
    raise SystemExit(2)
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
