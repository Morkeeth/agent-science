"""Split the film script into one file per paragraph, and derive the cue times.

The script is the single source of both the narration and the timeline. Each beat
header declares its own start, for example `# Beat 1, the refusal (0:20 to 0:55)`,
so the cues come from the same file a person edits. Before 2026-09-04 the cues were
a hardcoded dict in film/lay_voice.py that named a JSON in another repo and had
silently diverged from it.

Two defects fixed here, both found 2026-09-04:

1. Paragraphs were joined into ONE line with " ".join. Every beat paragraph starts
   with a `#` header, so the joined line started with `#`, and vo.py drops lines
   starting with `#`. Every paragraph was dropped. vo.py exited "has no spoken
   lines" and the film rendered SILENT. Lines are now kept separate and `#` lines
   are stripped here, so per-line `| pause_ms | speed` markers survive.

2. A header-only paragraph (the production note at the top) produced an empty part.
   Paragraphs with no spoken line after stripping are now skipped.
"""
import json
import pathlib
import re
import sys

SRC = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "demo/voiceover.txt")
OUT = pathlib.Path("demo/.vo-parts")

# `# Beat 0, the problem (0:00 to 0:20)` -> 0.0
HEADER_TIME = re.compile(r"\((\d+):([0-5]\d)\s+to\s+\d+:[0-5]\d\)")


def start_seconds(header: str):
    m = HEADER_TIME.search(header)
    if not m:
        return None
    return int(m.group(1)) * 60 + int(m.group(2))


def main() -> int:
    raw = SRC.read_text(encoding="utf-8").split("\n")
    head = [l for l in raw if l.startswith("@")]

    # Group into paragraphs on blank lines, keeping every line separate.
    paras, cur = [], []
    for line in [l for l in raw if not l.startswith("@")]:
        if line.strip():
            cur.append(line)
        elif cur:
            paras.append(cur)
            cur = []
    if cur:
        paras.append(cur)

    OUT.mkdir(parents=True, exist_ok=True)
    for old in OUT.glob("p*"):
        old.unlink()
    cues_path = OUT / "cues.json"
    if cues_path.exists():
        cues_path.unlink()

    cues, kept, skipped = [], 0, 0
    for para in paras:
        headers = [l for l in para if l.lstrip().startswith("#")]
        spoken = [l for l in para if not l.lstrip().startswith("#")]
        if not spoken:
            skipped += 1
            continue  # production note, nothing to read
        cue = None
        for h in headers:
            cue = start_seconds(h)
            if cue is not None:
                break
        cues.append(cue)
        (OUT / f"p{kept:02d}.txt").write_text(
            "\n".join(head) + "\n\n" + "\n".join(spoken) + "\n", encoding="utf-8")
        kept += 1

    missing = [i for i, c in enumerate(cues) if c is None]
    if missing:
        print(f"WARNING: no declared start time on part(s) {missing}. "
              f"lay_voice will refuse rather than guess.", file=sys.stderr)
    cues_path.write_text(json.dumps(
        {"source": str(SRC), "cues": cues}, indent=1), encoding="utf-8")

    print(f"{kept} spoken paragraphs -> {OUT} ({skipped} header-only skipped)")
    print(f"cues from {SRC}: {cues}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
