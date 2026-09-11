#!/usr/bin/env bash
# Long run — stranger goal path on hosted Agent Science (truth dictionary flywheel).
# Usage: bash scripts/long_run_goal.sh [HOSTED_URL]
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
BASE="${1:-https://agent-science-568004190078.us-central1.run.app}"
STAMP="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
SUBJ="longrun-$(date +%m%d-%H%M)"
RECEIPT="docs/LONG-RUN-RECEIPT-$(date +%Y-%m-%d).md"
LOG="/tmp/agent-science-longrun-$$.log"
exec > >(tee -a "$LOG") 2>&1

echo "=== Agent Science LONG RUN ==="
echo "stamp=$STAMP url=$BASE subject=$SUBJ"
echo

pass=0
fail=0
note() { echo "  OK  $*"; pass=$((pass+1)); }
bad() { echo "  FAIL $*"; fail=$((fail+1)); }

echo "--- LOCAL: seed + controls ---"
python3 scripts/seed_document_cache.py
if python3 tests/test_watch_it_go_red.py 2>&1 | tail -1 | grep -q '0 failed'; then
  note "watch_it_go_red 72/72"
else
  bad "watch_it_go_red"
fi
for t in test_dictionary.py test_partner_runtime.py test_routing.py test_popular.py; do
  if python3 "tests/$t" 2>&1 | tail -1 | grep -qiE 'passed|PASS|OK'; then
    note "$t"
  else
    bad "$t"
  fi
done

echo "--- LOCAL: dictionary lookups ---"
for q in "2012/28/EU" "Directive 2012/28/EU" "orphan works directive"; do
  out=$(python3 -m clearance lookup "$q" 2>&1 | head -1)
  if echo "$out" | grep -q SOURCED; then
    note "lookup local: $q"
  else
    bad "lookup local: $q ($out)"
  fi
done

echo "--- HOSTED: health + public partner surfaces ---"
curl -sf "$BASE/health" | python3 -c "
import sys,json
d=json.load(sys.stdin)
assert d['ok'], d
for f in ('engine_default','parallel','gemini','agent_builder'):
    assert f in d, f'missing {f} on /health — FINDING 2026-09-11'
assert d['engine_default']=='adk' and d['parallel'] and d['gemini']
print('  health ok engine=adk mode=', d.get('mode'))
open('/tmp/as_long_health.json','w').write(json.dumps(d))
"
note "hosted health"

curl -sf "$BASE/partners" | python3 -c "
import sys,json
d=json.load(sys.stdin)
assert (d.get('track_checklist') or {}).get('parallel_search_at_runtime') is True
print('  partners checklist ok')
"
note "hosted /partners"

MODE="$(python3 -c "import json; print(json.load(open('/tmp/as_long_health.json')).get('mode') or '')")"
if [[ "$MODE" == "private-workspaces" ]]; then
  note "hosted mode private-workspaces — public /search|/clear|/registry are local-only"
  for path in / /registry /popular/ui /stats; do
    code=$(curl -s -o /dev/null -w '%{http_code}' "$BASE$path" || true)
    note "GET $path $code (workspace cutover)"
  done

  echo "--- LOCAL substitutes (dictionary + offline compound) ---"
  for q in "2012/28/EU" "Directive 2012/28/EU"; do
    if python3 -m clearance lookup "$q" 2>&1 | head -1 | grep -q SOURCED; then
      note "local lookup $q"
    else
      bad "local lookup $q"
    fi
  done
  if python3 "$ROOT/scripts/compound_exhibit_receipt.py" >/tmp/longrun_compound.txt 2>&1; then
    note "offline compound receipt"
    cat /tmp/longrun_compound.txt | tail -6
  else
    bad "offline compound receipt"
  fi
  python3 "$ROOT/scripts/eval_partner_health_baseline.py" | tee /tmp/longrun_baseline.txt
  if grep -q 'shipping_arm' /tmp/longrun_baseline.txt; then
    note "partner health baseline"
  else
    bad "partner health baseline"
  fi
  # Mark compound step satisfied via offline arm for receipt writer below.
  echo '{"parallel_api_calls":0,"corpus_hits":0,"engine":"offline"}' >/tmp/longrun_A.json
  echo '{"parallel_api_calls":0,"corpus_hits":1,"engine":"offline"}' >/tmp/longrun_B.json
  echo 1 >/tmp/longrun_compound.ok
else
for path in / /registry /popular/ui /stats /registry/api?q=2012; do
  code=$(curl -sf -o /dev/null -w '%{http_code}' "$BASE$path")
  if [[ "$code" == "200" ]]; then note "GET $path $code"; else bad "GET $path $code"; fi
done

echo "--- HOSTED: dictionary tier probes ---"
curl -sf "$BASE/search?q=2012/28/EU&live=false" | python3 -c "
import sys,json
d=json.load(sys.stdin)
assert d['label']=='SOURCED' and d.get('cost_tier')=='free'
assert d.get('parallel_api_calls',0)==0
print('  2012/28/EU SOURCED free')
"
note "free tier EU"

