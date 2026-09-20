#!/usr/bin/env bash
# Watch hosted /health partner proof — RED until Oscar deploy, GREEN after.
#
# Default EXPECT_STATE=red documents the known strip on revision 00028-hed:
# exit 0 only when partner fields are STILL missing (control watched red).
# After deploy: EXPECT_STATE=green (or omit after flipping default) requires
# full partner health — same assertions as verify_partners_hosted.sh step 1.
#
# Usage:
#   bash scripts/watch_hosted_partner_health.sh              # expect RED (pre-deploy)
#   EXPECT_STATE=green bash scripts/watch_hosted_partner_health.sh
#   bash scripts/watch_hosted_partner_health.sh https://…
set -euo pipefail
BASE="${1:-https://agent-science-568004190078.us-central1.run.app}"
EXPECT_STATE="${EXPECT_STATE:-red}"
STAMP="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

echo "=== Hosted partner health watch === stamp=$STAMP expect=$EXPECT_STATE"
echo "URL: $BASE/health"

HEALTH_JSON="$(curl -sf "$BASE/health")" || {
  echo "FAIL: curl /health failed"
  exit 1
}
echo "$HEALTH_JSON" | python3 -m json.tool

python3 -c "
import json, os, sys
d = json.loads(sys.argv[1])
expect = sys.argv[2]
partner_keys = ('gemini', 'parallel', 'agent_builder', 'engine_default')
present = all(k in d and d.get(k) is not None for k in partner_keys)
stripped = set(d.keys()) <= {'ok', 'service', 'mode', 'revision'} or not present
print('keys=', sorted(d))
print('partner_fields_present=', present)
print('looks_stripped=', stripped)
print('revision=', d.get('revision'))
if expect == 'red':
    assert stripped or d.get('gemini') is None, (
        'expected RED (stripped/missing partner fields); got full partner health — '
        'flip EXPECT_STATE=green if Oscar already deployed'
    )
    print('WATCH RED OK — partner proof still absent on live (known defect until deploy)')
elif expect == 'green':
    req = {
        'ok': True,
        'gemini': True,
        'parallel': True,
        'agent_builder': True,
        'engine_default': 'adk',
    }
    for k, v in req.items():
        got = d.get(k)
        assert got == v, f'{k}: expected {v!r}, got {got!r}'
    path = d.get('gemini_path') or ''
    assert path.startswith('vertex:') or path == 'api-key', path
    print('WATCH GREEN OK — partner proof present')
else:
    raise SystemExit(f'unknown EXPECT_STATE={expect!r} (use red|green)')
" "$HEALTH_JSON" "$EXPECT_STATE"
