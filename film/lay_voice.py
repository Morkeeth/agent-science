"""Lay narration onto flipbook reel beat times (agent-science.json scene starts)."""
import pathlib
import subprocess

PARTS = pathlib.Path("demo/.vo-parts")
OUT = pathlib.Path("demo/voiceover.mp3")
SR = 24000

# Scene start seconds from flipbook/examples/agent-science.json (cumulative)
CUES = {
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


def main():
    parts = sorted(PARTS.glob("p*.mp3"))
    if len(parts) != len(CUES):
        raise SystemExit(f"{len(parts)} parts vs {len(CUES)} cues — run split_voice + Kokoro first")
    inputs, filters, labels = [], [], []
    for i, p in enumerate(parts):
        inputs += ["-i", str(p)]
        delay = int(CUES[i] * 1000)
        filters.append(f"[{i}:a]aresample={SR},adelay={delay}|{delay}[a{i}]")
        labels.append(f"[a{i}]")
    filters.append("".join(labels) + f"amix=inputs={len(parts)}:normalize=0,"
                   f"alimiter=level_in=1:level_out=0.95[out]")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *inputs,
                    "-filter_complex", ";".join(filters), "-map", "[out]",
                    "-c:a", "libmp3lame", "-b:a", "192k", str(OUT)], check=True)
    print(f"WROTE {OUT}  {dur(OUT):.1f}s")


if __name__ == "__main__":
    main()