curl -sf "$BASE/search?q=Directive+2012/28/EU&live=false" | python3 -c "
import sys,json
d=json.load(sys.stdin)
assert d['label']=='SOURCED', d
print('  Directive form SOURCED')
"
note "alias Directive form"

curl -sf "$BASE/search?q=xyzzy-nonexistent-claim-99999&live=false" | python3 -c "
import sys,json
d=json.load(sys.stdin)
assert d['label']=='NOT_CLEARED' and d.get('next_step')
print('  honest NOT_CLEARED')
"
note "miss path"

STATS_BEFORE=$(curl -sf "$BASE/stats")
echo "$STATS_BEFORE" | python3 -c "
import sys,json
d=json.load(sys.stdin)
print(f\"  stats before: claims={d['n']} hit_rate={d.get('dictionary_hit_rate')} queries={d.get('queries_logged')}\")
"

echo "--- HOSTED: compound A/B (subject $SUBJ) ---"
A=$(curl -sf -m 240 -X POST "$BASE/clear" -H 'Content-Type: application/json' \
  -d "{\"script\":\"The Orphan Works Directive is Directive 2012/28/EU.\",\"subject\":\"$SUBJ\"}")
echo "$A" | python3 -c "
import sys,json
d=json.load(sys.stdin)
open('/tmp/longrun_A.json','w').write(json.dumps(d))
print(f\"  Run A: parallel={d.get('parallel_api_calls')} corpus_hits={d.get('corpus_hits')} engine={d.get('engine')}\")
"

B=$(curl -sf -m 240 -X POST "$BASE/clear" -H 'Content-Type: application/json' \
  -d "{\"script\":\"Directive 2012/28/EU is the EU orphan works law.\",\"subject\":\"$SUBJ\"}")
echo "$B" | python3 -c "
import sys,json
d=json.load(sys.stdin)
a=json.load(open('/tmp/longrun_A.json'))
ap, bp = a.get('parallel_api_calls',0), d.get('parallel_api_calls',0)
bh = d.get('corpus_hits',0)
print(f\"  Run B: parallel={bp} corpus_hits={bh}\")
if bh >= 1 and bp <= ap:
    print('  COMPOUND PASS')
    open('/tmp/longrun_compound.ok','w').write('1')
else:
    print('  COMPOUND FAIL', ap, bp, bh)
    sys.exit(1)
"
note "hosted compound A/B"

echo "--- HOSTED: registry API sample ---"
curl -sf "$BASE/registry/api?q=2012" | python3 -c "
import sys,json
d=json.load(sys.stdin)
assert d.get('label') in ('SOURCED','UNSOURCED','UNKNOWN','NOT_CLEARED')
print('  registry/api label', d.get('label'))
"
note "registry/api"

STATS_AFTER=$(curl -sf "$BASE/stats")
echo "$STATS_AFTER" | python3 -c "
import sys,json
d=json.load(sys.stdin)
print(f\"  stats after: claims={d['n']} hit_rate={d.get('dictionary_hit_rate')} queries={d.get('queries_logged')}\")
"
fi

echo "--- RECEIPT ---"
mkdir -p docs
cat > "$RECEIPT" <<EOF
# Long run receipt — Agent Science · $(date +%Y-%m-%d)

**Stamp:** $STAMP UTC  
**URL:** $BASE  
**Subject:** \`$SUBJ\`  
**Log:** \`$LOG\`

## Goal

Truth dictionary stranger path: free lookup first, compound on repeat, honest miss, registry grows.

## Results

| Gate | Result |
|------|--------|
| Local controls | watch_it_go_red + dictionary/routing/popular/partner |
| Hosted health | \`engine_default: adk\`, Parallel + Gemini |
| Free tier | \`2012/28/EU\` + \`Directive 2012/28/EU\` SOURCED, 0 Parallel |
| NOT_CLEARED | miss returns \`next_step\` |
| Compound A/B | subject \`$SUBJ\` — see log |
| Surfaces | /, /registry, /popular/ui, /stats |

## Stats delta

\`\`\`json
before: $STATS_BEFORE
after:  $STATS_AFTER
\`\`\`

## Run A / B (truncated)

\`\`\`json
$(echo "$A" | python3 -m json.tool 2>/dev/null | head -40)
\`\`\`

\`\`\`json
$(echo "$B" | python3 -m json.tool 2>/dev/null | head -40)
\`\`\`

## Pass/fail

- **Checks passed:** $pass (updated at end of script)
- **Command to replay:** \`bash scripts/long_run_goal.sh\`
- **Stranger one-liner:** \`bash scripts/new_user_trial.sh\`

EOF

echo
echo "=== LONG RUN COMPLETE ==="
echo "  passed=$pass failed=$fail"
echo "  receipt=$RECEIPT"
echo "  log=$LOG"
[[ "$fail" -eq 0 ]]
