"""Review-lane receipt: corpus compounding claim from PITCH.md §2.

Reproduces: Run 1 stores N verdicts; Run 2 recalls all N with zero network.
Uses europeana-film-archive.json (50 items) — the denominator PITCH implies.
"""
from __future__ import annotations

import os
import sys
import tempfile
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from clearance import corpus, engine
from clearance.sources import europeana


def main() -> int:
    items = europeana.load_fixture("europeana-film-archive.json")
    n = len(items)
    use = engine.AI_TRAINING

    tdb = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    tdb.close()
    con = corpus.connect(tdb.name)

    reused_run1 = 0
    for it in items:
        hit = corpus.recall(con, it["subject_id"], use)
        if hit:
            reused_run1 += 1
        v = engine.judge(
            subject_id=it["subject_id"],
            subject_title=it["subject_title"],
            instrument_uri=it["instrument_uri"],
            use=use,
            holder=it["holder"],
        )
        corpus.remember(con, [v])

    calls: list[int] = []
    real_urlopen = urllib.request.urlopen

    def tripwire(*_a, **_kw):
        calls.append(1)
        raise AssertionError("network touched on corpus recall run")

    urllib.request.urlopen = tripwire
    reused_run2 = 0
    try:
        for it in items:
            hit = corpus.recall(con, it["subject_id"], use)
            if hit:
                reused_run2 += 1
            else:
                engine.judge(
                    subject_id=it["subject_id"],
                    subject_title=it["subject_title"],
                    instrument_uri=it["instrument_uri"],
                    use=use,
                    holder=it["holder"],
                )
    finally:
        urllib.request.urlopen = real_urlopen
        os.unlink(tdb.name)

    print(f"fixture: europeana-film-archive.json ({n} items)")
    print(f"run 1 reused: {reused_run1}/{n} (expect 0/{n} on empty corpus)")
    print(f"run 2 reused: {reused_run2}/{n} (expect {n}/{n})")
    print(f"run 2 network calls: {len(calls)} (expect 0)")

    ok = reused_run1 == 0 and reused_run2 == n and len(calls) == 0
    print("PITCH compounding claim:", "VERIFIED" if ok else "FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
