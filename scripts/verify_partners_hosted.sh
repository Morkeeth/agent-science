#!/usr/bin/env bash
# Post-deploy verification — all four partners called at runtime on hosted desk.
# Oscar runs after deploy.sh; agents may run read-only against the live URL.
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
print('health checks OK')
" "$HEALTH_JSON"

echo
echo "--- 2. /partners (track manifest) ---"
PARTNERS_JSON="$(curl -sf "$BASE/partners")"
echo "$PARTNERS_JSON" | python3 -m json.tool | head -40
python3 -c "
import json, sys
d = json.loads(sys.argv[1])
tc = d.get('track_checklist') or {}
for key in ('parallel_search_at_runtime', 'gemini_at_runtime', 'adk_agent_builder', 'hosted_url_required'):
    assert tc.get(key) is True, f'track_checklist.{key} not true'
print('partners checklist OK')
" "$PARTNERS_JSON"

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
