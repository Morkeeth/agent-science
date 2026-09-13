#!/usr/bin/env bash
# Post-deploy verification — partner surfaces on hosted URL.
# Oscar runs after deploy.sh; agents may run read-only against the live URL.
#
# Private-workspaces mode (current hosted): public /health + /partners must
# expose all four partners. POST /clear is local-desk only — proved by
# scripts/verify_partners_local.sh, not by curling the hosted URL.
#
# Usage: bash scripts/verify_partners_hosted.sh [BASE_URL]
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BASE="${1:-https://agent-science-568004190078.us-central1.run.app}"
STAMP="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

echo "=== Partner hosted verify === stamp=$STAMP"
echo "URL: $BASE"
echo

echo "--- 1. /health (Gemini · Parallel · Cloud Run · ADK) ---"
HEALTH_JSON="$(curl -sf "$BASE/health")"
echo "$HEALTH_JSON" | python3 -m json.tool
MODE="$(python3 -c "import json,sys; print(json.loads(sys.argv[1]).get('mode') or 'legacy-desk')" "$HEALTH_JSON")"
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
assert path.startswith('vertex:'), f'gemini_path must be vertex ADC, got {path!r}'
print('health checks OK · mode=', d.get('mode') or 'legacy-desk')
" "$HEALTH_JSON"

echo
echo "--- 2. /partners (track manifest — must NOT require login) ---"
PARTNERS_JSON="$(curl -sf "$BASE/partners")"
echo "$PARTNERS_JSON" | python3 -m json.tool | head -50
python3 -c "
import json, sys
d = json.loads(sys.argv[1])
tc = d.get('track_checklist') or {}
for key in ('parallel_search_at_runtime', 'gemini_at_runtime', 'adk_agent_builder', 'hosted_url_required'):
    assert tc.get(key) is True, f'track_checklist.{key} not true'
partners = d.get('partners') or {}
for name in ('gemini_vertex', 'parallel', 'google_cloud', 'agent_builder_adk'):
    assert name in partners, f'missing partner {name}'
print('partners checklist OK')
" "$PARTNERS_JSON"

if [[ "$MODE" == "private-workspaces" ]]; then
  echo
  echo "--- 3. POST /clear (hosted) ---"
  echo "SKIP — private-workspaces: unauthenticated /clear is local-only (AGENTS.md)."
  echo "Prove clearance + ADK engine locally:"
  echo "  bash scripts/verify_partners_local.sh"
  echo
  echo "--- 4–5. Compound A/B (hosted public /clear) ---"
  echo "SKIP — same boundary. Offline compound remains authoritative:"
  echo "  python3 scripts/compound_exhibit_receipt.py"
  echo
  echo "=== Partner hosted verify OK (health + partners) === $STAMP"
  echo "mode=private-workspaces · clear/compound deferred to local desk"
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
