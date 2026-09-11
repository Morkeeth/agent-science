#!/usr/bin/env bash
# Post-deploy partner verification against the hosted URL.
# Oscar runs after deploy.sh; agents may run read-only against the live URL.
#
# Hosted private-workspaces boundary (AGENTS.md):
#   PUBLIC:  GET /health · GET /partners
#   LOCAL:   POST /clear · GET/POST /search · ingest · shared history
#
# Usage:
#   bash scripts/verify_partners_hosted.sh [BASE_URL]
#   VERIFY_LOCAL_CLEAR=1 bash scripts/verify_partners_hosted.sh   # also run local /clear proof
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BASE="${1:-https://agent-science-568004190078.us-central1.run.app}"
STAMP="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
FAIL=0

echo "=== Partner hosted verify === stamp=$STAMP"
echo "URL: $BASE"
echo

echo "--- 1. /health (Gemini · Parallel · Cloud Run · ADK) ---"
HEALTH_JSON="$(curl -sf "$BASE/health")" || {
  echo "FAIL: /health unreachable"
  exit 1
}
echo "$HEALTH_JSON" | python3 -m json.tool
python3 -c "
import json, sys
d = json.loads(sys.argv[1])
assert d.get('ok') is True, d
for field in ('gemini', 'gemini_path', 'parallel', 'parallel_sdk', 'agent_builder', 'engine_default', 'revision'):
    assert field in d, f'missing {field} — hosted health stripped partners (FINDING 2026-09-11)'
assert d.get('engine_default') in ('adk', 'direct'), d.get('engine_default')
# Deployed Cloud Run should expose Vertex ADC + Parallel secret + ADK.
if d.get('mode') == 'private-workspaces' or d.get('revision', '').startswith('agent-science-'):
    assert d.get('gemini') is True, f'gemini must be true on hosted, got {d.get(\"gemini\")!r}'
    assert d.get('parallel') is True, f'parallel must be true on hosted, got {d.get(\"parallel\")!r}'
    assert d.get('parallel_sdk') is True, f'parallel_sdk must be true on hosted, got {d.get(\"parallel_sdk\")!r}'
    assert d.get('agent_builder') is True, f'agent_builder must be true on hosted, got {d.get(\"agent_builder\")!r}'
    assert d.get('engine_default') == 'adk', f'engine_default must be adk on hosted, got {d.get(\"engine_default\")!r}'
    path = d.get('gemini_path') or ''
    assert path.startswith('vertex:'), f'gemini_path must be vertex ADC, got {path!r}'
print('health checks OK')
" "$HEALTH_JSON"

echo
echo "--- 2. /partners (track manifest, no auth) ---"
# Do not follow host-alias redirects into /login; /partners must be public on this URL.
PARTNERS_CODE="$(curl -s -o /tmp/partners.body -w '%{http_code}' "$BASE/partners")"
PARTNERS_JSON="$(cat /tmp/partners.body)"
echo "HTTP $PARTNERS_CODE"
if [[ "$PARTNERS_CODE" != "200" ]]; then
  echo "FAIL: /partners must be public JSON, got HTTP $PARTNERS_CODE"
  echo "$PARTNERS_JSON" | head -c 400
  exit 1
fi
echo "$PARTNERS_JSON" | python3 -m json.tool | head -50
python3 -c "
import json, sys
d = json.loads(sys.argv[1])
tc = d.get('track_checklist') or {}
for key in ('parallel_search_at_runtime', 'gemini_at_runtime', 'adk_agent_builder', 'hosted_url_required', 'public_health_partners'):
    assert tc.get(key) is True, f'track_checklist.{key} not true: {tc}'
assert tc.get('hosted_clear_local_only') is True, 'hosted must declare /clear as local-only'
print('partners checklist OK')
" "$PARTNERS_JSON"

echo
echo "--- 3. Baseline vs shipping stranger-proof score ---"
ROOT="$ROOT" python3 - "$HEALTH_JSON" "$PARTNERS_JSON" <<'PY'
import json, os, sys
sys.path.insert(0, os.environ['ROOT'])
from cloud import partners
health = json.loads(sys.argv[1])
manifest = json.loads(sys.argv[2])
naive = {
    'ok': True,
    'service': 'agent-science',
    'mode': 'private-workspaces',
    'revision': health.get('revision'),
}
naive_score = partners.partner_proof_score(naive, None)
ship_score = partners.partner_proof_score(health, manifest)
print('naive_arm', naive_score)
print('shipping_arm', ship_score)
assert ship_score['score'] > naive_score['score'], (naive_score, ship_score)
assert ship_score['score'] == ship_score['denominator'], ship_score
print('baseline delta +%d' % (ship_score['score'] - naive_score['score']))
PY

echo
echo "--- 4. Hosted /clear boundary (must NOT be a silent public desk) ---"
CLEAR_CODE="$(curl -s -o /tmp/clear.body -w '%{http_code}' -X POST "$BASE/clear" \
  -H 'Content-Type: application/json' \
  -d '{"script":"boundary probe","subject":"partner-boundary"}')"
echo "POST /clear HTTP $CLEAR_CODE"
python3 -c "
import sys
code = int(sys.argv[1])
# 401 = workspace auth required; 404 = route absent; both prove local-only boundary.
assert code in (401, 404, 303, 405), f'unexpected /clear status {code} — do not reopen public clear without Oscar'
print('hosted /clear boundary OK (local-only)')
" "$CLEAR_CODE"

if [[ "${VERIFY_LOCAL_CLEAR:-0}" == "1" ]]; then
  echo
  echo "--- 5. Local /clear ADK+Parallel proof (optional; needs keys) ---"
  if [[ -z "${PARALLEL_API_KEY:-}" && ! -f "${HOME}/.config/keys/parallel.key" ]]; then
    echo "BLOCKED: PARALLEL_API_KEY missing — skip local clear proof"
  else
    python3 "$ROOT/scripts/partner_probe.py" || FAIL=1
  fi
else
  echo
  echo "--- 5. Local /clear proof skipped (set VERIFY_LOCAL_CLEAR=1 to run) ---"
fi

echo
if [[ "$FAIL" -ne 0 ]]; then
  echo "=== Partner hosted verify FAILED === $STAMP"
  exit 1
fi
echo "=== Partner hosted verify OK (public surfaces) === $STAMP"
echo "NOTE: live /clear + compound remain local-desk / post-deploy Oscar gates."
