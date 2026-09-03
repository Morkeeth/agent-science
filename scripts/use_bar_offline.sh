#!/usr/bin/env bash
# Stranger use-bar path — cold, no key, no network required for core checks.
# Usage: bash scripts/use_bar_offline.sh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

export AGENT_SCIENCE_RECEIPTS="${AGENT_SCIENCE_RECEIPTS:-$ROOT/cache/session_receipts.jsonl}"
# Isolate from hosted pollution for this smoke
TMPDB=$(mktemp -d)/refusal_log.db
export REFUSAL_LOG_DB="$TMPDB"

echo "=== use-bar offline (no key) ==="
echo "receipts: $AGENT_SCIENCE_RECEIPTS"
echo "db: $REFUSAL_LOG_DB"

# Boot minimal shelf from corpus if available
if [[ -f scripts/boot_registry.py ]]; then
  python3 scripts/boot_registry.py >/tmp/use_bar_boot.txt 2>&1 || true
fi

echo "1. intercept free lookup"
python3 -m clearance.stack_cli use-bar "2012/28/EU" --traffic human --json | python3 -c "
import sys,json
d=json.load(sys.stdin)
print('  label', d.get('label'), 'tier', d.get('cost_tier'), 'receipt', d.get('receipt_id'))
assert d.get('receipt_id'), d
assert d.get('label') in ('SOURCED','NOT_CLEARED','UNSOURCED','UNKNOWN','CONTRARY_TO_RESEARCH'), d
"

echo "2. intercept gate probe (must refuse, no cite)"
python3 -m clearance.stack_cli use-bar "xyzzy-nonexistent-claim-99999" --traffic gate --json | python3 -c "
import sys,json
d=json.load(sys.stdin)
print('  label', d.get('label'), 'traffic', d.get('traffic'), 'cite', d.get('citation_url'))
assert d.get('label')=='NOT_CLEARED', d
assert not d.get('citation_url'), d
"

echo "3. receipt assert"
python3 - <<'PY'
from clearance import use_path
use_path.assert_receipt_exists("2012/28/EU")
print("  receipt OK for 2012/28/EU")
print(use_path.use_bar_summary(limit=5))
PY

echo "4. traffic unit + use_path tests"
python3 tests/test_traffic_class.py
python3 tests/test_use_path.py

echo "5. baseline arms (may embarrass)"
USE_PATH_EVAL_OFFLINE=1 python3 scripts/eval_use_path_baseline.py | python3 -c "
import sys,json
d=json.load(sys.stdin)
print('  winner', d['winner'], '·', d['finding'])
print('  ranking', d['ranking'])
"

echo
echo "=== use-bar offline OK ==="
echo "Next for Cursor: docs/USE-BAR-PATH-2026-09-04.md"
echo "Oscar fills: docs/SESSION-RECEIPT-TEMPLATE.md — do not claim daily use without it"
