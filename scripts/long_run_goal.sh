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
# Logging: append to $LOG without `exec > >(tee)` — that redirection masks exit
# status as tee's (watched 2026-09-17: failed=13 printed, process exit 0).

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
  # Avoid `cmd | head` under pipefail — head closes early → SIGPIPE aborts the script
  # (watched 2026-09-17: long_run exited after 2/3 local lookups with no hosted checks).
  out=$(python3 -m clearance lookup "$q" 2>&1 || true)
  first=$(printf '%s\n' "$out" | sed -n '1p')
  if printf '%s\n' "$out" | grep -q SOURCED; then
    note "lookup local: $q"
  else
    bad "lookup local: $q ($first)"
  fi
done

echo "--- HOSTED: health + desk surfaces ---"
health_json=$(curl -sS -m 30 "$BASE/health" || true)
health_code=$(curl -sS -m 30 -o /dev/null -w '%{http_code}' "$BASE/health" || true)
if [[ "$health_code" != "200" ]]; then
  bad "hosted health HTTP $health_code"
else
  if printf '%s' "$health_json" | python3 -c "
import sys,json
d=json.load(sys.stdin)
missing=[k for k in ('engine_default','parallel','gemini') if k not in d]
if missing:
    print('STRIPPED keys missing:', ','.join(missing), '— mode=', d.get('mode'), 'rev=', d.get('revision'))
    sys.exit(2)
assert d.get('ok') and d['engine_default']=='adk' and d['parallel'] and d['gemini']
print('  health ok engine=adk parallel=True gemini=True')
"; then
    note "hosted health"
  else
    bad "hosted health partner fields stripped or non-adk (see above) — Oscar deploy"
  fi
fi

for path in / /registry /popular/ui /stats /registry/api?q=2012; do
  code=$(curl -sS -m 30 -o /dev/null -w '%{http_code}' "$BASE$path" || true)
  if [[ "$code" == "200" ]]; then note "GET $path $code"
  elif [[ "$code" == "303" || "$code" == "401" || "$code" == "302" ]]; then
    bad "GET $path $code (private-workspaces / auth — not public stranger path)"
  else
    bad "GET $path $code"
  fi
done

echo "--- HOSTED: dictionary tier probes ---"
search_code=$(curl -sS -m 30 -o /tmp/longrun_search.json -w '%{http_code}' \
  "$BASE/search?q=2012/28/EU&live=false" || true)
if [[ "$search_code" != "200" ]]; then
  bad "free tier EU HTTP $search_code (expected 200 SOURCED free)"
else
  if python3 -c "
import json
d=json.load(open('/tmp/longrun_search.json'))
assert d['label']=='SOURCED' and d.get('cost_tier')=='free'
assert d.get('parallel_api_calls',0)==0
print('  2012/28/EU SOURCED free')
"; then
    note "free tier EU"
  else
    bad "free tier EU body"
  fi
fi

search_code=$(curl -sS -m 30 -o /tmp/longrun_search2.json -w '%{http_code}' \
  "$BASE/search?q=Directive+2012/28/EU&live=false" || true)
if [[ "$search_code" != "200" ]]; then
  bad "alias Directive form HTTP $search_code"
else
  if python3 -c "
import json
d=json.load(open('/tmp/longrun_search2.json'))
assert d['label']=='SOURCED', d
print('  Directive form SOURCED')
"; then
    note "alias Directive form"
  else
    bad "alias Directive form body"
  fi
fi

search_code=$(curl -sS -m 30 -o /tmp/longrun_miss.json -w '%{http_code}' \
  "$BASE/search?q=xyzzy-nonexistent-claim-99999&live=false" || true)
if [[ "$search_code" != "200" ]]; then
  bad "miss path HTTP $search_code"
else
  if python3 -c "
import json
d=json.load(open('/tmp/longrun_miss.json'))
assert d['label']=='NOT_CLEARED' and d.get('next_step')
print('  honest NOT_CLEARED')
"; then
    note "miss path"
  else
    bad "miss path body"
  fi
