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

ok "hosted /health"
HEALTH="$(curl -sS --max-time 20 "$HOSTED_URL/health" || true)"
echo "$HEALTH" | python3 -c "import json,sys; d=json.load(sys.stdin); assert d.get('ok') and d.get('engine_default')=='adk'" \
  || red "/health bad"

ok "hosted /visibility/ui"
curl -sf --max-time 20 "$VISIBILITY_URL" | grep -q Transparency || red "visibility UI missing Transparency pane"

ok "hosted /truths/ui"
curl -sf --max-time 20 "$TRUTHS_URL" | grep -q "Truths dashboard" || red "truths ui down"

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
