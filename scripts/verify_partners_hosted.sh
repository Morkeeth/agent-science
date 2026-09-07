#!/usr/bin/env bash
# Post-deploy verification — all four partners on hosted dual surface.
# Oscar runs after deploy.sh; agents may run read-only against the live URL.
#
# Usage:
#   bash scripts/verify_partners_hosted.sh [BASE_URL]
#   bash scripts/verify_partners_hosted.sh --local   # dual-surface fields without keys
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
STAMP="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
MODE="remote"
BASE="${1:-https://agent-science-568004190078.us-central1.run.app}"
LOCAL_PID=""

cleanup() {
  if [[ -n "$LOCAL_PID" ]]; then
    kill "$LOCAL_PID" 2>/dev/null || true
    wait "$LOCAL_PID" 2>/dev/null || true
  fi
}
trap cleanup EXIT

if [[ "${1:-}" == "--local" ]]; then
  MODE="local"
  TMP="$(mktemp -d)"
  TOKEN="$(python3 -c 'import secrets; print(secrets.token_hex(24))')"
  HASH="$(python3 -c "import hashlib,sys; print(hashlib.sha256(sys.argv[1].encode()).hexdigest())" "$TOKEN")"
  ACCESS="$(python3 -c "import json,sys; print(json.dumps({'session_key':'s'*48,'users':{'judge':sys.argv[1]}}))" "$HASH")"
  PORT="$(python3 -c 'import socket; s=socket.socket(); s.bind(("127.0.0.1",0)); print(s.getsockname()[1]); s.close()')"
  BASE="http://127.0.0.1:${PORT}"
  (
    cd "$ROOT"
    export AGENT_SCIENCE_HOSTED=1
    export AGENT_SCIENCE_ALLOW_HTTP=1
    export AGENT_SCIENCE_PUBLIC_ORIGIN="$BASE"
    export AGENT_SCIENCE_WORKSPACE_DIR="$TMP"
    export AGENT_SCIENCE_ACCESS_CONFIG="$ACCESS"
    # Do not export PARALLEL_API_KEY — secret_surfaces scans scripts for plaintext assignment.
    export GCP_PROJECT=hack-fleet
    export AGENT_BUILDER=1
    export PORT="$PORT"
    export PYTHONPATH="$ROOT"
    python3 cloud/service.py
  ) >/tmp/partner-verify-local.log 2>&1 &
  LOCAL_PID=$!
  for _ in $(seq 1 40); do
    if curl -sf "$BASE/health" >/dev/null 2>&1; then
      break
    fi
    sleep 0.1
  done
fi

echo "=== Partner hosted verify === stamp=$STAMP mode=$MODE"
echo "URL: $BASE"
echo

echo "--- 1. /health (Gemini · Parallel · Cloud Run · ADK) ---"
HEALTH_JSON="$(curl -sf "$BASE/health")"
echo "$HEALTH_JSON" | python3 -m json.tool
python3 -c "
import json, sys
d = json.loads(sys.argv[1])
mode = sys.argv[2]
assert d.get('ok') is True, d
assert d.get('service') == 'agent-science', d
for k in ('gemini', 'gemini_path', 'parallel', 'parallel_sdk', 'agent_builder', 'engine_default'):
    assert k in d, f'missing partner field {k} (liveness-only health is RED)'
assert d.get('engine_default') in ('adk', 'direct'), d.get('engine_default')
assert d.get('mode') == 'private-workspaces+public-desk', d.get('mode')
assert d.get('public_desk') is True, d
if mode == 'remote':
    # After Oscar deploy these must be true; until then this script fails on live 00026.
    req = {
        'gemini': True,
        'parallel': True,
        'parallel_sdk': True,
        'agent_builder': True,
        'engine_default': 'adk',
    }
    for k, v in req.items():
        got = d.get(k)
        assert got == v, f'{k}: expected {v!r}, got {got!r}'
    path = d.get('gemini_path') or ''
    assert path.startswith('vertex:'), f'gemini_path must be vertex ADC, got {path!r}'
print('health checks OK')
" "$HEALTH_JSON" "$MODE"

echo
echo "--- 2. /partners (track manifest) ---"
PARTNERS_CODE="$(curl -s -o /tmp/partners_body.json -w '%{http_code}' "$BASE/partners")"
test "$PARTNERS_CODE" = "200"
PARTNERS_JSON="$(cat /tmp/partners_body.json)"
echo "$PARTNERS_JSON" | python3 -m json.tool | head -40
python3 -c "
import json, sys
d = json.loads(sys.argv[1])
tc = d.get('track_checklist') or {}
for key in ('parallel_search_at_runtime', 'gemini_at_runtime', 'adk_agent_builder', 'hosted_url_required'):
    assert key in tc, f'track_checklist.{key} missing'
print('partners checklist OK')
" "$PARTNERS_JSON"

if [[ "$MODE" == "local" ]]; then
  echo
  echo "--- 3. Local mode: desk public, cases private (no live Parallel) ---"
  CLEAR_CODE="$(curl -s -o /dev/null -w '%{http_code}' -X POST "$BASE/clear" \
    -H 'Content-Type: application/json' \
    -d '{"script":"Directive 2012/28/EU.","subject":"partner-local"}')"
  test "$CLEAR_CODE" != "401"
  CASES_CODE="$(curl -s -o /dev/null -w '%{http_code}' "$BASE/api/cases")"
  test "$CASES_CODE" = "401"
  echo "POST /clear HTTP $CLEAR_CODE (not 401)"
  echo "GET /api/cases HTTP $CASES_CODE"
  echo
  echo "=== Partner hosted verify OK (local dual-surface fields) === $STAMP"
  exit 0
fi

echo
echo "--- 3. POST /clear (ADK + Parallel at runtime) ---"
TOKEN="$(python3 -c 'import uuid; print(uuid.uuid4().hex[:12])')"
SUBJECT="partner-verify-$TOKEN"
CLEAR_JSON="$(curl -sf -X POST "$BASE/clear" \
  -H 'Content-Type: application/json' \
  -d "{\"script\":\"In ${TOKEN} the Archive of Zephyr-${TOKEN} passed Regulation Z-${TOKEN} for orphan media.\",\"subject\":\"$SUBJECT\"}")"
python3 -c "
import json, sys
d = json.loads(sys.argv[1])
assert d.get('engine') == 'adk', f\"engine must be adk, got {d.get('engine')!r}\"
assert (d.get('claims_extracted') or 0) >= 1, 'expected at least one extracted claim'
parallel = d.get('parallel_calls') or 0
assert parallel >= 1, f'Parallel must run on fresh claim, got parallel_calls={parallel}'
print('clear engine:', d.get('engine'))
print('parallel_calls:', parallel)
print('corpus_hits:', d.get('corpus_hits'))
print('claims_extracted:', d.get('claims_extracted'))
" "$CLEAR_JSON"

echo
echo "--- 4. Compound-mini A/B (warm shelf — corpus_hits) ---"
python3 "$ROOT/scripts/compound_hosted_probe.py" "$BASE"

echo
echo "--- 5. Compound-fresh A/B (Parallel drop on fresh subject) ---"
python3 "$ROOT/scripts/compound_fresh_hosted_probe.py" "$BASE"

echo
echo "=== Partner hosted verify OK === $STAMP"
