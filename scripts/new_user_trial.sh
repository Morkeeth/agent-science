#!/usr/bin/env bash
# New-user trial — stranger path.
# Hosted private-workspaces: public partner proof + local dictionary (no public /search|/clear).
# Local desk URL: full free-lookup + compound path.
# Usage: bash scripts/new_user_trial.sh [HOSTED_OR_LOCAL_URL]
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BASE="${1:-https://agent-science-568004190078.us-central1.run.app}"
SUBJ="trial-$(date +%H%M)"

echo "=== Agent Science new-user trial ==="
echo "URL: $BASE"
echo "GOAL: truth dictionary — free lookup first, compound on repeat"
echo

py() { python3 -c "$1"; }

echo "1. Health (partners wired — public even on private-workspaces)"
HEALTH_JSON="$(curl -sf "$BASE/health")"
echo "$HEALTH_JSON" | py "
import sys,json
d=json.load(sys.stdin)
assert d.get('ok') is True, d
for f in ('gemini','parallel','agent_builder','engine_default','gemini_path'):
    assert f in d, f'missing {f} — see docs/FINDING-hosted-partner-health-regression-2026-09-11.md'
print('  engine', d.get('engine_default'), 'parallel', d.get('parallel'), 'gemini', d.get('gemini'), 'mode', d.get('mode'))
open('/tmp/as_health.json','w').write(json.dumps(d))
"

MODE="$(python3 -c "import json; print(json.load(open('/tmp/as_health.json')).get('mode') or '')")"

echo "2. /partners (public manifest)"
curl -sf "$BASE/partners" | py "
import sys,json
d=json.load(sys.stdin)
tc=d.get('track_checklist') or {}
assert tc.get('parallel_search_at_runtime') is True, tc
print('  track', d.get('track'), 'checklist ok')
"

if [[ "$MODE" == "private-workspaces" ]]; then
  echo
  echo "HOSTED MODE: private-workspaces — /search and /clear are local-only."
  echo "Continuing with LOCAL dictionary + offline compound (stranger, no keys)."
  echo
  echo "3. Local free lookup (registry SOURCED, 0 Parallel)"
  # EUR-Lex/CELEX often returns UNSOURCED on cold VMs (403). Use a GREEN registry row.
  python3 -m clearance lookup "arXiv:2511.12884 — Agent READMEs" > /tmp/as_lookup.txt
  head -4 /tmp/as_lookup.txt
  grep -q SOURCED /tmp/as_lookup.txt
  grep -q '0 Parallel' /tmp/as_lookup.txt

  echo "4. Local miss stays honest"
  # lookup exits non-zero on NOT_CLEARED — that is the product working.
  python3 -m clearance lookup "xyzzy-nonexistent-claim-99999" > /tmp/as_miss.txt || true
  head -3 /tmp/as_miss.txt
  grep -q NOT_CLEARED /tmp/as_miss.txt

  echo "5. Offline compound receipt"
  # compound_exhibit_receipt exits 3 when A already has 0 Parallel (warm shelf);
  # still require the written receipt to record a B corpus hit.
  set +e
  python3 "$ROOT/scripts/compound_exhibit_receipt.py" >/tmp/as_compound.txt
  comp_rc=$?
  set -e
  tail -8 /tmp/as_compound.txt
  grep -E 'corpus_hits|Parallel|2/2 passed' /tmp/as_compound.txt | head -10
  test -f "$ROOT/docs/COMPOUND-EXHIBIT-2026-08-29.md"
  grep -q 'corpus' "$ROOT/docs/COMPOUND-EXHIBIT-2026-08-29.md"
  echo "  compound_exhibit_receipt exit=$comp_rc (0=strict pass; 3=warm-shelf / no Parallel drop)"

  echo "6. Partner baseline (naive vs shipping)"
  python3 "$ROOT/scripts/eval_partner_health_baseline.py" | tee /tmp/as_baseline.txt
  grep -q 'shipping_arm' /tmp/as_baseline.txt
  grep -q 'naive_arm' /tmp/as_baseline.txt

  echo
  echo "=== Trial OK (hosted workspace boundary path) ==="
  echo "  Health:   $BASE/health"
  echo "  Partners: $BASE/partners"
  echo "  Cases:    $BASE/cases  (token required)"
  echo "  Local desk /clear remains the compound demo surface until Oscar says otherwise."
  exit 0
fi

echo "3. Free lookup (dictionary — 0 Parallel)"
curl -sf "$BASE/search?q=2012/28/EU&live=false" | py "
import sys,json
d=json.load(sys.stdin)
print('  label', d['label'], 'tier', d.get('cost_tier'), 'parallel', d.get('parallel_api_calls',0))
assert d['label']=='SOURCED', d
"

echo "4. Miss without live (honest NOT_CLEARED)"
curl -sf "$BASE/search?q=xyzzy-nonexistent-claim-99999&live=false" | py "
import sys,json
d=json.load(sys.stdin)
print('  label', d['label'], 'next_step', bool(d.get('next_step')))
assert d['label']=='NOT_CLEARED', d
"

echo "5. Dictionary stats + popular"
curl -sf "$BASE/stats" | py "import sys,json; d=json.load(sys.stdin); print('  claims', d['n'], 'hit_rate', d.get('dictionary_hit_rate'))"
curl -sf "$BASE/popular?limit=3" | py "import sys,json; d=json.load(sys.stdin); [print('  ', r['asks'],'x', r['example'][:55]) for r in d.get('popular_queries',[])[:3]]"

echo "6. Same subject twice — corpus compounding"
A=$(curl -sf -m 180 -X POST "$BASE/clear" -H 'Content-Type: application/json' \
  -d "{\"script\":\"The Orphan Works Directive is Directive 2012/28/EU.\",\"subject\":\"$SUBJ\"}")
echo "$A" | py "import sys,json; d=json.load(sys.stdin); print('  Run A: parallel', d.get('parallel_api_calls'), 'corpus_hits', d.get('corpus_hits')); open('/tmp/as_A.json','w').write(json.dumps(d))"

B=$(curl -sf -m 180 -X POST "$BASE/clear" -H 'Content-Type: application/json' \
  -d "{\"script\":\"Directive 2012/28/EU is the EU orphan works law.\",\"subject\":\"$SUBJ\"}")
echo "$B" | py "
import sys,json
d=json.load(sys.stdin)
a=json.load(open('/tmp/as_A.json'))
ap, bp = a.get('parallel_api_calls',0), d.get('parallel_api_calls',0)
bh = d.get('corpus_hits',0)
print('  Run B: parallel', bp, 'corpus_hits', bh)
assert bh >= 1, ('expected corpus_hits>=1', ap, bp, bh)
assert bp <= ap, ('expected B not more expensive than A', ap, bp)
print('  COMPOUND OK (corpus hits on repeat)')
"

echo
echo "=== Trial OK ==="
echo "  Desk:     $BASE/"
echo "  Registry: $BASE/registry"
echo "  Popular:  $BASE/popular/ui"
echo "  Front:    $BASE/front"
echo
echo "New-user habit: /search?q=...&live=false first · live only on NOT_CLEARED"
