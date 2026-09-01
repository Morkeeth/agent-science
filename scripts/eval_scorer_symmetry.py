#!/usr/bin/env python3
"""Qwen eval gate — scorer symmetrical across arms.

Both arms emit the same delivered JSON schema. The scorer reads ONLY that output —
no internal GREEN/UNKNOWN, no project-specific verdict types.

Run: python3 scripts/seed_document_cache.py && python3 scripts/eval_scorer_symmetry.py
"""
from __future__ import annotations

import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from clearance import instruments, verify as V
from clearance.facts import Claim, judge_claim
from clearance.locate import DEFAULT
from clearance.verdict import GREEN, UNKNOWN

sys.path.insert(0, str(ROOT / "scripts"))
from eval_stats import format_ci, mcnemar_exact  # noqa: E402

SET = json.loads((ROOT / "fixtures/refusal-correctness/set.json").read_text())
SCHEMA_KEYS = ("status", "passage", "cause")


def _visible(raw: str) -> str:
    raw = re.sub(r"<(script|style).*?</\1>", " ", raw, flags=re.S | re.I)
    txt = html.unescape(re.sub(r"<[^>]+>", " ", raw))
    return re.sub(r"\s+", " ", txt).strip()


def _deliver_baseline(body: str, must_contain: str) -> dict:
    """Naive arm — substring match only."""
    if must_contain.lower() in body.lower():
        return {"status": "SUPPORTED", "passage": must_contain, "cause": None}
    return {"status": "NOT_SUPPORTED", "passage": None, "cause": "term_not_in_document"}


def _deliver_shipping(url: str, body: str, claim: str, must_contain: str) -> dict:
    """Shipping arm — full judge path, normalized to delivered schema."""
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
    finally:
        instruments.document = saved

    if v.verdict == GREEN:
        return {"status": "SUPPORTED", "passage": v.quoted_terms, "cause": None}
    return {
        "status": "NOT_SUPPORTED",
        "passage": None,
        "cause": v.cause or v.refusal_code or "refused",
    }


def _score_delivered(gold_expected: str, delivered: dict) -> bool:
    """External scorer — identical for every arm."""
    assert set(delivered.keys()) == set(SCHEMA_KEYS), delivered
    if gold_expected == "SUPPORTED":
        return delivered["status"] == "SUPPORTED" and bool(delivered.get("passage"))
    return delivered["status"] == "NOT_SUPPORTED"


def main() -> None:
    rows = []
    base_correct = ship_correct = 0
    b_win = c = 0
    n = len(SET["items"])

    for item in SET["items"]:
        doc_path = ROOT / item["document"]
        body = _visible(doc_path.read_text())
        url = f"file://{doc_path.name}"

        base_out = _deliver_baseline(body, item["must_contain"])
        ship_out = _deliver_shipping(url, body, item["claim"], item["must_contain"])

        base_ok = _score_delivered(item["expected"], base_out)
        ship_ok = _score_delivered(item["expected"], ship_out)
        base_correct += int(base_ok)
        ship_correct += int(ship_ok)
        if base_ok and not ship_ok:
            b_win += 1
        elif ship_ok and not base_ok:
            c += 1
        rows.append({
            "id": item["id"],
            "expected": item["expected"],
            "baseline": base_out,
            "shipping": ship_out,
            "baseline_ok": base_ok,
            "shipping_ok": ship_ok,
        })

    print("SCORER SYMMETRY EVAL — n=%d held-out items" % n)
    print("Delivered schema:", SCHEMA_KEYS)
    print("Scorer: SUPPORTED iff status=SUPPORTED and passage present; else NOT_SUPPORTED iff status=NOT_SUPPORTED")
    print()
    print(f"{'id':<6} {'gold':<14} {'b_status':<14} {'s_status':<14} {'b_ok':<6} {'s_ok'}")
    for r in rows:
        print(
            f"{r['id']:<6} {r['expected']:<14} {r['baseline']['status']:<14} "
            f"{r['shipping']['status']:<14} {str(r['baseline_ok']):<6} {r['shipping_ok']}"
        )
    print()
    print(f"Baseline:  {format_ci(base_correct, n)}")
    print(f"Shipping:  {format_ci(ship_correct, n)}")
    delta = ship_correct - base_correct
    print(f"Delta (shipping - baseline): {delta:+d}")
    p, detail = mcnemar_exact(b_win, c)
    print(f"McNemar:   p={p:.4f} ({detail})")
    if ship_correct < base_correct:
        print("FINDING: baseline beats shipping under symmetric scorer.")
    elif ship_correct == base_correct:
        print("FINDING: tied under symmetric scorer on n=%d." % n)
    else:
        print("FINDING: shipping beats baseline by %d under symmetric scorer." % delta)

    rc5 = next(r for r in rows if r["id"] == "RC5")
    if rc5["baseline"]["status"] == "SUPPORTED" and rc5["shipping"]["status"] == "NOT_SUPPORTED":
        print("RC5: baseline false-SUPPORTED, shipping refuses — delta visible to external judge.")


if __name__ == "__main__":
    main()
