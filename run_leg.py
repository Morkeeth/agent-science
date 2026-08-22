#!/usr/bin/env python3
"""One leg of the compounding experiment, written to disk as it completes.

Split from measure_compounding.py after a 25-minute two-leg run was killed and lost
everything. A long measurement that only records its result at the end is a measurement
you cannot afford to have interrupted - and the powered experiment is precisely the one
that takes long enough to be interrupted.
"""
import json, sys, pathlib, time
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import agent_science
from clearance import search as _search

GEMINI_CALL, PARALLEL_CALL = 0.0001, 0.005
OUT = pathlib.Path("fixtures/compounding")

if __name__ == "__main__":
    leg, path, subject = sys.argv[1], sys.argv[2], sys.argv[3]
    _search.reset_calls()
    t0 = time.monotonic()
    r = agent_science.clear_script(pathlib.Path(path).read_text(),
                                   subject=subject, model="gemini-3.5-flash-lite")
    dt = time.monotonic() - t0
    n, pc, ch = len(r["rows"]), r["parallel_calls"], r["corpus_hits"]
    gemini = 1 + (n - ch)
    res = {"leg": leg, "script": path, "claims": n, "corpus_hits": ch,
           "parallel_calls": pc, "gemini_calls": gemini, "seconds": round(dt, 1),
           "parallel_calls_true": _search.calls(),
           "cost": round(gemini * GEMINI_CALL + _search.calls() * PARALLEL_CALL, 4),
           "sourced": sum(1 for x in r["rows"] if x["label"] == "SOURCED")}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{leg}.json").write_text(json.dumps(res, indent=2))
    print(json.dumps(res, indent=2), flush=True)
