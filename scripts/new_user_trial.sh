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
fail=0
ok() { echo "  OK  $*"; }
bad() { echo "  FAIL $*"; fail=$((fail+1)); }

echo "1. Health (partners wired)"
health=$(curl -sS -m 30 "$BASE/health" || true)
code=$(curl -sS -m 30 -o /dev/null -w '%{http_code}' "$BASE/health" || true)
if [[ "$code" != "200" ]]; then
  bad "health HTTP $code"
else
  if printf '%s' "$health" | py "
import sys,json
d=json.load(sys.stdin)
missing=[k for k in ('engine_default','parallel','gemini') if k not in d]
if missing:
    print('STRIPPED:', ','.join(missing), 'mode=', d.get('mode'), 'rev=', d.get('revision'))
    raise SystemExit(2)
print('  engine', d['engine_default'], 'parallel', d['parallel'], 'gemini', d['gemini'])
"; then
    ok "health partners"
  else
    bad "health partner fields stripped — Oscar deploy (see above)"
  fi
fi

echo "2. Free lookup (dictionary — 0 Parallel)"
code=$(curl -sS -m 30 -o /tmp/trial_search.json -w '%{http_code}' \
  "$BASE/search?q=2012/28/EU&live=false" || true)
if [[ "$code" != "200" ]]; then
  bad "free lookup HTTP $code (private-workspaces may 303)"
else
  py "
import json
d=json.load(open('/tmp/trial_search.json'))
print('  label', d['label'], 'tier', d.get('cost_tier'), 'parallel', d.get('parallel_api_calls',0))
assert d['label']=='SOURCED', d
" && ok "free lookup" || bad "free lookup body"
fi

echo "3. Miss without live (honest NOT_CLEARED)"
code=$(curl -sS -m 30 -o /tmp/trial_miss.json -w '%{http_code}' \
  "$BASE/search?q=xyzzy-nonexistent-claim-99999&live=false" || true)
if [[ "$code" != "200" ]]; then
  bad "miss HTTP $code"
else
  py "
import json
d=json.load(open('/tmp/trial_miss.json'))
print('  label', d['label'], 'next_step', bool(d.get('next_step')))
assert d['label']=='NOT_CLEARED', d
" && ok "miss path" || bad "miss body"
fi

echo "4. Dictionary stats + popular"
code=$(curl -sS -m 30 -o /tmp/trial_stats.json -w '%{http_code}' "$BASE/stats" || true)
if [[ "$code" != "200" ]]; then
  bad "stats HTTP $code"
else
  py "import json; d=json.load(open('/tmp/trial_stats.json')); print('  claims', d['n'], 'hit_rate', d.get('dictionary_hit_rate'))"
  ok "stats"
fi
code=$(curl -sS -m 30 -o /tmp/trial_popular.json -w '%{http_code}' "$BASE/popular?limit=3" || true)
if [[ "$code" != "200" ]]; then
  bad "popular HTTP $code"
else
  py "import json; d=json.load(open('/tmp/trial_popular.json')); [print('  ', r['asks'],'x', r['example'][:55]) for r in d.get('popular_queries',[])[:3]]"
  ok "popular"
fi

echo "5. Same subject twice — corpus compounding"
code=$(curl -sS -m 180 -o /tmp/as_A.json -w '%{http_code}' -X POST "$BASE/clear" \
  -H 'Content-Type: application/json' \
  -d "{\"script\":\"The Orphan Works Directive is Directive 2012/28/EU.\",\"subject\":\"$SUBJ\"}" || true)
if [[ "$code" != "200" ]]; then
  bad "clear Run A HTTP $code (workspace token required on private-workspaces)"
else
  py "import json; d=json.load(open('/tmp/as_A.json')); print('  Run A: parallel', d.get('parallel_api_calls'), 'corpus_hits', d.get('corpus_hits'))"
  code_b=$(curl -sS -m 180 -o /tmp/as_B.json -w '%{http_code}' -X POST "$BASE/clear" \
    -H 'Content-Type: application/json' \
    -d "{\"script\":\"Directive 2012/28/EU is the EU orphan works law.\",\"subject\":\"$SUBJ\"}" || true)
  if [[ "$code_b" != "200" ]]; then
    bad "clear Run B HTTP $code_b"
  else
    if py "
import json
d=json.load(open('/tmp/as_B.json'))
a=json.load(open('/tmp/as_A.json'))
ap, bp = a.get('parallel_api_calls',0), d.get('parallel_api_calls',0)
bh = d.get('corpus_hits',0)
print('  Run B: parallel', bp, 'corpus_hits', bh)
assert bh >= 1, ('expected corpus_hits>=1', ap, bp, bh)
assert bp <= ap, ('expected B not more expensive than A', ap, bp)
print('  COMPOUND OK (corpus hits on repeat)')
"; then
      ok "compound"
    else
      bad "compound"
    fi
  fi
fi

echo
if [[ "$fail" -eq 0 ]]; then
  echo "=== Trial OK ==="
  echo "  Desk:     $BASE/"
  echo "  Registry: $BASE/registry"
  echo "  Popular:  $BASE/popular/ui"
  echo "  Front:    $BASE/front"
  echo
  echo "New-user habit: /search?q=...&live=false first · live only on NOT_CLEARED"
  exit 0
fi
echo "=== Trial FAILED ($fail) ==="
echo "Private-workspaces live may 303/401 until Oscar deploy + workspace token."
echo "Offline stranger path: bash scripts/verify_cold_clone.sh"
exit 1
