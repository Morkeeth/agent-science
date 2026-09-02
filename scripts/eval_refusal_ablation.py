#!/usr/bin/env python3
"""Qwen eval gate — ablation arm: signature mechanism (verify) switched off.

Ablation accepts the locator's first proposal when must_contain appears in it,
without running clearance.verify — the structural guard this project sells.

Run: python3 scripts/seed_document_cache.py && python3 scripts/eval_refusal_ablation.py
"""
from __future__ import annotations

import html
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from clearance import holdout, instruments
from clearance.facts import Claim
from clearance.locate import DEFAULT, StringLocator
from clearance.verdict import GREEN, UNKNOWN

sys.path.insert(0, str(ROOT / "scripts"))
from eval_stats import format_ci, mcnemar_exact  # noqa: E402


def _visible(raw: str) -> str:
    raw = re.sub(r"<(script|style).*?</\1>", " ", raw, flags=re.S | re.I)
    txt = html.unescape(re.sub(r"<[^>]+>", " ", raw))
    return re.sub(r"\s+", " ", txt).strip()


def _ablation_verdict(url: str, body: str, claim: str, must_contain: str) -> str:
    """Locator proposes; no verify() — accept if terms appear in proposal."""
    saved = instruments.document

    def fake(u, fetch=False):
        return body if u == url else saved(u, fetch=fetch)

    instruments.document = fake
    try:
        proposed = DEFAULT.propose(
            claim=claim, must_contain=must_contain, document=body,
        )
        if proposed and must_contain in proposed:
            return GREEN
        return UNKNOWN
    finally:
        instruments.document = saved


def _shipping_verdict(url: str, body: str, claim: str, must_contain: str) -> str:
    from clearance.facts import judge_claim

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
        return v.verdict
    finally:
        instruments.document = saved


def _gold(expected: str) -> str:
    return GREEN if expected == "SUPPORTED" else UNKNOWN


def main() -> None:
    holdout.verify()
    items = holdout.holdout_set()["items"]
    rows = []
    abl_correct = ship_correct = 0
    b_win = c = 0
    n = len(items)

    for item in items:
        doc_path = ROOT / item["document"]
        body = _visible(doc_path.read_text())
        url = f"file://{doc_path.name}"
        gold = _gold(item["expected"])

        abl = _ablation_verdict(url, body, item["claim"], item["must_contain"])
        ship = _shipping_verdict(url, body, item["claim"], item["must_contain"])

        abl_ok = abl == gold
        ship_ok = ship == gold
        abl_correct += int(abl_ok)
        ship_correct += int(ship_ok)
        if abl_ok and not ship_ok:
            b_win += 1
        elif ship_ok and not abl_ok:
            c += 1
        rows.append({
            "id": item["id"],
            "expected": item["expected"],
            "ablation": abl,
            "shipping": ship,
            "abl_ok": abl_ok,
            "ship_ok": ship_ok,
        })

    print("REFUSAL-CORRECTNESS ABLATION — n=%d held-out items" % n)
    print("Ablation arm: StringLocator only — verify() OFF")
    print("Shipping arm: StringLocator + verify + judge_claim")
    print()
    print(f"{'id':<6} {'gold':<14} {'ablation':<10} {'shipping':<10} {'a_ok':<6} {'s_ok'}")
    for r in rows:
        print(
            f"{r['id']:<6} {r['expected']:<14} {r['ablation']:<10} {r['shipping']:<10} "
            f"{str(r['abl_ok']):<6} {r['ship_ok']}"
        )
    print()
    print(f"Ablation:  {format_ci(abl_correct, n)}")
    print(f"Shipping:  {format_ci(ship_correct, n)}")
    delta = ship_correct - abl_correct
    print(f"Delta (shipping - ablation): {delta:+d}")
    p, detail = mcnemar_exact(b_win, c)
    print(f"McNemar:   p={p:.4f} ({detail})")
    if ship_correct < abl_correct:
        print("FINDING: ablation beats shipping — verifier hurts accuracy on this set.")
    elif ship_correct == abl_correct:
        print("FINDING: tied — verify() adds no delta on n=%d." % n)
    else:
        print("FINDING: shipping beats ablation by %d item(s) — verify() earns its keep." % delta)

    rc3 = next(r for r in rows if r["id"] == "RC3")
    if rc3["ablation"] == GREEN and rc3["shipping"] == UNKNOWN:
        print("RC3 near-miss date: ablation false-GREEN, shipping refuses — verify() delta proven.")
    rc5 = next(r for r in rows if r["id"] == "RC5")
    if rc5["ablation"] == GREEN and rc5["shipping"] == GREEN:
        print("RC5 substring trap: BOTH arms false-GREEN — semantic guard still missing.")


if __name__ == "__main__":
    main()
