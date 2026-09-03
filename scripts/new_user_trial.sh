#!/usr/bin/env bash
# New-user trial — run against hosted Agent Science as a stranger would.
# Usage: bash scripts/new_user_trial.sh [HOSTED_URL]
set -euo pipefail
BASE="${1:-https://agent-science-568004190078.us-central1.run.app}"
SUBJ="trial-$(date +%H%M)"

echo "=== Agent Science new-user trial ==="
echo "URL: $BASE"
echo "GOAL: truth dictionary — free lookup first, compound on repeat"
echo

py() { python3 -c "$1"; }

echo "1. Health (partners wired)"
curl -sf "$BASE/health" | py "import sys,json; d=json.load(sys.stdin); assert d['ok']; print('  engine', d['engine_default'], 'parallel', d['parallel'], 'gemini', d['gemini'])"

echo "2. Free lookup (dictionary — 0 Parallel)"
curl -sf "$BASE/search?q=2012/28/EU&live=false&traffic=gate" | py "
import sys,json
d=json.load(sys.stdin)
print('  label', d['label'], 'tier', d.get('cost_tier'), 'parallel', d.get('parallel_api_calls',0), 'traffic', d.get('traffic'))
assert d['label']=='SOURCED', d
"

echo "3. Miss without live (honest NOT_CLEARED)"
curl -sf "$BASE/search?q=xyzzy-nonexistent-claim-99999&live=false&traffic=gate" | py "
import sys,json
d=json.load(sys.stdin)
print('  label', d['label'], 'next_step', bool(d.get('next_step')), 'traffic', d.get('traffic'))
assert d['label']=='NOT_CLEARED', d
"

echo "4. Dictionary stats + popular"
curl -sf "$BASE/stats" | py "import sys,json; d=json.load(sys.stdin); print('  claims', d['n'], 'hit_rate', d.get('dictionary_hit_rate'))"
curl -sf "$BASE/popular?limit=3" | py "import sys,json; d=json.load(sys.stdin); [print('  ', r['asks'],'x', r['example'][:55]) for r in d.get('popular_queries',[])[:3]]"

echo "5. Same subject twice — corpus compounding"
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
# Seeded dictionary: A may already be 0 Parallel; B must hit corpus shelf.
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
