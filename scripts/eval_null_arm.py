#!/usr/bin/env python3
"""Qwen eval gate — always-silent null arm vs shipping on the held-out set.

Steelman baseline: the trivial always-UNKNOWN null (refuse everything). A gate
that cannot beat this is not a gate. Historical lesson: a null once beat both
of our arms on a different eval — ship the comparison so that finding is
visible if it recurs.

Arms:
  Null     — always UNKNOWN (never SOURCED)
  Baseline — substring-in-document (same as eval_refusal_baseline)
  Shipping — StringLocator + verify + judge_claim

Run: python3 scripts/seed_document_cache.py && python3 scripts/eval_null_arm.py
"""
from __future__ import annotations

import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from clearance import instruments
from clearance.facts import Claim, judge_claim
from clearance.locate import DEFAULT
from clearance.verdict import GREEN, UNKNOWN

sys.path.insert(0, str(ROOT / "scripts"))
from eval_stats import format_ci, mcnemar_exact  # noqa: E402

SET = json.loads((ROOT / "fixtures/refusal-correctness/set.json").read_text())


def _visible(raw: str) -> str:
    raw = re.sub(r"<(script|style).*?</\1>", " ", raw, flags=re.S | re.I)
    txt = html.unescape(re.sub(r"<[^>]+>", " ", raw))
    return re.sub(r"\s+", " ", txt).strip()


def _null_verdict(_body: str, _claim: str, _must: str) -> str:
    return UNKNOWN


def _baseline_verdict(body: str, _claim: str, must_contain: str) -> str:
    if must_contain.lower() in body.lower():
        return GREEN
    return UNKNOWN


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


def main() -> int:
    print("NULL-ARM EVAL — always-UNKNOWN vs baseline vs shipping · n=6")
    print("Null arm: refuse everything (always UNKNOWN)")
    print("Baseline: substring-in-document")
    print("Shipping: StringLocator + verify + judge_claim")
    print()

    print(f"{'id':<6} {'gold':<14} {'null':<10} {'base':<10} {'ship':<10}  n_ok b_ok s_ok")
    null_c = base_c = ship_c = 0
    # McNemar null vs shipping
    b_win = c = 0
    # McNemar baseline vs shipping (for context)
    bb_win = bc = 0

    for item in SET["items"]:
        doc_path = ROOT / item["document"]
        body = _visible(doc_path.read_text())
        url = f"file://{doc_path.name}"
        gold = _gold(item["expected"])

        null_v = _null_verdict(body, item["claim"], item["must_contain"])
        base_v = _baseline_verdict(body, item["claim"], item["must_contain"])
        ship_v = _shipping_verdict(url, body, item["claim"], item["must_contain"])

        n_ok = null_v == gold
        b_ok = base_v == gold
        s_ok = ship_v == gold
        null_c += int(n_ok)
        base_c += int(b_ok)
        ship_c += int(s_ok)

        if n_ok and not s_ok:
            b_win += 1
        if s_ok and not n_ok:
            c += 1
        if b_ok and not s_ok:
            bb_win += 1
        if s_ok and not b_ok:
            bc += 1

        print(
            f"{item['id']:<6} {item['expected']:<14} {null_v:<10} {base_v:<10} {ship_v:<10}  "
            f"{n_ok!s:<4} {b_ok!s:<4} {s_ok!s}"
        )

    n = len(SET["items"])
    print()
    print(f"Null:      {format_ci(null_c, n)}")
    print(f"Baseline:  {format_ci(base_c, n)}")
    print(f"Shipping:  {format_ci(ship_c, n)}")
    print(f"Delta (shipping - null):     +{ship_c - null_c}")
    print(f"Delta (shipping - baseline): +{ship_c - base_c}")
    p, note = mcnemar_exact(b_win, c)
    print(f"McNemar null vs shipping:     p={p:.4f} ({note})")
    p2, note2 = mcnemar_exact(bb_win, bc)
    print(f"McNemar baseline vs shipping: p={p2:.4f} ({note2})")

    if ship_c < null_c:
        print("FINDING: NULL BEATS SHIPPING — gate embarrassment; do not publish as win.")
        return 1
    if ship_c == null_c:
        print("FINDING: tied with null — shipping adds no measured accuracy on n=6.")
        return 0
    print("FINDING: shipping beats always-UNKNOWN null.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
