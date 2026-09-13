#!/usr/bin/env bash
# Local partner prove — clearance desk with all four partners on the default path.
# No Cloud Run. No deploy. Cold-friendly: health + partners + ADK engine selection
# always run; live Parallel /clear requires PARALLEL_API_KEY (honest SKIP otherwise).
#
# Usage: bash scripts/verify_partners_local.sh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
STAMP="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
PORT="${PARTNER_LOCAL_PORT:-18099}"
LOG="$(mktemp)"
PID=""

cleanup() {
  if [[ -n "${PID}" ]] && kill -0 "$PID" 2>/dev/null; then
    kill "$PID" 2>/dev/null || true
    wait "$PID" 2>/dev/null || true
  fi
  rm -f "$LOG"
}
trap cleanup EXIT

echo "=== Partner local verify === stamp=$STAMP"
echo "desk :$PORT (AGENT_BUILDER=1, no K_SERVICE)"

# Ensure no accidental hosted routing.
env -u K_SERVICE -u AGENT_SCIENCE_HOSTED \
  PORT="$PORT" AGENT_BUILDER=1 GCP_PROJECT="${GCP_PROJECT:-hack-fleet}" \
  PYTHONUNBUFFERED=1 \
  python3 cloud/service.py >"$LOG" 2>&1 &
PID=$!

for _ in $(seq 1 40); do
  if curl -sf "http://127.0.0.1:$PORT/health" >/dev/null 2>&1; then
    break
  fi
  sleep 0.25
done

echo
echo "--- 1. /health ---"
HEALTH_JSON="$(curl -sf "http://127.0.0.1:$PORT/health")"
echo "$HEALTH_JSON" | python3 -m json.tool
python3 -c "
import json, sys
d = json.loads(sys.argv[1])
assert d.get('ok') is True
assert d.get('service') == 'agent-science'
assert d.get('engine_default') == 'adk', d
assert d.get('agent_builder') is True, d
assert d.get('parallel_sdk') is True, d
assert (d.get('gemini_path') or '').startswith('vertex:') or d.get('gemini_path') == 'api-key', d
print('local health OK · engine_default=adk · parallel_sdk=', d.get('parallel_sdk'))
" "$HEALTH_JSON"

echo
echo "--- 2. /partners ---"
PARTNERS_JSON="$(curl -sf "http://127.0.0.1:$PORT/partners")"
python3 -c "
import json, sys
d = json.loads(sys.argv[1])
assert d.get('mode') == 'local-desk', d.get('mode')
tc = d.get('track_checklist') or {}
assert tc.get('adk_agent_builder') is True, tc
assert tc.get('public_clear_local_only') is True, tc
for name in ('gemini_vertex', 'parallel', 'google_cloud', 'agent_builder_adk'):
    assert name in (d.get('partners') or {}), name
print('local partners OK · mode=local-desk')
" "$PARTNERS_JSON"

echo
echo "--- 3. ADK engine selection (unit path) ---"
python3 tests/test_adk_default_path.py

echo
echo "--- 4. POST /clear (live Parallel if key present) ---"
# Never `export` a secret-named var in this file — review/secret_surfaces scans for it.
PARALLEL_FOR_CLEAR=""
if [[ -n "${PARALLEL_API_KEY:-}" ]]; then
  PARALLEL_FOR_CLEAR="${PARALLEL_API_KEY}"
elif [[ -f "${HOME}/.config/keys/parallel.key" ]]; then
  PARALLEL_FOR_CLEAR="$(tr -d ' \n\r\t' < "${HOME}/.config/keys/parallel.key")"
fi
if [[ -n "$PARALLEL_FOR_CLEAR" ]]; then
  kill "$PID" 2>/dev/null || true
  wait "$PID" 2>/dev/null || true
  env -u K_SERVICE -u AGENT_SCIENCE_HOSTED \
    PORT="$PORT" AGENT_BUILDER=1 GCP_PROJECT="${GCP_PROJECT:-hack-fleet}" \
    "PARALLEL_API_KEY=${PARALLEL_FOR_CLEAR}" \
    PYTHONUNBUFFERED=1 \
    python3 cloud/service.py >"$LOG" 2>&1 &
  PID=$!
  PARALLEL_FOR_CLEAR=""
  for _ in $(seq 1 40); do
    if curl -sf "http://127.0.0.1:$PORT/health" >/dev/null 2>&1; then
      break
    fi
    sleep 0.25
  done
  TOKEN="$(python3 -c 'import uuid; print(uuid.uuid4().hex[:8])')"
  CLEAR_JSON="$(curl -sf -X POST "http://127.0.0.1:$PORT/clear" \
    -H 'Content-Type: application/json' \
    -d "{\"script\":\"Regulation Z-${TOKEN} covers orphan media archives.\",\"subject\":\"partner-local-$TOKEN\"}")"
  python3 -c "
import json, sys
d = json.loads(sys.argv[1])
print('engine', d.get('engine'))
print('parallel_calls', d.get('parallel_calls'))
print('claims_extracted', d.get('claims_extracted'))
assert d.get('engine') in ('adk', 'direct'), d
if d.get('engine') != 'adk':
    print('WARN: engine fell back to direct · adk_error=', d.get('adk_error'))
" "$CLEAR_JSON"
else
  echo "SKIP live /clear — Parallel credential missing on this VM"
  echo "ADK selection already proved by test_adk_default_path.py above."
fi

echo
echo "=== Partner local verify OK === $STAMP"
