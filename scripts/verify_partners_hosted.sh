#!/usr/bin/env bash
# Post-deploy verification — partner readiness on hosted URL.
# Oscar runs after deploy.sh; agents may run read-only against the live URL.
#
# Product boundary (2026-09): shared /clear /search /ingest are local-only.
# Hosted Cloud Run is private workspaces. Partners are still proved by:
#   GET /health   — gemini · parallel · ADK engine_default (public, no secrets)
#   GET /partners — track manifest (public)
#   Parallel live calls happen on authenticated workspace research (case_worker).
#
# Usage: bash scripts/verify_partners_hosted.sh [BASE_URL]
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BASE="${1:-https://agent-science-568004190078.us-central1.run.app}"
STAMP="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
# Do not hide failures behind a pipe to tail/head (false green).
FAIL=0

echo "=== Partner hosted verify === stamp=$STAMP"
echo "URL: $BASE"
echo

echo "--- 1. /health (Gemini · Parallel · Cloud Run · ADK) ---"
HEALTH_JSON="$(curl -sf "$BASE/health")" || { echo "FAIL: /health unreachable"; exit 1; }
echo "$HEALTH_JSON" | python3 -m json.tool
python3 -c "
import json, sys
d = json.loads(sys.argv[1])
req = {
    'ok': True,
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
assert path.startswith('vertex:') or path == 'api-key', f'gemini_path must be vertex ADC or api-key, got {path!r}'
mode = d.get('mode')
if mode == 'private-workspaces':
    assert d.get('clear_path') == 'local-desk', 'hosted health must name clear_path=local-desk'
    assert d.get('parallel_hosted_path') == 'workspace-live-research', 'hosted health must name Parallel research path'
    print('health checks OK (private-workspaces + partner fields)')
else:
    print('health checks OK (local-desk shape)')
" "$HEALTH_JSON" || FAIL=1

echo
echo "--- 2. /partners (track manifest, public, no auth) ---"
PARTNERS_CODE="$(curl -s -o /tmp/partners_body.json -w '%{http_code}' "$BASE/partners")"
if [[ "$PARTNERS_CODE" != "200" ]]; then
  echo "FAIL: /partners HTTP $PARTNERS_CODE (must be public JSON for judges)"
  FAIL=1
else
  python3 -m json.tool < /tmp/partners_body.json | head -40
  python3 -c "
import json, sys
d = json.load(open('/tmp/partners_body.json'))
tc = d.get('track_checklist') or {}
for key in ('parallel_search_at_runtime', 'gemini_at_runtime', 'adk_agent_builder', 'hosted_url_required', 'public_partner_health'):
    assert tc.get(key) is True, f'track_checklist.{key} not true'
print('partners checklist OK')
" || FAIL=1
fi

echo
echo "--- 3. POST /clear (gated on private-workspaces; required on local desk) ---"
CLEAR_CODE="$(curl -s -o /tmp/clear_body.json -w '%{http_code}' -X POST "$BASE/clear" \
  -H 'Content-Type: application/json' \
  -d '{"script":"The Dust Bowl displaced 2.5 million people.","subject":"partner-verify-probe"}')"
echo "HTTP $CLEAR_CODE"
if [[ "$CLEAR_CODE" == "401" || "$CLEAR_CODE" == "303" ]]; then
  echo "OK: hosted /clear gated (workspace boundary). ADK clear path = local desk."
  echo "    Prove Parallel runtime on hosted via authenticated live research, not shared /clear."
elif [[ "$CLEAR_CODE" == "200" || "$CLEAR_CODE" == "422" ]]; then
  python3 -c "
import json
d = json.load(open('/tmp/clear_body.json'))
assert d.get('engine') == 'adk', f\"engine must be adk, got {d.get('engine')!r}\"
assert (d.get('claims_extracted') or 0) >= 1 or d.get('ok') is False, 'expected claim extract or structured refuse'
parallel = d.get('parallel_calls') or 0
print('clear engine:', d.get('engine'))
print('parallel_calls:', parallel)
print('corpus_hits:', d.get('corpus_hits'))
" || FAIL=1
  echo
  echo "--- 4. Compound-mini A/B (warm shelf) ---"
  python3 "$ROOT/scripts/compound_hosted_probe.py" "$BASE" || FAIL=1
  echo
  echo "--- 5. Compound-fresh A/B ---"
  python3 "$ROOT/scripts/compound_fresh_hosted_probe.py" "$BASE" || FAIL=1
else
  echo "FAIL: unexpected /clear HTTP $CLEAR_CODE"
  head -c 400 /tmp/clear_body.json; echo
  FAIL=1
fi

echo
if [[ "$FAIL" -ne 0 ]]; then
  echo "=== Partner hosted verify FAILED === $STAMP"
  exit 1
fi
echo "=== Partner hosted verify OK === $STAMP"
exit 0
