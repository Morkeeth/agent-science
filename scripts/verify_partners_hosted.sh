#!/usr/bin/env bash
# Post-deploy verification — partner surfaces on hosted desk.
# Oscar runs after deploy.sh; agents may run read-only against the live URL.
#
# Private-workspaces (AGENT_SCIENCE_HOSTED / K_SERVICE):
#   · /health and /partners stay PUBLIC (admissibility proof)
#   · /clear, /search, compound probes require a workspace bearer token
#     (set AGENT_SCIENCE_WORKSPACE_TOKEN) or are reported BLOCKED — not skipped silently.
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
MODE="$(python3 -c "import json,sys; print(json.loads(sys.argv[1]).get('mode') or '')" "$HEALTH_JSON")"
python3 -c "
import json, sys
d = json.loads(sys.argv[1])
required = ('ok', 'gemini', 'parallel', 'parallel_sdk', 'agent_builder', 'engine_default', 'gemini_path')
missing = [k for k in required if k not in d]
if missing:
    raise SystemExit(
        'FAIL: /health missing partner fields '
        + str(missing)
        + ' — see docs/FINDING-hosted-partner-proof-dark-2026-09-11.md'
    )
assert d.get('ok') is True
assert d.get('engine_default') in ('adk', 'direct'), d.get('engine_default')
# On a fully wired Cloud Run image we expect partners true + adk default.
# A stripped health (pre-fix) fails above. A wired desk without ADK import
# reports engine_default=direct — still a named partner surface, not silence.
print('health partner fields OK')
print('mode:', d.get('mode') or '(local-desk)')
print('engine_default:', d.get('engine_default'))
print('gemini_path:', d.get('gemini_path'))
print('parallel:', d.get('parallel'), 'sdk:', d.get('parallel_sdk'))
print('agent_builder:', d.get('agent_builder'))
" "$HEALTH_JSON"

echo
echo "--- 2. /partners (track manifest, public) ---"
PARTNERS_JSON="$(curl -sf "$BASE/partners")"
echo "$PARTNERS_JSON" | python3 -m json.tool | head -40
python3 -c "
import json, sys
d = json.loads(sys.argv[1])
tc = d.get('track_checklist') or {}
for key in ('parallel_search_at_runtime', 'gemini_at_runtime', 'adk_agent_builder', 'hosted_url_required'):
    assert key in tc, f'track_checklist.{key} missing'
print('partners checklist OK')
" "$PARTNERS_JSON"

if [[ "$MODE" == "private-workspaces" && -z "$TOKEN" ]]; then
  echo
  echo "--- 3–5. /clear + compound — BLOCKED (private-workspaces, no AGENT_SCIENCE_WORKSPACE_TOKEN) ---"
  echo "Public /clear is intentionally gated. Partner *wiring* was proved at /health + /partners."
  echo "To prove live Parallel on /clear after Oscar deploy:"
  echo "  AGENT_SCIENCE_WORKSPACE_TOKEN=<bearer> bash scripts/verify_partners_hosted.sh"
  echo "Or run the local desk proof (no Cloud Run):"
  echo "  bash scripts/prove_partners_local.sh"
  echo
  echo "=== Partner hosted verify PARTIAL OK (public surfaces) === $STAMP"
  exit 0
fi

echo
echo "--- 3. POST /clear (ADK + Parallel at runtime) ---"
AUTH_ARGS=()
if [[ -n "$TOKEN" ]]; then
  AUTH_ARGS=(-H "Authorization: Bearer $TOKEN")
fi
CLEAR_TOKEN="$(python3 -c 'import uuid; print(uuid.uuid4().hex[:12])')"
SUBJECT="partner-verify-$CLEAR_TOKEN"
CLEAR_JSON="$(curl -sf -X POST "$BASE/clear" \
  "${AUTH_ARGS[@]}" \
  -H 'Content-Type: application/json' \
  -d "{\"script\":\"In ${CLEAR_TOKEN} the Archive of Zephyr-${CLEAR_TOKEN} passed Regulation Z-${CLEAR_TOKEN} for orphan media.\",\"subject\":\"$SUBJECT\"}")"
python3 -c "
import json, sys
d = json.loads(sys.argv[1])
assert d.get('engine') in ('adk', 'direct'), f\"engine missing, got {d.get('engine')!r}\"
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
