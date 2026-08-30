#!/usr/bin/env python3
"""Qwen eval gate — symmetric scorer on delivered gap rows.

Both arms emit identical registry-facing text; the scorer parses ONLY that text.
Nothing only shipping can emit (no Verdict enum, no internal cause codes).

Run:
  python3 scripts/seed_document_cache.py
  python3 scripts/eval_holdout_freeze.py
  python3 scripts/eval_symmetric_scorer.py
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
from clearance.verdict import GREEN, UNKNOWN, SOURCE_SILENT

sys.path.insert(0, str(ROOT / "scripts"))
from eval_gap_row import excerpt_around, render_gap_row, score_delivered  # noqa: E402
from eval_holdout_freeze import check_holdout  # noqa: E402
from eval_stats import format_ci, mcnemar_exact  # noqa: E402

SET = json.loads((ROOT / "fixtures/refusal-correctness/set.json").read_text())


def _visible(raw: str) -> str:
    raw = re.sub(r"<(script|style).*?</\1>", " ", raw, flags=re.S | re.I)
    txt = html.unescape(re.sub(r"<[^>]+>", " ", raw))
    return re.sub(r"\s+", " ", txt).strip()


def baseline_delivered(body: str, claim: str, must_contain: str) -> str:
    if must_contain.lower() in body.lower():
        span = excerpt_around(body, must_contain)
        return render_gap_row(claim=claim, label="SOURCED", span=span or must_contain)
    return render_gap_row(
        claim=claim, label="UNSOURCED", cause="term_absent_in_document",
    )


def shipping_delivered(url: str, body: str, claim: str, must_contain: str) -> str:
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
        return render_gap_row(
            claim=claim,
            label="SOURCED",
            span=v.quoted_terms or must_contain,
            url=v.citation_url or url,
        )
    cause = v.cause or SOURCE_SILENT
    return render_gap_row(claim=claim, label="UNSOURCED", cause=cause)


def main() -> int:
    ok, msg = check_holdout()
    print(msg)
    if not ok:
        return 1

    rows = []
    base_correct = ship_correct = 0
    b_win = c = 0
    n = len(SET["items"])

    print()
    print("SYMMETRIC SCORER — delivered gap rows only (n=%d)" % n)
    print("Baseline arm: substring → SOURCED|UNSOURCED row")
    print("Shipping arm: judge_claim → same row format")
    print()

    for item in SET["items"]:
        doc_path = ROOT / item["document"]
        body = _visible(doc_path.read_text())
        url = f"file://{doc_path.name}"
        gold = item["expected"]

        base_text = baseline_delivered(body, item["claim"], item["must_contain"])
        ship_text = shipping_delivered(url, body, item["claim"], item["must_contain"])

        base_ok = score_delivered(base_text, gold)
        ship_ok = score_delivered(ship_text, gold)
        base_correct += int(base_ok)
        ship_correct += int(ship_ok)
        if base_ok and not ship_ok:
            b_win += 1
        elif ship_ok and not base_ok:
            c += 1
        rows.append({
            "id": item["id"],
            "expected": gold,
            "base_ok": base_ok,
            "ship_ok": ship_ok,
            "base_text": base_text,
            "ship_text": ship_text,
        })

    print(f"{'id':<6} {'gold':<14} {'b_ok':<6} {'s_ok'}")
    for r in rows:
        print(f"{r['id']:<6} {r['expected']:<14} {str(r['base_ok']):<6} {r['ship_ok']}")

    print()
    print(f"Baseline:  {format_ci(base_correct, n)}")
    print(f"Shipping:  {format_ci(ship_correct, n)}")
    delta = ship_correct - base_correct
    print(f"Delta (shipping - baseline): {delta:+d}")
    p, detail = mcnemar_exact(b_win, c)
    print(f"McNemar:   p={p:.4f} ({detail})")

    rc5 = next(r for r in rows if r["id"] == "RC5")
    if not rc5["base_ok"] and not rc5["ship_ok"]:
        print("RC5 substring trap: BOTH arms false-SOURCED on delivered rows — semantic guard missing.")
        print("--- baseline delivered ---")
        print(rc5["base_text"])
        print("--- shipping delivered ---")
        print(rc5["ship_text"])

    if ship_correct < base_correct:
        print("FINDING: baseline beats shipping on symmetric scorer.")
    elif ship_correct == base_correct:
        print("FINDING: tied — symmetric scorer adds no delta on n=%d." % n)
    else:
        print("FINDING: shipping beats baseline by %d item(s) on delivered rows." % delta)

    return 0


if __name__ == "__main__":
    sys.exit(main())
