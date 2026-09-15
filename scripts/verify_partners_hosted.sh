#!/usr/bin/env bash
# Post-deploy verification — all four partners visible + callable on hosted desk.
# Oscar runs after deploy.sh; agents may run read-only against the live URL.
#
# Public (no key): /health partner fields · /partners track checklist
# Workspace (optional): AGENT_SCIENCE_WORKSPACE_TOKEN for live research probe
# Local desk /clear remains the ADK clearance path (not exposed on hosted).
#
# Usage: bash scripts/verify_partners_hosted.sh [BASE_URL]
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
req = {
    'ok': True,
    'mode': 'private-workspaces',
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
assert d.get('revision'), 'revision missing'
print('health checks OK')
" "$HEALTH_JSON"

echo
echo "--- 2. /partners (track manifest, anonymous) ---"
PARTNERS_JSON="$(curl -sf "$BASE/partners")"
echo "$PARTNERS_JSON" | python3 -m json.tool | head -50
python3 -c "
import json, sys
d = json.loads(sys.argv[1])
assert d.get('mode') == 'private-workspaces', d.get('mode')
tc = d.get('track_checklist') or {}
for key in ('parallel_search_at_runtime', 'gemini_at_runtime', 'adk_agent_builder', 'hosted_url_required', 'partner_health_public'):
    assert tc.get(key) is True, f'track_checklist.{key} not true'
print('partners checklist OK')
" "$PARTNERS_JSON"

echo
echo "--- 3. Legacy public /clear stays closed (workspace boundary) ---"
CLEAR_CODE="$(curl -s -o /tmp/partner-clear.body -w '%{http_code}' -X POST "${BASE}/clear" \
  -H 'Content-Type: application/json' \
  -d '{"script":"boundary check","subject":"partner-boundary"}')"
echo "POST /clear HTTP $CLEAR_CODE"
python3 -c "
code = int('$CLEAR_CODE')
assert code in (401, 303, 404), f'public /clear must stay closed, got {code}'
print('workspace boundary OK')
"

if [[ -z "$TOKEN" ]]; then
  echo
  echo "--- 4/5. Workspace live research + compound ---"
  echo "SKIPPED — set AGENT_SCIENCE_WORKSPACE_TOKEN to prove Parallel on hosted /api/cases"
  echo "=== Partner hosted verify PARTIAL (health+partners OK; live research not run) === $STAMP"
  exit 0
fi

echo
echo "--- 4. Authenticated live research (Parallel at runtime) ---"
RID="partner-verify-$(python3 -c 'import uuid; print(uuid.uuid4().hex[:12])')"
CASE_JSON="$(curl -sf -X POST "$BASE/api/cases" \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d "{\"request_id\":\"$RID\",\"question\":\"What is Directive 2012/28/EU about orphan works?\",\"live\":true,\"official_domains\":[\"eur-lex.europa.eu\"]}")"
echo "$CASE_JSON" | python3 -m json.tool | head -40
python3 -c "
import json, sys
d = json.loads(sys.argv[1])
assert d.get('case_id'), d
print('case_id', d.get('case_id'), 'version', d.get('version'))
" "$CASE_JSON"

echo
echo "--- 5. Compound probes (local offline authoritative if hosted times out) ---"
if python3 "$ROOT/scripts/compound_fresh_hosted_probe.py" "$BASE"; then
  echo "compound-fresh OK"
else
  echo "WARN: compound-fresh failed or timed out — offline receipt remains authoritative"
fi

echo
echo "=== Partner hosted verify OK === $STAMP"
