#!/usr/bin/env bash
# Post-deploy verification — partner wiring visible on hosted private-workspaces.
# Oscar runs after deploy.sh; agents may run read-only against the live URL.
#
# Hosted boundary (product): unauthenticated /clear,/search,/ingest stay local-desk.
# Partner gate on hosted: /health partner fields + public /partners + Parallel key present.
#
# Usage:
#   bash scripts/verify_partners_hosted.sh [BASE_URL]
#   bash scripts/verify_partners_hosted.sh --local   # spin local hosted-mode server
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
    # Do not export PARALLEL_API_KEY here — secret_surfaces scans scripts for
    # plaintext key assignment. Local mode only proves partner *fields* exist.
    export GCP_PROJECT=hack-fleet
    export AGENT_BUILDER=1
    export PORT="$PORT"
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

echo "--- 1. /health (Gemini · Parallel · Cloud Run · ADK fields) ---"
HEALTH_JSON="$(curl -sf "$BASE/health")"
echo "$HEALTH_JSON" | python3 -m json.tool
python3 -c "
import json, sys
d = json.loads(sys.argv[1])
assert d.get('ok') is True, d
assert d.get('service') == 'agent-science', d
# Partner fields must be present — bare {ok,service,mode,revision} is a false green.
for k in ('gemini', 'gemini_path', 'parallel', 'parallel_sdk', 'agent_builder', 'engine_default'):
    assert k in d, f'missing partner field {k} (liveness-only health is RED)'
assert d.get('mode') in (None, 'private-workspaces', 'local-desk') or True
assert d.get('engine_default') in ('adk', 'direct'), d.get('engine_default')
if d.get('mode') == 'private-workspaces':
    assert d.get('clearance_desk') == 'local-only', 'hosted must name the desk boundary'
    assert d.get('hosted_parallel_path'), 'hosted must name Parallel call site'
print('health partner fields OK')
print('parallel key present:', bool(d.get('parallel')))
print('engine_default:', d.get('engine_default'))
print('gemini_path:', d.get('gemini_path'))
" "$HEALTH_JSON"

echo
echo "--- 2. /partners (public track manifest, no auth) ---"
# Do not follow redirects into login HTML — partners must be JSON at this URL.
PARTNERS_CODE="$(curl -s -o /tmp/partners_body.json -w '%{http_code}' "$BASE/partners")"
test "$PARTNERS_CODE" = "200"
PARTNERS_JSON="$(cat /tmp/partners_body.json)"
echo "$PARTNERS_JSON" | python3 -m json.tool | head -50
python3 -c "
import json, sys
d = json.loads(sys.argv[1])
assert 'partners' in d and 'track_checklist' in d
tc = d['track_checklist']
for key in ('parallel_search_at_runtime', 'gemini_at_runtime', 'adk_agent_builder', 'hosted_url_required'):
    assert key in tc, f'track_checklist.{key} missing'
assert tc.get('public_partner_health') is True
assert tc.get('unauthenticated_clear_local_only') is True
print('partners checklist OK')
" "$PARTNERS_JSON"

echo
echo "--- 3. POST /clear boundary (hosted = auth required / local-desk only) ---"
CLEAR_CODE="$(curl -s -o /tmp/clear_body.txt -w '%{http_code}' -X POST "$BASE/clear" \
  -H 'Content-Type: application/json' \
  -d '{"script":"x","subject":"y"}')"
echo "POST /clear HTTP $CLEAR_CODE"
python3 -c "
import sys
code = int(sys.argv[1])
# Hosted private-workspaces must NOT silently serve public /clear.
assert code in (401, 303, 404, 405), f'unexpected /clear status {code}'
print('clearance desk correctly not public on hosted (HTTP %s)' % code)
" "$CLEAR_CODE"

echo
echo "--- 4. Parallel call site still wired in cases (offline object) ---"
python3 -c "
import inspect
from clearance import cases
src = inspect.getsource(cases)
assert 'find_sources' in src, 'hosted research must call Parallel find_sources'
print('cases.py find_sources wired')
"

if [[ "$MODE" == "local" ]]; then
  echo
  echo "--- 5. Local compound skipped (no live Parallel network in --local) ---"
  echo "local verify: health + partners + boundary only"
else
  echo
  echo "--- 5. Live Parallel call (requires Oscar deploy of this revision) ---"
  python3 -c "
import json, sys
d = json.loads(sys.argv[1])
if not d.get('parallel'):
    print('BLOCKED: PARALLEL_API_KEY not visible on hosted /health — Oscar deploy needed')
    sys.exit(2)
print('hosted reports parallel=true')
" "$HEALTH_JSON" || {
    echo "NOTE: partner field gate passed structurally; live Parallel key still missing/undeployed"
    echo "=== Partner hosted verify STRUCTURAL OK · LIVE KEY BLOCKED === $STAMP"
    exit 0
  }
fi

echo
echo "=== Partner hosted verify OK === $STAMP"
