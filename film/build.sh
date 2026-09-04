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

# --- STORY GUARD, added 2026-09-04 ---
# This script builds the film from demo/voiceover.txt and docs/assets/screens/*.png.
# It has NEVER read docs/film/. The Sep 3 film pack (7 beat screenshots plus a
# 6 beat voiceover) is orphaned from this pipeline, so running this script
# reproduces the OLD Sep 1 story against the NEW script. Fail loudly instead.
#
# Repointing this script alone does NOT fix it. The scene-to-image mapping lives
# in a DIFFERENT repo: $FLIPBOOK/examples/agent-science.json, which hardcodes 7
# filenames from docs/assets/screens and 11 scenes cut to the Sep 1 script.
# Fixing the story means editing that JSON too. That is out of this repo.
if ! diff -q "$ROOT/demo/voiceover.txt" "$ROOT/docs/film/voiceover.txt" >/dev/null 2>&1; then
  cat >&2 <<'GUARD'
=== FILM BUILD BLOCKED: story drift ===
demo/voiceover.txt (what this script renders) does not match
docs/film/voiceover.txt (the current story, 6 beats, 2026-09-03).

Building now would ship the superseded Sep 1 film.

To fix, in this order:
  1. Update $FLIPBOOK/examples/agent-science.json to the current beats and to the
     screenshots in docs/film/. It presently hardcodes 7 names from docs/assets/screens.
  2. Sync docs/film/ screenshots into docs/assets/screens, or repoint step 2/6 below.
  3. cp docs/film/voiceover.txt demo/voiceover.txt
  4. Re-run this script.

To build the OLD film deliberately, anyway:
  FILM_ALLOW_STALE=1 bash film/build.sh
GUARD
  [ "${FILM_ALLOW_STALE:-0}" = "1" ] || exit 1
  echo "WARNING: FILM_ALLOW_STALE=1 set, building the SUPERSEDED story on purpose." >&2
fi
# --- end STORY GUARD ---

echo "1/6 · refresh hosted screenshots"
python3 scripts/capture_screens.py

echo "2/6 · sync screenshots → flipbook assets"
mkdir -p "$FLIPBOOK/examples/assets/agent-science"
cp -f "$ROOT/docs/assets/screens/"*.png "$FLIPBOOK/examples/assets/agent-science/"

echo "3/6 · purge stale flipbook output (scout reel cache)"
rm -rf "$FLIPBOOK/out/agent-science" "$ROOT/out/agent-science"

echo "4/6 · flipbook render (16x9)"
( cd "$FLIPBOOK" && ./bin/flipbook audit examples/agent-science.json ) || true
# VERIFY GATE, added 2026-09-04. `audit || true` cannot fail the build and
# cannot see the world. verify exercises the row hash binding and exits 1 on drift,
# so it is the only thing standing between a stale asset and a rendered film.
# It was never run by this script before today.
( cd "$FLIPBOOK" && ./bin/flipbook verify examples/agent-science.json --run-commands ) || {
  echo "FAIL: flipbook verify reported drift. The reel does not match its declared sources." >&2
  echo "  Run: ( cd $FLIPBOOK && ./bin/flipbook verify examples/agent-science.json --run-commands )" >&2
  exit 1
}
( cd "$FLIPBOOK" && ./bin/flipbook render examples/agent-science.json --aspect 16x9 )
FB_MP4="$FLIPBOOK/out/agent-science/agent-science-16x9.mp4"
[ -f "$FB_MP4" ] || FB_MP4="$ROOT/out/agent-science/agent-science-16x9.mp4"
if [ ! -f "$FB_MP4" ]; then
  echo "FAIL: flipbook render produced no mp4 at either candidate path." >&2
  echo "  tried $FLIPBOOK/out/agent-science/agent-science-16x9.mp4" >&2
  echo "  tried $ROOT/out/agent-science/agent-science-16x9.mp4" >&2
  exit 1
fi
mkdir -p demo
cp -f "$FB_MP4" demo/seg-flipbook.mp4

# --- PICTURE GUARD, replaces two dead hooks, 2026-09-04 ---
# REMOVED: two HTML content hooks that had never executed once. They read
# $FLIPBOOK/out/agent-science/agent-science.html, which `flipbook render` never
# writes; HTML comes from the separate `flipbook html` command and is named
# <name>-<aspect>.html. Both were wrapped in [ -f "$FB_HTML" ], so both skipped
# silently and printed nothing, which is worse than no guard because the build
# looked checked. One of them also required the word "websearches", which appears
# in the superseded Sep 1 script and NOT in the current story: repairing the path
# alone would have turned a silent no-op into a hard failure on the new film.
#
# What they were for was "the picture is the wrong reel". This replaces that with
# a check on an object that exists, and it runs on every build. The script's own
# final beat header declares the end time, so the picture is checked against the
# same single source the cues come from.
STORY="$ROOT/docs/film/voiceover.txt"
DECLARED_END="$(sed -n 's/.*to \([0-9]\{1,\}\):\([0-5][0-9]\)).*/\1 \2/p' "$STORY" | tail -1 \
  | awk '{print $1 * 60 + $2}')"
PIC_DUR="$(ffprobe -v error -show_entries format=duration -of csv=p=0 demo/seg-flipbook.mp4)"
if [ -n "$DECLARED_END" ]; then
  awk -v pic="$PIC_DUR" -v want="$DECLARED_END" -v fb="$FLIPBOOK" -v story="$STORY" 'BEGIN{
    d = pic - want; if (d < 0) d = -d;
    if (d > 2) {
      printf "FAIL: picture is %.1fs but the script declares %ds. Off by %.1fs.\n", pic, want, d > "/dev/stderr";
      printf "  The rendered reel does not match the current story.\n" > "/dev/stderr";
      printf "  Check %s/examples/agent-science.json against %s\n", fb, story > "/dev/stderr";
      exit 1
    }
    printf "picture %.1fs matches declared %ds\n", pic, want;
  }' || exit 1
else
  echo "WARNING: no declared end time found in $STORY, picture not checked." >&2
fi
# --- end PICTURE GUARD ---

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
