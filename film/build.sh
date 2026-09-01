#!/usr/bin/env bash
# Rebuild demo/demo-final.mp4 — flipbook picture + Kokoro voiceover.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
FLIPBOOK="${FLIPBOOK_ROOT:-$HOME/CODE/flipbook}"
cd "$ROOT"

SILENT=0
[ "${1:-}" = "--silent" ] && SILENT=1

echo "=== Agent Science film build ==="
source "$ROOT/film/numbers.env"

echo "1/6 · refresh hosted screenshots"
python3 scripts/capture_screens.py

echo "2/6 · sync screenshots → flipbook assets"
mkdir -p "$FLIPBOOK/examples/assets/agent-science"
cp -f "$ROOT/docs/assets/screens/"*.png "$FLIPBOOK/examples/assets/agent-science/"

echo "3/6 · purge stale flipbook output (scout reel cache)"
rm -rf "$FLIPBOOK/out/agent-science" "$ROOT/out/agent-science"

echo "4/6 · flipbook render (16x9)"
( cd "$FLIPBOOK" && ./bin/flipbook audit examples/agent-science.json ) || true
( cd "$FLIPBOOK" && ./bin/flipbook render examples/agent-science.json --aspect 16x9 )
FB_MP4="$FLIPBOOK/out/agent-science/agent-science-16x9.mp4"
FB_HTML="$FLIPBOOK/out/agent-science/agent-science.html"
[ -f "$FB_MP4" ] || FB_MP4="$ROOT/out/agent-science/agent-science-16x9.mp4"
[ -f "$FB_HTML" ] || FB_HTML="$ROOT/out/agent-science/agent-science.html"
mkdir -p demo
cp -f "$FB_MP4" demo/seg-flipbook.mp4

# Verify hook — HTML must be truth-layer, not scout
if [ -f "$FB_HTML" ] && rg -q 'documentary needs two reports|SCOUT' "$FB_HTML"; then
  echo "FAIL: flipbook HTML still scout reel" >&2
  exit 1
fi
if [ -f "$FB_HTML" ] && ! rg -q 'websearches' "$FB_HTML"; then
  echo "FAIL: flipbook HTML missing truth-layer hook" >&2
  exit 1
fi

if [ "$SILENT" = "1" ]; then
  cp demo/seg-flipbook.mp4 demo/demo-silent.mp4
  echo "WROTE demo/demo-silent.mp4"
  exit 0
fi

echo "5/6 · Kokoro voice (local)"
python3 film/split_voice.py
VO_PY="${VOICE_GEN:-$HOME/CODE/voice-generation}/kvenv/bin/python"
if [ ! -x "$VO_PY" ]; then
  echo "MISSING Kokoro — picture-only fallback" >&2
  cp demo/seg-flipbook.mp4 demo/demo-final.mp4
  exit 0
fi
for f in demo/.vo-parts/p*.txt; do
  abs="$(cd "$(dirname "$f")" && pwd)/$(basename "$f")"
  ( cd "${VOICE_GEN:-$HOME/CODE/voice-generation}" && \
    "$VO_PY" vo.py "$abs" -o "${abs%.txt}.mp3" --preset demo --speed 1.35 )
done

echo "6/6 · lay voice + mux"
python3 film/lay_voice.py
ffmpeg -y -loglevel error -i demo/seg-flipbook.mp4 -i demo/voiceover.mp3 \
  -map 0:v -map 1:a -c:v copy -c:a aac -b:a 160k -shortest demo/demo-final.mp4

DUR="$(ffprobe -v error -show_entries format=duration -of csv=p=0 demo/demo-final.mp4)"
echo "WROTE demo/demo-final.mp4  ${DUR}s"
cp -f demo/demo-final.mp4 submission/demo-final.mp4 2>/dev/null || true
