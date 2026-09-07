#!/usr/bin/env bash
# New-user trial — run against hosted Agent Science as a stranger would.
# Usage: bash scripts/new_user_trial.sh [HOSTED_URL]
#
# Control contract: if hosted is private-workspaces (login wall), this script
# must exit non-zero with a named RED. A KeyError on a missing health field is
# not a control — that crash path was watched on 2026-09-07 and replaced.
set -euo pipefail
BASE="${1:-https://agent-science-568004190078.us-central1.run.app}"
SUBJ="trial-$(date +%H%M)"

echo "=== Agent Science new-user trial ==="
echo "URL: $BASE"
echo "GOAL: truth dictionary — free lookup first, compound on repeat"
echo

py() { python3 -c "$1"; }

echo "1. Health"
HEALTH_JSON="$(curl -sS -m 20 "$BASE/health" || true)"
if [[ -z "$HEALTH_JSON" ]]; then
  echo "  RED  /health empty or unreachable"
  exit 1
fi
echo "$HEALTH_JSON" | py "
import sys, json
d = json.load(sys.stdin)
assert d.get('ok'), d
mode = d.get('mode') or 'public-desk'
print('  ok', d.get('ok'), 'mode', mode, 'revision', d.get('revision'))
# Old desk shape (pre private-workspaces) carried partner wiring here.
if 'engine_default' in d:
    print('  engine', d.get('engine_default'), 'parallel', d.get('parallel'), 'gemini', d.get('gemini'))
if mode == 'private-workspaces':
    print('  RED  hosted mode is private-workspaces — stranger /search /registry /clear require an access key')
    print('  RED  public compound exhibit and free-lookup trial do not apply to this revision')
    print('  use offline: python3 tests/test_registry_surface.py -q && python3 scripts/compound_exhibit_receipt.py')
    sys.exit(2)
"

echo "2. Free lookup (dictionary — 0 Parallel)"
SEARCH_BODY="$(curl -sS -m 30 -w '\n%{http_code}' "$BASE/search?q=2012/28/EU&live=false" || true)"
echo "$SEARCH_BODY" | py "
import sys, json
raw = sys.stdin.read()
body, _, code = raw.rpartition('\n')
code = code.strip()
if 'Sign in' in body or code in {'303', '401', '403'}:
    print('  RED  /search login-walled or forbidden (http', code + ')')
    sys.exit(2)
d = json.loads(body)
print('  label', d['label'], 'tier', d.get('cost_tier'), 'parallel', d.get('parallel_api_calls', 0))
assert d['label'] == 'SOURCED', d
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
