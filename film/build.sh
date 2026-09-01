#!/usr/bin/env bash
# Rebuild demo/demo-final.mp4 — flipbook picture + Kokoro voiceover.
#   ./film/build.sh           # full build
#   ./film/build.sh --silent  # picture only
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
FLIPBOOK="${FLIPBOOK_ROOT:-$HOME/CODE/flipbook}"
cd "$ROOT"

SILENT=0
[ "${1:-}" = "--silent" ] && SILENT=1

echo "=== Agent Science film build ==="

# shellcheck source=film/numbers.env
source "$ROOT/film/numbers.env"

mkdir -p demo

render_picture() {
  if [ -x "$FLIPBOOK/bin/flipbook" ] && [ -f "$FLIPBOOK/examples/agent-science.json" ]; then
    echo "1/5 · sync screenshots → flipbook assets"
    mkdir -p "$FLIPBOOK/examples/assets/agent-science"
    cp -f "$ROOT/docs/assets/screens/"*.png "$FLIPBOOK/examples/assets/agent-science/"
    echo "2/5 · flipbook render (16x9)"
    "$FLIPBOOK/bin/flipbook" audit "$FLIPBOOK/examples/agent-science.json" || true
    "$FLIPBOOK/bin/flipbook" render "$FLIPBOOK/examples/agent-science.json" --aspect 16x9
    cp -f "$FLIPBOOK/out/agent-science/agent-science-16x9.mp4" demo/seg-flipbook.mp4
  else
    echo "1/5 · flipbook sibling missing — HTML reel fallback"
    python3 film/render_reel.py
    echo "2/5 · seg-flipbook.mp4 from render_reel.py"
  fi
}

render_picture

if [ "$SILENT" = "1" ]; then
  cp demo/seg-flipbook.mp4 demo/demo-silent.mp4
  echo "WROTE demo/demo-silent.mp4"
  exit 0
fi

echo "3/5 · Kokoro voice (local)"
python3 film/split_voice.py
VO_PY="${VOICE_GEN:-$HOME/CODE/voice-generation}/kvenv/bin/python"
if [ ! -x "$VO_PY" ]; then
  echo "MISSING Kokoro at $VO_PY — mux existing voiceover.mp3" >&2
  if [ ! -f demo/voiceover.mp3 ]; then
    echo "ERROR: no demo/voiceover.mp3 to mux" >&2
    exit 1
  fi
else
  VO_SCRIPT="${VOICE_GEN:-$HOME/CODE/voice-generation}/vo.py"
  for f in demo/.vo-parts/p*.txt; do
    abs="$(cd "$(dirname "$f")" && pwd)/$(basename "$f")"
    ( cd "${VOICE_GEN:-$HOME/CODE/voice-generation}" && \
      "$VO_PY" vo.py "$abs" -o "${abs%.txt}.mp3" --preset demo --speed 1.35 )
  done
  echo "4/5 · lay voice on cues"
  python3 film/lay_voice.py
fi

echo "5/5 · mux"
ffmpeg -y -loglevel error -i demo/seg-flipbook.mp4 -i demo/voiceover.mp3 \
  -map 0:v -map 1:a -c:v copy -c:a aac -b:a 160k -shortest demo/demo-final.mp4

DUR="$(ffprobe -v error -show_entries format=duration -of csv=p=0 demo/demo-final.mp4)"
echo
echo "WROTE demo/demo-final.mp4  ${DUR}s"
if python3 -c "import sys; sys.exit(0 if float('${DUR}') <= ${VIDEO_CAP_SEC} else 1)"; then
  echo "OK: under ${VIDEO_CAP_SEC}s cap"
else
  echo "WARN: over ${VIDEO_CAP_SEC}s — trim for Devpost" >&2
fi
cp -f demo/demo-final.mp4 submission/demo-final.mp4 2>/dev/null || true
