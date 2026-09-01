#!/usr/bin/env python3
"""Generate cue-aligned voiceover with edge-tts when Kokoro is unavailable."""
from __future__ import annotations

import asyncio
import pathlib
import subprocess
import sys

import edge_tts

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from film.lay_voice import CUES, OUT, PARTS, dur  # noqa: E402

VOICE = "en-US-GuyNeural"
RATE = "+15%"


async def synth_one(text: str, out: pathlib.Path) -> None:
    await edge_tts.Communicate(text, VOICE, rate=RATE).save(str(out))


async def main_async() -> None:
    parts = sorted(PARTS.glob("p*.txt"))
    if len(parts) != len(CUES):
        raise SystemExit(f"{len(parts)} parts vs {len(CUES)} cues")
    for p in parts:
        body = [ln for ln in p.read_text().splitlines() if not ln.startswith("@") and ln.strip()]
        text = " ".join(body)
        mp3 = p.with_suffix(".mp3")
        await synth_one(text, mp3)
        print(f"synth {mp3.name}  {dur(mp3):.1f}s")


def main() -> int:
    asyncio.run(main_async())
    subprocess.run(["python3", "film/lay_voice.py"], check=True)
    print(f"WROTE {OUT}  {dur(OUT):.1f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
