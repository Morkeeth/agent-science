#!/usr/bin/env bash
# New-user trial — stranger path. Prefer local (no keys). Hosted anonymous
# desk steps only run when /health still exposes a public search surface.
# Usage: bash scripts/new_user_trial.sh [HOSTED_URL]
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
BASE="${1:-https://agent-science-568004190078.us-central1.run.app}"

echo "=== Agent Science new-user trial ==="
echo "URL: $BASE"
echo "GOAL: truth dictionary — free lookup first, compound on repeat"
echo

py() { python3 -c "$1"; }

echo "0. Local stranger block (authoritative — no keys)"
python3 tests/test_registry_surface.py -q | tail -1
python3 -m clearance lookup "2012/28/EU" 2>&1 | head -1 | grep -q SOURCED
echo "  local lookup 2012/28/EU SOURCED"
python3 scripts/compound_exhibit_receipt.py >/tmp/as_compound.txt
grep -q 'Run B parallel < Run A: \*\*yes\*\*' /tmp/as_compound.txt
grep -q 'corpus_hits B ≥ 1: \*\*yes\*\*' /tmp/as_compound.txt
echo "  offline compound A→B PASS"

echo "1. Hosted health (mode at object)"
HEALTH=$(curl -sS -m 20 "$BASE/health")
echo "$HEALTH" | py "
import sys,json
d=json.load(sys.stdin)
assert d.get('ok') is True
mode=d.get('mode') or 'legacy-public'
print('  mode', mode, 'revision', d.get('revision'))
open('/tmp/as_health_mode','w').write(mode)
"

MODE=$(cat /tmp/as_health_mode)
if [[ "$MODE" == "private-workspaces" ]]; then
  echo
  echo "=== Trial OK (local) · HOSTED ANONYMOUS DESK BLOCKED ==="
  echo "  Hosted mode=private-workspaces — /search /clear /stats require a workspace token."
  echo "  Do not claim anonymous free-tier hosted lookup or hosted compound from this script."
  echo "  Local path above is the stranger proof. Oscar: tokenized trial or film the login wall."
  exit 0
fi

echo "2. Free lookup (dictionary — 0 Parallel) [legacy public desk]"
curl -sf "$BASE/search?q=2012/28/EU&live=false" | py "
import sys,json
d=json.load(sys.stdin)
print('  label', d['label'], 'tier', d.get('cost_tier'), 'parallel', d.get('parallel_api_calls',0))
assert d['label']=='SOURCED', d
"

echo "3. Miss without live (honest NOT_CLEARED)"
curl -sf "$BASE/search?q=xyzzy-nonexistent-claim-99999&live=false" | py "
import sys,json
d=json.load(sys.stdin)
print('  label', d['label'], 'next_step', bool(d.get('next_step')))
assert d['label']=='NOT_CLEARED', d
"

echo "4. Dictionary stats + popular"
curl -sf "$BASE/stats" | py "import sys,json; d=json.load(sys.stdin); print('  claims', d['n'], 'hit_rate', d.get('dictionary_hit_rate'))"

SUBJ="trial-$(date +%H%M)"
echo "5. Same subject twice — corpus compounding"
A=$(curl -sf -m 180 -X POST "$BASE/clear" -H 'Content-Type: application/json' \
  -d "{\"script\":\"The Orphan Works Directive is Directive 2012/28/EU.\",\"subject\":\"$SUBJ\"}")
echo "$A" | py "import sys,json; d=json.load(sys.stdin); print('  Run A: parallel', d.get('parallel_api_calls'), 'corpus_hits', d.get('corpus_hits')); open('/tmp/as_A.json','w').write(json.dumps(d))"

B=$(curl -sf -m 180 -X POST "$BASE/clear" -H 'Content-Type: application/json' \
  -d "{\"script\":\"The Orphan Works Directive is Directive 2012/28/EU.\",\"subject\":\"$SUBJ\"}")
echo "$B" | py "
import sys,json
d=json.load(sys.stdin)
a=json.load(open('/tmp/as_A.json'))
ap, bp = a.get('parallel_api_calls',0), d.get('parallel_api_calls',0)
bh = d.get('corpus_hits',0)
print('  Run B: parallel', bp, 'corpus_hits', bh)
assert bh >= 1, ('expected corpus_hits>=1', ap, bp, bh)
assert bp <= ap, ('expected B not more expensive than A', ap, bp)
print('  COMPOUND OK (corpus hits on repeat; exact assertion)')
"

echo
echo "=== Trial OK ==="
echo "  Desk:     $BASE/"
echo "  Registry: $BASE/registry"
echo "  Popular:  $BASE/popular/ui"
echo
echo "New-user habit: /search?q=...&live=false first · live only on NOT_CLEARED"
