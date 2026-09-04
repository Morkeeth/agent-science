"""Lay narration onto the cue times the film script itself declares.

Cues come from demo/.vo-parts/cues.json, written by film/split_voice.py from the
beat headers in the script. One source, in the file a person edits.

LEGACY_CUES below is the dict this file used before 2026-09-04. It is kept only as
a fallback for an old script with no beat headers, and it is wrong for the current
story: its docstring claimed the values came from flipbook/examples/agent-science.json,
they were a third copy of the timeline in a different repo, and they had diverged.
The JSON reads 0, 10, 22, 32, 41, 51, 60, 68, 78, 86, 92; the dict reads 0.5, 10.5,
22, 34, 44, 53, 63, 72, 80, 90, 98, 104. They disagree from the fourth cue on.
Using it now prints a loud warning.
"""
import json
import pathlib
import subprocess
import sys

PARTS = pathlib.Path("demo/.vo-parts")
CUES_JSON = PARTS / "cues.json"
OUT = pathlib.Path("demo/voiceover.mp3")
SR = 24000

LEGACY_CUES = {
    0: 0.5,    # hook
    1: 10.5,   # truth layer intro
    2: 22.0,   # visibility
    3: 34.0,   # contrary
    4: 44.0,   # rule
    5: 53.0,   # sourced
    6: 63.0,   # refuse
    7: 72.0,   # honest marketing
    8: 80.0,   # compound
    9: 90.0,   # truths dashboard
    10: 98.0,  # partners
    11: 104.0, # close
}


def dur(p):
    return float(subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(p)], capture_output=True, text=True).stdout.strip())


def load_cues(n_parts):
    """One source: the cues the script declared. No silent guessing."""
    if CUES_JSON.exists():
        data = json.loads(CUES_JSON.read_text(encoding="utf-8"))
        cues = data.get("cues", [])
        if len(cues) != n_parts:
            raise SystemExit(
                f"{n_parts} rendered parts vs {len(cues)} cues in {CUES_JSON}. "
                f"Re-run film/split_voice.py, then re-render the parts.")
        missing = [i for i, c in enumerate(cues) if c is None]
        if missing:
            raise SystemExit(
                f"part(s) {missing} have no declared start time in {data.get('source')}. "
                f"Add a beat header like '# Beat 1, the refusal (0:20 to 0:55)'. "
                f"Refusing to guess a cue.")
        return {i: float(c) for i, c in enumerate(cues)}

    print(f"WARNING: {CUES_JSON} missing, falling back to LEGACY_CUES. "
          f"These are the pre-2026-09-04 values and are wrong for the current story.",
          file=sys.stderr)
    if n_parts != len(LEGACY_CUES):
        raise SystemExit(
            f"{n_parts} parts vs {len(LEGACY_CUES)} legacy cues. "
            f"Run film/split_voice.py to generate {CUES_JSON} from the script.")
    return dict(LEGACY_CUES)


def main():
    parts = sorted(PARTS.glob("p*.mp3"))
    if not parts:
        raise SystemExit(f"no rendered parts in {PARTS} — run split_voice + Kokoro first")
    cues = load_cues(len(parts))
    inputs, filters, labels = [], [], []
    for i, p in enumerate(parts):
        inputs += ["-i", str(p)]
        delay = int(cues[i] * 1000)
        filters.append(f"[{i}:a]aresample={SR},adelay={delay}|{delay}[a{i}]")
        labels.append(f"[a{i}]")
    filters.append("".join(labels) + f"amix=inputs={len(parts)}:normalize=0,"
                   f"alimiter=level_in=1:level_out=0.95[out]")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *inputs,
                    "-filter_complex", ";".join(filters), "-map", "[out]",
                    "-c:a", "libmp3lame", "-b:a", "192k", str(OUT)], check=True)
    d = dur(OUT)
    last_cue = max(cues.values())
    print(f"WROTE {OUT}  {d:.1f}s  (last cue {last_cue:.0f}s, "
          f"tail {d - last_cue:.1f}s)")


if __name__ == "__main__":
    main()
