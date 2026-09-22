#!/usr/bin/env bash
# Post-deploy verification — all four partners visible on hosted desk.
# Oscar runs after deploy.sh; agents may run read-only against the live URL.
#
# Usage: bash scripts/verify_partners_hosted.sh [BASE_URL]
#
# Private-workspaces note (2026-09-16): unauthenticated /clear is local-only.
# Steps 1–2 are public partner proof. Steps 3–5 need WORKSPACE_TOKEN (or
# AGENT_SCIENCE_WORKSPACE_TOKEN) for /clear compound probes; without a token
# those steps print BLOCKED and the script exits non-zero so a green run
# cannot mean "ok=true with partner fields stripped".
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BASE="${1:-https://agent-science-568004190078.us-central1.run.app}"
STAMP="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
TOKEN="${WORKSPACE_TOKEN:-${AGENT_SCIENCE_WORKSPACE_TOKEN:-}}"
BLOCKED=0

echo "=== Partner hosted verify === stamp=$STAMP"
echo "URL: $BASE"
echo

echo "--- 1. /health (Gemini · Parallel · Cloud Run · ADK) ---"
HEALTH_JSON="$(curl -sf "$BASE/health")"
echo "$HEALTH_JSON" | python3 -m json.tool
python3 -c "
import json, sys
d = json.loads(sys.argv[1])
# A body that is only ok/service/mode/revision is a FALSE GREEN — watched on
# revision agent-science-00028-hed (2026-09-16).
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
    assert got == v, f'{k}: expected {v!r}, got {got!r} (keys={sorted(d)})'
path = d.get('gemini_path') or ''
assert path.startswith('vertex:'), f'gemini_path must be vertex ADC, got {path!r}'
print('health checks OK · mode=', d.get('mode'), '· revision=', d.get('revision'))
" "$HEALTH_JSON"

echo
echo "--- 2. /partners (track manifest, public) ---"
# Do not follow redirects: a 303 to login is the private-workspaces strip defect
# (watched live 2026-09-22 on revision agent-science-00028-hed).
PARTNERS_CODE="$(curl -s -o /tmp/partners_hosted_body.json -w '%{http_code}' "$BASE/partners")"
PARTNERS_JSON="$(cat /tmp/partners_hosted_body.json)"
echo "HTTP $PARTNERS_CODE"
if [[ "$PARTNERS_CODE" != "200" ]]; then
  echo "FAIL: /partners must be public JSON on this URL (no 303 to login)."
  echo "body: ${PARTNERS_JSON:0:200}"
  exit 1
fi
echo "$PARTNERS_JSON" | python3 -m json.tool | head -40
python3 -c "
import json, sys
d = json.loads(sys.argv[1])
assert isinstance(d, dict) and 'track_checklist' in d, 'partners must be JSON manifest, not login HTML'
tc = d.get('track_checklist') or {}
for key in ('parallel_search_at_runtime', 'gemini_at_runtime', 'adk_agent_builder', 'hosted_url_required'):
    assert tc.get(key) is True, f'track_checklist.{key} not true'
print('partners checklist OK')
" "$PARTNERS_JSON"

echo
if [[ -z "$TOKEN" ]]; then
  echo "--- 3–5. POST /clear + compound probes ---"
  echo "BLOCKED: no WORKSPACE_TOKEN / AGENT_SCIENCE_WORKSPACE_TOKEN in env."
  echo "Hosted /clear is workspace-auth only (private-workspaces). Public partner"
  echo "proof is steps 1–2. Oscar: export WORKSPACE_TOKEN=… then re-run for ADK+Parallel call."
  BLOCKED=1
else
  echo "--- 3. POST /clear (ADK + Parallel at runtime, workspace token) ---"
  SUBJECT_TOKEN="$(python3 -c 'import uuid; print(uuid.uuid4().hex[:12])')"
  SUBJECT="partner-verify-$SUBJECT_TOKEN"
  CLEAR_JSON="$(curl -sf -X POST "$BASE/clear" \
    -H "Authorization: Bearer $TOKEN" \
    -H 'Content-Type: application/json' \
    -d "{\"script\":\"In ${SUBJECT_TOKEN} the Archive of Zephyr-${SUBJECT_TOKEN} passed Regulation Z-${SUBJECT_TOKEN} for orphan media.\",\"subject\":\"$SUBJECT\"}")" \
    || CLEAR_JSON=""
  if [[ -z "$CLEAR_JSON" ]]; then
    echo "BLOCKED: POST /clear with workspace token did not return JSON (401/404/HTML)."
    echo "On private-workspaces the clearance desk may only live on /cases — see partner doc."
    BLOCKED=1
  else
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
  fi
fi

echo
if [[ "$BLOCKED" -eq 1 ]]; then
  echo "=== Partner hosted verify PARTIAL === $STAMP (public health+partners OK; /clear BLOCKED)"
  exit 2
fi
echo "=== Partner hosted verify OK === $STAMP"
