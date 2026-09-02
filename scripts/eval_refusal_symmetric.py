#!/usr/bin/env python3
"""Qwen eval gate — symmetric scorer on delivered output only.

Both arms emit the same neutral deliverable:
    {"supported": bool, "quote": str | null}

The scorer never reads GREEN/UNKNOWN, cause codes, refusal_code, or any field only
the shipping stack can emit. A competent baseline team can produce the same shape.

Run: python3 scripts/seed_document_cache.py && python3 scripts/eval_refusal_symmetric.py
"""
from __future__ import annotations

import html
import re
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from clearance import holdout, instruments
from clearance.facts import Claim, judge_claim
from clearance.locate import DEFAULT

sys.path.insert(0, str(ROOT / "scripts"))
from eval_stats import format_ci, mcnemar_exact  # noqa: E402


@dataclass(frozen=True)
class Delivered:
    """What a judge sees — identical shape for every arm."""
    supported: bool
    quote: str | None


def score_delivered(d: Delivered, expected: str) -> bool:
    """External scorer: bool supported vs gold SUPPORTED / NOT_SUPPORTED only."""
    gold = expected == "SUPPORTED"
    return d.supported == gold


def _visible(raw: str) -> str:
    raw = re.sub(r"<(script|style).*?</\1>", " ", raw, flags=re.S | re.I)
    txt = html.unescape(re.sub(r"<[^>]+>", " ", raw))
    return re.sub(r"\s+", " ", txt).strip()


def baseline_deliver(body: str, must_contain: str) -> Delivered:
    """Naive grep arm — substring anywhere in document."""
    idx = body.lower().find(must_contain.lower())
    if idx < 0:
        return Delivered(supported=False, quote=None)
    return Delivered(supported=True, quote=body[idx: idx + len(must_contain)])


def shipping_deliver(url: str, body: str, claim: str, must_contain: str) -> Delivered:
    """Shipping stack — map verdict to the same deliverable shape."""
    saved = instruments.document

    def fake(u, fetch=False):
        return body if u == url else saved(u, fetch=fetch)

    instruments.document = fake
    try:
        v = judge_claim(
            Claim("x", claim, url, must_contain),
            locator=DEFAULT,
            live_search=False,
        )
        return Delivered(
            supported=(v.verdict == "GREEN"),
            quote=v.quoted_terms,
        )
    finally:
        instruments.document = saved


def main() -> None:
    holdout.verify()
    items = holdout.holdout_set()["items"]
    n = len(items)
    rows = []
    base_correct = ship_correct = 0
    b_win = c = 0

    for item in items:
        doc_path = ROOT / item["document"]
        body = _visible(doc_path.read_text())
        url = f"file://{doc_path.name}"

        base_d = baseline_deliver(body, item["must_contain"])
        ship_d = shipping_deliver(url, body, item["claim"], item["must_contain"])

        base_ok = score_delivered(base_d, item["expected"])
        ship_ok = score_delivered(ship_d, item["expected"])
        base_correct += int(base_ok)
        ship_correct += int(ship_ok)
        if base_ok and not ship_ok:
            b_win += 1
        elif ship_ok and not base_ok:
            c += 1
        rows.append({
            "id": item["id"],
            "expected": item["expected"],
            "baseline": base_d,
            "shipping": ship_d,
            "base_ok": base_ok,
            "ship_ok": ship_ok,
        })

    print("REFUSAL-CORRECTNESS SYMMETRIC SCORER — n=%d held-out items" % n)
    print("Deliverable: {supported: bool, quote: str|null} — same for both arms")
    print("Scorer: external bool match to gold SUPPORTED / NOT_SUPPORTED")
    print()
    print(f"{'id':<6} {'gold':<14} {'b_sup':<6} {'s_sup':<6} {'b_ok':<6} {'s_ok'}")
    for r in rows:
        print(
            f"{r['id']:<6} {r['expected']:<14} "
            f"{str(r['baseline'].supported):<6} {str(r['shipping'].supported):<6} "
            f"{str(r['base_ok']):<6} {r['ship_ok']}"
        )
    print()
    print(f"Baseline:  {format_ci(base_correct, n)}")
    print(f"Shipping:  {format_ci(ship_correct, n)}")
    delta = ship_correct - base_correct
    print(f"Delta (shipping - baseline): {delta:+d}")
    p, detail = mcnemar_exact(b_win, c)
    print(f"McNemar:   p={p:.4f} ({detail})")
    if ship_correct < base_correct:
        print("FINDING: baseline beats shipping under symmetric scorer — report honestly.")
    elif ship_correct == base_correct:
        print("FINDING: tied — shipping adds no delta on n=%d under symmetric scorer." % n)
    else:
        print("FINDING: shipping beats baseline by %d item(s)." % delta)

    rc5 = next(r for r in rows if r["id"] == "RC5")
    if rc5["baseline"].supported and not rc5["shipping"].supported:
        print("RC5 substring trap: baseline false-GREEN, shipping refuses — symmetric delta proven.")
    elif rc5["baseline"].supported and rc5["shipping"].supported:
        print("RC5: BOTH arms false-GREEN under symmetric scorer.")


if __name__ == "__main__":
    main()
