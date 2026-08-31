#!/usr/bin/env python3
"""Run the wedge through the shipping engine and write the receipt the surface renders.

    python3 scripts/wedge_receipt.py

NETWORK: one fetch of the cited regulation (cached afterwards in cache/documents.json).
Two arms per case, because a refusal is only interesting beside the GREEN it replaced:

    BASE   the engine with the citation check OFF — what shipped at 04:00 on 2026-08-31
    SHIPS  the engine as it stands now

Every field written here comes from a Verdict object. If the engine changes its mind,
this file changes with it, and the page changes with the file. There is no path by which
the page can say something the engine did not.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from clearance import instruments, semantic as S, wedge as W  # noqa: E402
from clearance.facts import Claim, judge_claim  # noqa: E402

PRODUCTION = "ai-act-penalties"


def _run(case, checks) -> dict:
    saved = S.DEFAULT_CHECKS
    S.DEFAULT_CHECKS = checks
    try:
        v = judge_claim(Claim(case.case_id, case.claim, W.URL, case.must_contain),
                        fetch=True)
    finally:
        S.DEFAULT_CHECKS = saved
    return {
        "verdict": v.verdict,
        "label": "SOURCED" if v.verdict == "GREEN" else "REFUSED",
        "cause": v.cause,
        "refusal_code": v.refusal_code,
        "reason": v.reason,
        "citation_url": v.citation_url,
        "quoted_terms": v.quoted_terms,
        "trail": [dict(r) for r in v.trail],
    }


def main() -> int:
    body = instruments.document(W.URL, fetch=True)
    if not body:
        print("FAILED: could not fetch the cited document. The receipt is not written "
              "from memory — run this online.", file=sys.stderr)
        return 1

    cases = []
    for c in W.CASES:
        base = _run(c, ("polarity",))
        ships = _run(c, ("polarity", "citation"))
        agrees = ships["label"] == c.expect
        cases.append({"id": c.case_id, "claim": c.claim,
                      "must_contain": c.must_contain, "expect": c.expect,
                      "note": c.note, "base": base, "ships": ships,
                      "engine_agrees_with_label": agrees,
                      "coverage": S.coverage(base.get("quoted_terms") or "", c.claim)})
        print(f"{c.case_id}  expect {c.expect:8}  BASE {base['label']:8} -> "
              f"SHIPS {ships['label']:8}  {ships['refusal_code'] or ''}  "
              f"{'OK' if agrees else 'WRONG'}")

    # The registry gets the run. This is not a demo being staged onto the shelf: it is a
    # real clearance of two real claims against a real fetched instrument, and the shelf
    # is where clearances go. It is INSERT OR IGNORE, so re-running adds nothing.
    from clearance import refusal_log
    con = refusal_log.connect()
    before = refusal_log.stats(con)["n"]
    for c, case in zip(W.CASES, cases):
        sh = case["ships"]
        refusal_log.record(
            con, term=c.must_contain, assertion=c.claim,
            verdict=sh["verdict"], production=PRODUCTION,
            basis="primary" if sh["verdict"] == "GREEN" else None,
            cause=sh["cause"], citation_url=sh["citation_url"],
            quoted_terms=sh["quoted_terms"], origins=[PRODUCTION],
            refusal_code=sh["refusal_code"], trail=sh["trail"])
    print(f"registry: {refusal_log.stats(con)['n'] - before} new row(s), "
          f"{refusal_log.stats(con)['n']} total")

    W.RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    W.RECEIPT.write_text(json.dumps({
        "produced_by": W.COMMAND,
        "produced_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "url": W.URL,
        "instrument": W.INSTRUMENT,
        "document_chars": len(body),
        "cases": cases,
    }, indent=1))
    print(f"\nwritten: {W.RECEIPT.relative_to(ROOT)}  ({len(body):,} chars fetched)")
    return 0 if all(c["engine_agrees_with_label"] for c in cases) else 1


if __name__ == "__main__":
    raise SystemExit(main())
