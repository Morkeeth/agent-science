#!/usr/bin/env bash
# Must exit 0 before recording or shipping demo-final.mp4
set -euo pipefail
FILM_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$FILM_DIR/.." && pwd)"
# shellcheck source=film/numbers.env
source "$FILM_DIR/numbers.env"
cd "$ROOT"
FAIL=0
red() { printf '\033[31mPREFLIGHT FAIL:\033[0m %s\n' "$*" >&2; FAIL=1; }
ok() { printf '\033[32mok:\033[0m %s\n' "$*"; }

ok "voiceover spine lines"
grep -q "CONTRARY" "$FILM_DIR/voiceover.txt" || red "missing CONTRARY in spine"
grep -q "$PARALLEL_A" "$FILM_DIR/voiceover.txt" || red "missing parallel A"
grep -q "$PARALLEL_B" "$FILM_DIR/voiceover.txt" || red "missing parallel B"

ok "hosted /health (partner fields — thin stub is a fail)"
# /health must stay on the configured host (no -L): partner fields are the object.
HEALTH="$(curl -sS --max-time 20 "$HOSTED_URL/health" || true)"
echo "$HEALTH" | python3 -c "
import json, sys
d = json.load(sys.stdin)
assert d.get('ok') and d.get('engine_default') == 'adk', d
assert d.get('parallel_sdk') is True, d
assert (d.get('gemini_path') or '').startswith('vertex:'), d
assert 'mode' in d, d
" || red "/health missing partner fields (redeploy required if live still thin)"

ok "hosted /partners (anonymous JSON — login HTML is a fail)"
PARTNERS="$(curl -sS --max-time 20 "$HOSTED_URL/partners" || true)"
echo "$PARTNERS" | python3 -c "
import json, sys
raw = sys.stdin.read()
assert not raw.lstrip().lower().startswith('<!doctype'), 'partners redirected to login HTML'
d = json.loads(raw)
tc = d.get('track_checklist') or {}
assert tc.get('partner_health_public') is True, d
assert tc.get('adk_agent_builder') is True, d
" || red "/partners not public partner JSON (redeploy required)"

ok "hosted public evidence demo (not the old visibility dashboard)"
# Private-workspace mode retired anonymous /visibility/ui + /truths/ui.
# Film the public judge demo + partner /health instead.
JUDGE_URL="${JUDGE_DEMO_URL:-$HOSTED_URL/judge/demo}"
curl -sfL --max-time 20 "$JUDGE_URL" | grep -q "Public read-only research example" \
  || red "hosted /judge/demo missing public evidence example"

ok "hosted visibility/truths stay local-only notices (no false film surface)"
curl -sfL --max-time 20 "$VISIBILITY_URL" | grep -q "local-only research route" \
  || red "hosted /visibility/ui must say local-only (do not film as transparency WOW)"
curl -sfL --max-time 20 "$TRUTHS_URL" | grep -q "local-only research route" \
  || red "hosted /truths/ui must say local-only (do not film as truths dashboard)"

if [ -f demo/demo-final.mp4 ]; then
  DUR="$(ffprobe -v error -show_entries format=duration -of csv=p=0 demo/demo-final.mp4)"
  ok "demo-final.mp4 exists (${DUR}s)"
  python3 -c "import sys; sys.exit(0 if float('$DUR') <= float('$VIDEO_CAP_SEC') else 1)" \
    || red "video over ${VIDEO_CAP_SEC}s cap"
else
  echo "  note: demo/demo-final.mp4 not built yet — run ./film/build.sh" >&2
fi

if [ "$FAIL" -ne 0 ]; then
  echo "PREFLIGHT FAILED" >&2
  exit 1
fi
echo
echo "PREFLIGHT PASS"
exit 0