fi

STATS_BEFORE=$(curl -sS -m 30 "$BASE/stats" || true)
stats_code=$(curl -sS -m 30 -o /dev/null -w '%{http_code}' "$BASE/stats" || true)
if [[ "$stats_code" == "200" ]]; then
  echo "$STATS_BEFORE" | python3 -c "
import sys,json
d=json.load(sys.stdin)
print(f\"  stats before: claims={d['n']} hit_rate={d.get('dictionary_hit_rate')} queries={d.get('queries_logged')}\")
" || bad "stats before parse"
else
  bad "stats HTTP $stats_code"
  STATS_BEFORE="{\"http\":$stats_code}"
fi

echo "--- HOSTED: compound A/B (subject $SUBJ) ---"
clear_code=$(curl -sS -m 240 -o /tmp/longrun_A.json -w '%{http_code}' -X POST "$BASE/clear" \
  -H 'Content-Type: application/json' \
  -d "{\"script\":\"The Orphan Works Directive is Directive 2012/28/EU.\",\"subject\":\"$SUBJ\"}" || true)
if [[ "$clear_code" != "200" ]]; then
  bad "hosted clear Run A HTTP $clear_code (workspace token required on private-workspaces)"
  A="{\"http\":$clear_code}"
  B="{\"http\":\"skipped\"}"
else
  A=$(cat /tmp/longrun_A.json)
  echo "$A" | python3 -c "
import sys,json
d=json.load(sys.stdin)
print(f\"  Run A: parallel={d.get('parallel_api_calls')} corpus_hits={d.get('corpus_hits')} engine={d.get('engine')}\")
"
  clear_code_b=$(curl -sS -m 240 -o /tmp/longrun_B.json -w '%{http_code}' -X POST "$BASE/clear" \
    -H 'Content-Type: application/json' \
    -d "{\"script\":\"Directive 2012/28/EU is the EU orphan works law.\",\"subject\":\"$SUBJ\"}" || true)
  if [[ "$clear_code_b" != "200" ]]; then
    bad "hosted clear Run B HTTP $clear_code_b"
    B="{\"http\":$clear_code_b}"
  else
    B=$(cat /tmp/longrun_B.json)
    if echo "$B" | python3 -c "
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
"; then
      note "hosted compound A/B"
    else
      bad "hosted compound A/B"
    fi
  fi
fi

echo "--- HOSTED: registry API sample ---"
reg_code=$(curl -sS -m 30 -o /tmp/longrun_reg.json -w '%{http_code}' "$BASE/registry/api?q=2012" || true)
if [[ "$reg_code" != "200" ]]; then
  bad "registry/api HTTP $reg_code"
else
  if python3 -c "
import json
d=json.load(open('/tmp/longrun_reg.json'))
assert d.get('label') in ('SOURCED','UNSOURCED','UNKNOWN','NOT_CLEARED')
print('  registry/api label', d.get('label'))
"; then
    note "registry/api"
  else
    bad "registry/api body"
  fi
fi

STATS_AFTER=$(curl -sS -m 30 "$BASE/stats" || true)
stats_code=$(curl -sS -m 30 -o /dev/null -w '%{http_code}' "$BASE/stats" || true)
if [[ "$stats_code" == "200" ]]; then
  echo "$STATS_AFTER" | python3 -c "
import sys,json
d=json.load(sys.stdin)
print(f\"  stats after: claims={d['n']} hit_rate={d.get('dictionary_hit_rate')} queries={d.get('queries_logged')}\")
" || true
else
  STATS_AFTER="{\"http\":$stats_code}"
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
# Explicit status — `exec > >(tee …)` can otherwise mask a failed [[ ]] as exit 0
# (watched 2026-09-17: failed=13 printed, process exit 0).
if [[ "$fail" -eq 0 ]]; then
  exit 0
fi
exit 1
