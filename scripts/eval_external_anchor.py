#!/usr/bin/env python3
"""External anchor eval — live rightsstatements.org pages we did not author.

Qwen PRIOR LOSS gate: one dataset or benchmark we did not build and cannot tune.
These pages are fetched at runtime from rightsstatements.org; labels are the same
RC4/RC6 claims pinned in fixtures/refusal-correctness/set.json.

Run: python3 scripts/eval_external_anchor.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from clearance import instruments
from clearance.facts import Claim, judge_claim
from clearance.locate import DEFAULT
from clearance.verdict import GREEN, UNKNOWN

from eval_stats import format_ci, mcnemar_exact, wilson_ci  # noqa: E402

# External URLs — not our fixtures; fetched live from rightsstatements.org
EXTERNAL = [
    {
        "id": "EA1",
        "url": "https://rightsstatements.org/vocab/InC/1.0/",
        "claim": "The copyright and related rights status of this Item has not been evaluated.",
        "must_contain": "has not been evaluated",
        "expected": "NOT_SUPPORTED",
        "why": "Wrong document — InC page, not CNE. Same RC4 claim as held-out set.",
    },
    {
        "id": "EA2",
        "url": "https://rightsstatements.org/vocab/CNE/1.0/",
        "claim": "The copyright and related rights status of this Item has not been evaluated.",
        "must_contain": "has not been evaluated",
        "expected": "SUPPORTED",
        "why": "CNE page — same RC6 claim as held-out set.",
    },
]


def _gold(expected: str) -> str:
    return GREEN if expected == "SUPPORTED" else UNKNOWN


def _baseline(body: str, must_contain: str) -> str:
    if must_contain.lower() in body.lower():
        return GREEN
    return UNKNOWN


def _shipping(url: str, body: str, claim: str, must_contain: str) -> str:
    saved = instruments.document

    def fake(u, fetch=False):
        return body if instruments.canonical(u) == instruments.canonical(url) else saved(u, fetch=fetch)

    instruments.document = fake
    try:
        v = judge_claim(Claim("x", claim, url, must_contain), locator=DEFAULT, live_search=False)
        return v.verdict
    finally:
        instruments.document = saved


def main() -> int:
    rows = []
    base_ok = ship_ok = 0
    b_win = c = 0

    print("EXTERNAL ANCHOR EVAL — live rightsstatements.org (not our fixtures)")
    print()
    for item in EXTERNAL:
        body = instruments.document(item["url"], fetch=True)
        if not body:
            print(f"FAIL  {item['id']}: could not fetch {item['url']}")
            return 1
        gold = _gold(item["expected"])
        base = _baseline(body, item["must_contain"])
        ship = _shipping(item["url"], body, item["claim"], item["must_contain"])
        b_ok = base == gold
        s_ok = ship == gold
        base_ok += int(b_ok)
        ship_ok += int(s_ok)
        if b_ok and not s_ok:
            b_win += 1
        elif s_ok and not b_ok:
            c += 1
        rows.append({**item, "gold": gold, "baseline": base, "shipping": ship, "b_ok": b_ok, "s_ok": s_ok, "chars": len(body)})

    n = len(rows)
    print(f"{'id':<5} {'expected':<14} {'baseline':<10} {'shipping':<10} {'chars':<6} {'b_ok':<6} s_ok")
    for r in rows:
        print(
            f"{r['id']:<5} {r['expected']:<14} {r['baseline']:<10} {r['shipping']:<10} "
            f"{r['chars']:<6} {str(r['b_ok']):<6} {r['s_ok']}"
        )
    print()
    print(f"Baseline:  {format_ci(base_ok, n)}")
    print(f"Shipping:  {format_ci(ship_ok, n)}")
    p, detail = mcnemar_exact(b_win, c)
    print(f"McNemar:   p={p:.4f} ({detail})")
    if ship_ok < base_ok:
        print("FINDING: baseline beats shipping on external anchor — report honestly.")
    elif ship_ok == base_ok:
        print("FINDING: tied on external anchor — no measured delta.")
    else:
        print(f"FINDING: shipping beats baseline by {ship_ok - base_ok} item(s) on external anchor.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
