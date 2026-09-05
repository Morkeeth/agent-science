#!/usr/bin/env bash
# Prove partner dual surface without Cloud Run deploy.
# Starts a local hosted-mode server, checks public partners + private /api/cases.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
PORT="${PORT:-8765}"
TMP="$(mktemp -d)"
trap 'kill "$PID" 2>/dev/null || true; rm -rf "$TMP"' EXIT

export AGENT_SCIENCE_HOSTED=1
export AGENT_SCIENCE_ALLOW_HTTP=1
export AGENT_SCIENCE_PUBLIC_ORIGIN="http://127.0.0.1:${PORT}"
export AGENT_SCIENCE_WORKSPACE_DIR="$TMP/ws"
export AGENT_SCIENCE_ACCESS_CONFIG="$(python3 - <<'PY'
import hashlib, json
token = "a" * 48
print(json.dumps({
    "session_key": "s" * 48,
    "users": {"demo": hashlib.sha256(token.encode()).hexdigest()},
}))
PY
)"
export AGENT_BUILDER=1
export GCP_PROJECT=hack-fleet
export PARALLEL_API_KEY=pk-demo-not-live
export PORT
export PYTHONPATH="$ROOT"
mkdir -p "$AGENT_SCIENCE_WORKSPACE_DIR"

python3 cloud/service.py >"$TMP/server.log" 2>&1 &
PID=$!
for i in $(seq 1 40); do
  if curl -sf "http://127.0.0.1:${PORT}/health" >/dev/null 2>&1; then
    break
  fi
  sleep 0.1
done

echo "=== dual-surface local prove ==="
HEALTH="$(curl -sf "http://127.0.0.1:${PORT}/health")"
echo "$HEALTH" | python3 -m json.tool
python3 -c "
import json, sys
d = json.loads(sys.argv[1])
assert d.get('mode') == 'private-workspaces+public-desk', d
assert d.get('public_desk') is True, d
assert d.get('engine_default') in ('adk', 'direct'), d
assert 'gemini_path' in d and 'parallel' in d, d
print('health OK')
" "$HEALTH"

PARTNERS="$(curl -sf "http://127.0.0.1:${PORT}/partners")"
python3 -c "
import json, sys
d = json.loads(sys.argv[1])
assert 'partners' in d and 'track_checklist' in d, d
print('partners OK')
" "$PARTNERS"

CODE="$(curl -s -o /dev/null -w '%{http_code}' -X POST "http://127.0.0.1:${PORT}/clear" \
  -H 'Content-Type: application/json' \
  -d '{"script":"Directive 2012/28/EU.","subject":"dual-demo"}')"
# 200 with mock keys may 503 without Vertex; anything other than 401 means desk reached.
test "$CODE" != "401"
echo "POST /clear HTTP $CODE (not workspace-auth 401)"

API="$(curl -s -o /dev/null -w '%{http_code}' "http://127.0.0.1:${PORT}/api/cases")"
test "$API" = "401"
echo "GET /api/cases HTTP $API (workspace still private)"

echo "=== dual-surface local prove OK ==="
