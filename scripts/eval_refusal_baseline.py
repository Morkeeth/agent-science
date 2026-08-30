#!/usr/bin/env python3
"""Qwen eval gate — alternative arm vs shipping on the held-out refusal set.

Baseline arm: what a competent team builds in two hours — substring match in the
document, no verifier, no independence check. GREEN if must_contain appears anywhere.

Shipping arm: DEFAULT locator + verify + judge_claim (structural guard).

Run: python3 scripts/seed_document_cache.py && python3 scripts/eval_refusal_baseline.py
"""
from __future__ import annotations

import json
import re
import html
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from clearance import instruments, verify as V
from clearance.facts import Claim, judge_claim
from clearance.locate import DEFAULT, StringLocator
from clearance.verdict import GREEN, UNKNOWN

SET = json.loads((ROOT / "fixtures/refusal-correctness/set.json").read_text())


def _visible(raw: str) -> str:
    raw = re.sub(r"<(script|style).*?</\1>", " ", raw, flags=re.S | re.I)
    txt = html.unescape(re.sub(r"<[^>]+>", " ", raw))
    return re.sub(r"\s+", " ", txt).strip()


def _baseline_verdict(body: str, claim: str, must_contain: str) -> str:
    """Naive grep: GREEN if distinctive term appears anywhere in the document."""
    if must_contain.lower() in body.lower():
        return "GREEN"
    return "UNKNOWN"


def _shipping_verdict(url: str, body: str, claim: str, must_contain: str) -> str:
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
    rows = []
    base_correct = ship_correct = 0
    n = len(SET["items"])

    for item in SET["items"]:
        doc_path = ROOT / item["document"]
        body = _visible(doc_path.read_text())
        url = f"file://{doc_path.name}"
        gold = _gold(item["expected"])

        base = _baseline_verdict(body, item["claim"], item["must_contain"])
        ship = _shipping_verdict(url, body, item["claim"], item["must_contain"])

        base_ok = (base == gold) or (gold == GREEN and base == GREEN) or (
            gold == UNKNOWN and base == UNKNOWN
        )
        # stricter: exact match to gold verdict enum
        base_ok = base == gold
        ship_ok = ship == gold

        base_correct += int(base_ok)
        ship_correct += int(ship_ok)
        rows.append({
            "id": item["id"],
            "expected": item["expected"],
            "baseline": base,
            "shipping": ship,
            "baseline_ok": base_ok,
            "shipping_ok": ship_ok,
        })

    print("REFUSAL-CORRECTNESS EVAL — n=%d held-out items" % n)
    print("Baseline arm: substring-in-document (no verifier)")
    print("Shipping arm: StringLocator + verify + judge_claim")
    print()
    print(f"{'id':<6} {'gold':<14} {'baseline':<10} {'shipping':<10} {'b_ok':<6} {'s_ok'}")
    for r in rows:
        print(
            f"{r['id']:<6} {r['expected']:<14} {r['baseline']:<10} {r['shipping']:<10} "
            f"{str(r['baseline_ok']):<6} {r['shipping_ok']}"
        )
    print()
    print(f"Baseline accuracy: {base_correct}/{n} = {base_correct/n:.3f}")
    print(f"Shipping accuracy: {ship_correct}/{n} = {ship_correct/n:.3f}")
    delta = ship_correct - base_correct
    print(f"Delta (shipping - baseline): {delta:+d}")
    if ship_correct < base_correct:
        print("FINDING: baseline beats shipping on this set — report honestly.")
    elif ship_correct == base_correct:
        print("FINDING: tied — verifier adds no delta on n=%d; look at per-item false GREENs." % n)
    else:
        print("FINDING: shipping beats baseline by %d item(s)." % delta)

    # Pin the known substring defect
    rc5 = next(r for r in rows if r["id"] == "RC5")
    if rc5["baseline"] == GREEN and rc5["shipping"] == GREEN:
        print("RC5 substring trap: BOTH arms false-GREEN — documented engine limit.")


if __name__ == "__main__":
    main()
