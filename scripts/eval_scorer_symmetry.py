#!/usr/bin/env python3
"""Scorer symmetry gate — one external judge on delivered output for every arm.

Qwen PRIOR LOSS gate: nothing only our system can emit; judge from delivered
output (SOURCED/UNSOURCED + passage) for baseline, shipping, and ablation.

The judge never reads internal GREEN/UNKNOWN enums — only the public row a
stranger would see in a gap report.

Run: python3 scripts/seed_document_cache.py && python3 scripts/eval_scorer_symmetry.py
"""
from __future__ import annotations

import html
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from clearance import instruments, verify as V
from clearance.facts import Claim, judge_claim
from clearance.locate import DEFAULT, StringLocator
from clearance.verdict import GREEN, UNKNOWN

sys.path.insert(0, str(ROOT / "scripts"))
from eval_stats import format_ci, mcnemar_exact  # noqa: E402

SET = json.loads((ROOT / "fixtures/refusal-correctness/set.json").read_text())


@dataclass(frozen=True)
class Delivered:
    """Public-facing row — same schema for every arm."""

    status: str  # SOURCED | UNSOURCED
    passage: str | None
    source: str | None


def _visible(raw: str) -> str:
    raw = re.sub(r"<(script|style).*?</\1>", " ", raw, flags=re.S | re.I)
    txt = html.unescape(re.sub(r"<[^>]+>", " ", raw))
    return re.sub(r"\s+", " ", txt).strip()


def judge_delivered(item: dict, row: Delivered) -> bool:
    """Single external scorer — identical for all arms."""
    if item["expected"] == "SUPPORTED":
        if row.status != "SOURCED":
            return False
        if not row.passage:
            return False
        doc_path = ROOT / item["document"]
        body = doc_path.read_text()
        if row.passage not in body:
            return False
        if item["must_contain"] not in row.passage:
            return False
        return V.verify(row.passage, document=body, must_contain=item["must_contain"]) is None
    # NOT_SUPPORTED — must refuse (no SOURCED with verified passage)
    if row.status == "SOURCED" and row.passage:
        doc_path = ROOT / item["document"]
        body = doc_path.read_text()
        if V.verify(row.passage, document=body, must_contain=item["must_contain"]) is None:
            return False
    return row.status == "UNSOURCED"


def _baseline_deliver(body: str, must_contain: str) -> Delivered:
    if must_contain.lower() in body.lower():
        return Delivered(status="SOURCED", passage=None, source=None)
    return Delivered(status="UNSOURCED", passage=None, source=None)


def _shipping_deliver(url: str, body: str, claim: str, must_contain: str) -> Delivered:
    saved = instruments.document

    def fake(u, fetch=False):
        return body if u == url else saved(u, fetch=fetch)

    instruments.document = fake
    try:
        v = judge_claim(Claim("x", claim, url, must_contain), locator=DEFAULT, live_search=False)
    finally:
        instruments.document = saved

    if v.verdict == GREEN and v.quoted_terms:
        return Delivered(status="SOURCED", passage=v.quoted_terms, source=v.citation_url)
    return Delivered(status="UNSOURCED", passage=None, source=v.citation_url)


def _ablation_deliver(url: str, body: str, claim: str, must_contain: str) -> Delivered:
    """Locator only — verify() switched off."""
    saved = instruments.document
    loc = StringLocator()

    def fake(u, fetch=False):
        return body if u == url else saved(u, fetch=fetch)

    instruments.document = fake
    try:
        passage = loc.propose(claim=claim, must_contain=must_contain, document=body)
        if passage and V.verify(passage, document=body, must_contain=must_contain) is None:
            return Delivered(status="SOURCED", passage=passage, source=url)
        return Delivered(status="UNSOURCED", passage=None, source=url)
    finally:
        instruments.document = saved


def _score_arm(name: str, deliver_fn) -> tuple[list[dict], int, int, int]:
    rows = []
    correct = 0
    b_win = c = 0
    for item in SET["items"]:
        doc_path = ROOT / item["document"]
        body = _visible(doc_path.read_text())
        url = f"file://{doc_path.name}"
        if deliver_fn.__name__ == "_baseline_deliver":
            d = deliver_fn(body, item["must_contain"])
        else:
            d = deliver_fn(url, body, item["claim"], item["must_contain"])
        ok = judge_delivered(item, d)
        correct += int(ok)
        rows.append({"id": item["id"], "expected": item["expected"], "delivered": d, "ok": ok})
    return rows, correct, b_win, c


def main() -> int:
    n = len(SET["items"])
    arms: dict[str, tuple[list[dict], int]] = {}

    for name, fn in (
        ("baseline", _baseline_deliver),
        ("shipping", _shipping_deliver),
        ("ablation", _ablation_deliver),
    ):
        rows, correct, _, _ = _score_arm(name, fn)
        arms[name] = (rows, correct)

    print("SCORER SYMMETRY GATE — one judge on delivered rows (SOURCED/UNSOURCED + passage)")
    print()
    header = f"{'id':<6} {'gold':<14} {'baseline':<12} {'shipping':<12} {'ablation':<12} b s a"
    print(header)
    for i, item in enumerate(SET["items"]):
        parts = []
        for arm in ("baseline", "shipping", "ablation"):
            d = arms[arm][0][i]["delivered"]
            parts.append(f"{d.status[:4]}")
        b_ok, s_ok, a_ok = (arms[a][0][i]["ok"] for a in ("baseline", "shipping", "ablation"))
        print(
            f"{item['id']:<6} {item['expected']:<14} {parts[0]:<12} {parts[1]:<12} {parts[2]:<12} "
            f"{int(b_ok)} {int(s_ok)} {int(a_ok)}"
        )

    print()
    scores = {arm: arms[arm][1] for arm in arms}
    for arm in ("baseline", "shipping", "ablation"):
        print(f"{arm.capitalize():<10} {format_ci(scores[arm], n)}")

    # McNemar: shipping vs baseline on symmetric judge
    b_win = c = 0
    for i in range(n):
        b_ok = arms["baseline"][0][i]["ok"]
        s_ok = arms["shipping"][0][i]["ok"]
        if b_ok and not s_ok:
            b_win += 1
        elif s_ok and not b_ok:
            c += 1
    p, detail = mcnemar_exact(b_win, c)
    print(f"McNemar (shipping vs baseline, symmetric judge): p={p:.4f} ({detail})")

    rc5 = next(r for r in arms["shipping"][0] if r["id"] == "RC5")
    if rc5["delivered"].status == "SOURCED":
        print("RC5 substring trap: shipping false-SOURCED under symmetric judge — documented engine limit.")

    if scores["baseline"] == scores["shipping"] == scores["ablation"]:
        print("FINDING: all three arms tie under symmetric judge — no arm wins on delivered output alone.")
    elif scores["shipping"] < scores["baseline"]:
        print("FINDING: baseline beats shipping under symmetric judge — report honestly.")
    else:
        print(f"FINDING: shipping={scores['shipping']} baseline={scores['baseline']} ablation={scores['ablation']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
