#!/usr/bin/env python3
"""The compounding CURVE — the powered experiment, reached the only way available.

The brief said 50-100 claims. Writing longer scripts does not get there: the extractor
caps at roughly 10 claims per script regardless of length (388 words carrying ~35
checkable assertions yielded 10). So the power comes from MORE SCRIPTS, not bigger ones.

Four independently written scripts on one subject, run in sequence into one corpus.
Each leg writes its result before the next starts, so a kill costs one leg. What this
measures is the shape a buyer actually experiences: does the Nth production about a
subject cost less than the first?
"""
import json, pathlib, sys, time
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import agent_science
from clearance import corpus, search as _search

GEMINI_CALL, PARALLEL_CALL = 0.0001, 0.005
SUBJECT = "curve"
OUT = pathlib.Path("fixtures/compounding/curve")
SCRIPTS = [
    "fixtures/scripts/powered-A-law.txt",
    "fixtures/scripts/documentary-orphan-works.txt",
    "fixtures/scripts/powered-B-archive.txt",
    "fixtures/scripts/documentary-orphan-works-B.txt",
]

if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    if "--fresh" in sys.argv and corpus.DB.exists():
        corpus.DB.unlink()
    only = [a for a in sys.argv[1:] if a.isdigit()]
    for i, path in enumerate(SCRIPTS, 1):
        if only and str(i) not in only:
            continue
        dest = OUT / f"leg{i}.json"
        if dest.exists() and "--force" not in sys.argv:
            print(f"leg {i} already measured, skipping", flush=True)
            continue
        _search.reset_calls()
        t0 = time.monotonic()
        r = agent_science.clear_script(pathlib.Path(path).read_text(),
                                       subject=SUBJECT, model="gemini-3.5-flash-lite")
        dt = time.monotonic() - t0
        n, ch = len(r["rows"]), r["corpus_hits"]
        res = {"leg": i, "script": pathlib.Path(path).name, "claims": n,
               "corpus_hits": ch, "hit_rate": round(ch / n, 3) if n else 0,
               "parallel_calls": _search.calls(), "seconds": round(dt, 1),
               "cost": round((1 + n - ch) * GEMINI_CALL + _search.calls() * PARALLEL_CALL, 4),
               "sourced": sum(1 for x in r["rows"] if x["label"] == "SOURCED")}
        dest.write_text(json.dumps(res, indent=2))
        print(json.dumps(res), flush=True)
