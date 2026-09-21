#!/usr/bin/env python3
"""RUNG 1 — is the compounding claim true at scale, and in what units?

The pitch says "the second production about the same subject costs a fraction of the
first". That has never been measured on the FACT leg. This measures it, on two scripts
about the same subject, written independently of each other and of any source.

Cost model, re-derived from fixtures/price-card/parallel.json (retrieved_at on
the card). Do not edit the USD figures here — change the card, then re-run.
Invoice truth is a different object: fixtures/billing/invoice.json.
"""
import json, sys, time, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import agent_science
from clearance import corpus

_ROOT = pathlib.Path(__file__).resolve().parent
_CARD = json.loads((_ROOT / "fixtures/price-card/parallel.json").read_text())
_PROC = _CARD["default_processor_for_agent_science"]
GEMINI_CALL = float(_CARD.get("gemini_flash_lite_usd_per_call_order_of_magnitude", 0.0001))
PARALLEL_CALL = float(_CARD["search_api_usd_per_request"][_PROC])
SUBJECT = "orphan-works"


def run(name, path):
    t0 = time.monotonic()
    r = agent_science.clear_script(pathlib.Path(path).read_text(),
                                   subject=SUBJECT, model="gemini-3.5-flash-lite")
    dt = time.monotonic() - t0
    n = len(r["rows"])
    pc, ch = r["parallel_calls"], r["corpus_hits"]
    # one extract + roughly one locate per non-cached claim
    gemini = 1 + (n - ch)
    cost = gemini * GEMINI_CALL + pc * PARALLEL_CALL
    print(f"\n=== {name} ({pathlib.Path(path).name}) ===")
    print(f"  claims            {n}")
    print(f"  corpus hits       {ch}  ({ch/n:.0%})" if n else "")
    print(f"  parallel searches {pc}")
    print(f"  gemini calls      ~{gemini}")
    print(f"  wall clock        {dt:.1f}s")
    print(f"  est. cost         ${cost:.4f}")
    return {"name": name, "claims": n, "hits": ch, "parallel": pc,
            "gemini": gemini, "secs": dt, "cost": cost, "rows": r["rows"]}


if __name__ == "__main__":
    fresh = "--fresh" in sys.argv
    if fresh:
        db = corpus.DB
        if db.exists():
            db.unlink()
            print(f"corpus cleared: {db}")
    if "--powered" in sys.argv:
        # The experiment as originally specified: enough claims that two hits either
        # way cannot swing the result twenty points. The small-subject version was
        # under-powered before it was ever wrong, and three corrections came out of it.
        pa = "fixtures/scripts/powered-A-law.txt"
        pb = "fixtures/scripts/powered-B-archive.txt"
    else:
        pa = "fixtures/scripts/documentary-orphan-works.txt"
        pb = "fixtures/scripts/documentary-orphan-works-B.txt"
    a = run("PRODUCTION 1", pa)
    b = run("PRODUCTION 2 (same subject, different script)", pb)
    print("\n" + "=" * 62)
    print("# COMPOUNDING")
    print(f"  production 1  ${a['cost']:.4f}  {a['secs']:.0f}s  {a['hits']}/{a['claims']} from memory")
    print(f"  production 2  ${b['cost']:.4f}  {b['secs']:.0f}s  {b['hits']}/{b['claims']} from memory")
    if a["cost"]:
        print(f"  saving        {1 - b['cost']/a['cost']:+.0%} cost, "
              f"{1 - b['secs']/a['secs']:+.0%} wall clock")
    print(f"\n  cache-hit rate on production 2: {b['hits']}/{b['claims']}"
          f" = {(b['hits']/b['claims'] if b['claims'] else 0):.0%}")
