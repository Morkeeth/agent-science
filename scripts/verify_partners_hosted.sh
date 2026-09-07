#!/usr/bin/env bash
# Post-deploy verification — all four partners visible publicly; clearance behind token.
# Oscar runs after deploy.sh; agents may run read-only against the live URL.
#
# Usage:
#   bash scripts/verify_partners_hosted.sh [BASE_URL]
# Optional for runtime /api/clear proof:
#   AGENT_SCIENCE_WORKSPACE_TOKEN=<invite key> bash scripts/verify_partners_hosted.sh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BASE="${1:-https://agent-science-568004190078.us-central1.run.app}"
STAMP="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
TOKEN="${AGENT_SCIENCE_WORKSPACE_TOKEN:-}"

echo "=== Partner hosted verify === stamp=$STAMP"
echo "URL: $BASE"
echo

echo "--- 1. /health (Gemini · Parallel · Cloud Run · ADK) ---"
HEALTH_JSON="$(curl -sf "$BASE/health")"
echo "$HEALTH_JSON" | python3 -m json.tool
python3 -c "
import json, sys
d = json.loads(sys.argv[1])
assert d.get('ok') is True, d
assert d.get('service') == 'agent-science', d
# Private-workspace revisions must still expose partner wiring — stripped health is RED.
for k in ('gemini', 'parallel', 'parallel_sdk', 'agent_builder', 'engine_default', 'gemini_path'):
    assert k in d, f'missing health field {k}: {d}'
assert d.get('engine_default') in ('adk', 'direct'), d.get('engine_default')
assert d.get('gemini') is True, f'gemini must be wired, got {d.get(\"gemini\")!r} path={d.get(\"gemini_path\")!r}'
assert d.get('parallel') is True, f'parallel key must be present on hosted, got {d.get(\"parallel\")!r}'
assert d.get('parallel_sdk') is True, d
assert d.get('agent_builder') is True, d
assert d.get('engine_default') == 'adk', f'engine_default must be adk, got {d.get(\"engine_default\")!r}'
path = d.get('gemini_path') or ''
assert path.startswith('vertex:'), f'gemini_path must be vertex ADC, got {path!r}'
print('health checks OK')
if d.get('mode'):
    print('mode:', d.get('mode'), 'revision:', d.get('revision'))
" "$HEALTH_JSON"

echo
echo "--- 2. /partners (track manifest) ---"
PARTNERS_JSON="$(curl -sf "$BASE/partners")"
echo "$PARTNERS_JSON" | python3 -m json.tool | head -50
python3 -c "
import json, sys
d = json.loads(sys.argv[1])
tc = d.get('track_checklist') or {}
for key in ('parallel_search_at_runtime', 'gemini_at_runtime', 'adk_agent_builder', 'hosted_url_required'):
    assert tc.get(key) is True, f'track_checklist.{key} not true: {tc}'
assert (d.get('partners') or {}).get('agent_builder_adk', {}).get('engine_default') == 'adk'
print('partners checklist OK')
" "$PARTNERS_JSON"

echo
echo "--- 3. POST /api/clear (ADK + Parallel at runtime, workspace token) ---"
if [[ -z "$TOKEN" ]]; then
  echo "BLOCKED: AGENT_SCIENCE_WORKSPACE_TOKEN unset — cannot prove live /api/clear on private workspaces."
  echo "Public partner surfaces (steps 1–2) passed. Oscar: export the invite key and re-run for runtime clear."
  echo "=== Partner hosted verify PARTIAL (public only) === $STAMP"
  exit 2
fi

TOKEN_HEX="$(python3 -c 'import uuid; print(uuid.uuid4().hex[:12])')"
SUBJECT="partner-verify-$TOKEN_HEX"
REQUEST_ID="partner-clear-${TOKEN_HEX}xxxx"
CLEAR_JSON="$(curl -sf -X POST "$BASE/api/clear" \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $TOKEN" \
  -d "{\"request_id\":\"$REQUEST_ID\",\"script\":\"In ${TOKEN_HEX} the Archive of Zephyr-${TOKEN_HEX} passed Regulation Z-${TOKEN_HEX} for orphan media.\",\"subject\":\"$SUBJECT\"}")"
python3 -c "
import json, sys
d = json.loads(sys.argv[1])
assert d.get('engine') == 'adk', f\"engine must be adk, got {d.get('engine')!r}\"
assert (d.get('claims_extracted') or 0) >= 1, 'expected at least one extracted claim'
parallel = d.get('parallel_calls') or d.get('parallel_api_calls') or 0
assert parallel >= 1, f'Parallel must run on fresh claim, got parallel_calls={parallel}'
print('clear engine:', d.get('engine'))
print('parallel_calls:', parallel)
print('corpus_hits:', d.get('corpus_hits'))
print('claims_extracted:', d.get('claims_extracted'))
" "$CLEAR_JSON"

echo
echo "--- 4. Compound-mini A/B (requires token; uses /api/clear) ---"
python3 "$ROOT/scripts/compound_hosted_probe.py" "$BASE"

echo
echo "--- 5. Compound-fresh A/B ---"
python3 "$ROOT/scripts/compound_fresh_hosted_probe.py" "$BASE"

echo
echo "=== Partner hosted verify OK === $STAMP"
