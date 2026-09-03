#!/usr/bin/env python3
"""Qwen eval gate — symmetrical scorer on delivered gap-report rows only.

Every arm emits the same JSON shape a judge or Devpost reader would see:
  {"id", "label": "SOURCED"|"UNSOURCED", "claim", "span"}

The scorer reads ONLY `label` — never engine_verdict, cause, or internal enums.
Baseline arm: competent two-hour substring matcher (no verifier).
Shipping arm: DEFAULT locator + verify + judge_claim, then map to gap labels.

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

from clearance import instruments, verify as V  # noqa: F401
from clearance.facts import Claim, judge_claim
from clearance.locate import DEFAULT
from clearance.verdict import GREEN, UNKNOWN

sys.path.insert(0, str(ROOT / "scripts"))
from eval_stats import format_ci, mcnemar_exact  # noqa: E402

SET = json.loads((ROOT / "fixtures/refusal-correctness/set.json").read_text())
GOLD_LABEL = {"SUPPORTED": "SOURCED", "NOT_SUPPORTED": "UNSOURCED"}


def _visible(raw: str) -> str:
    raw = re.sub(r"<(script|style).*?</\1>", " ", raw, flags=re.S | re.I)
    txt = html.unescape(re.sub(r"<[^>]+>", " ", raw))
    return re.sub(r"\s+", " ", txt).strip()


def _deliver(*, item_id: str, claim: str, label: str, span: str | None = None) -> dict:
    """Gap-report row any arm can emit — no internal engine fields."""
    row = {"id": item_id, "claim": claim, "label": label}
    if span:
        row["span"] = span
    return row


def _baseline_deliver(body: str, item: dict) -> dict:
    term = item["must_contain"]
    if term.lower() in body.lower():
        return _deliver(
            item_id=item["id"],
            claim=item["claim"],
            label="SOURCED",
            span=term,
        )
    return _deliver(item_id=item["id"], claim=item["claim"], label="UNSOURCED")


def _shipping_deliver(url: str, body: str, item: dict) -> dict:
    saved = instruments.document

    def fake(u, fetch=False):
        return body if u == url else saved(u, fetch=fetch)

    instruments.document = fake
    try:
        v = judge_claim(
            Claim("x", item["claim"], url, item["must_contain"]),
            locator=DEFAULT,
            live_search=False,
        )
    finally:
        instruments.document = saved

    label = "SOURCED" if v.verdict == GREEN else "UNSOURCED"
    span = v.quoted_terms if v.verdict == GREEN else None
    row = _deliver(item_id=item["id"], claim=item["claim"], label=label, span=span)
    # Paranoia: scorer must not need engine-only fields
    assert "engine_verdict" not in row and "cause" not in row
    return row


def _score_delivered(rows: list[dict], gold: dict[str, str]) -> tuple[int, list[dict]]:
    """Single scorer for every arm — label field only."""
    correct = 0
    detail = []
    for row in rows:
        want = gold[row["id"]]
        got = row["label"]
        ok = got == want
        correct += int(ok)
        detail.append({**row, "gold": want, "ok": ok})
    return correct, detail


def main() -> None:
    n = len(SET["items"])
    gold = {item["id"]: GOLD_LABEL[item["expected"]] for item in SET["items"]}

    baseline_rows = []
    shipping_rows = []
    for item in SET["items"]:
        doc_path = ROOT / item["document"]
        body = _visible(doc_path.read_text())
        url = f"file://{doc_path.name}"
        baseline_rows.append(_baseline_deliver(body, item))
        shipping_rows.append(_shipping_deliver(url, body, item))

    base_correct, base_detail = _score_delivered(baseline_rows, gold)
    ship_correct, ship_detail = _score_delivered(shipping_rows, gold)

    b_win = c = 0
    for b, s in zip(base_detail, ship_detail):
        if b["ok"] and not s["ok"]:
            b_win += 1
        elif s["ok"] and not b["ok"]:
            c += 1

    print("SCORER SYMMETRY EVAL — delivered gap-report rows only")
    print("Scorer: label == gold (SOURCED|UNSOURCED); ignores engine internals")
    print("Baseline arm: substring → gap label")
    print("Shipping arm: judge_claim → gap label via _present mapping")
    print()
    print(f"{'id':<6} {'gold':<12} {'baseline':<10} {'shipping':<10} {'b_ok':<6} {'s_ok'}")
    for b, s in zip(base_detail, ship_detail):
        print(
            f"{b['id']:<6} {b['gold']:<12} {b['label']:<10} {s['label']:<10} "
            f"{str(b['ok']):<6} {s['ok']}"
        )
    print()
    print(f"Baseline:  {format_ci(base_correct, n)}")
    print(f"Shipping:  {format_ci(ship_correct, n)}")
    delta = ship_correct - base_correct
    print(f"Delta (shipping - baseline): {delta:+d}")
    p, detail = mcnemar_exact(b_win, c)
    print(f"McNemar:   p={p:.4f} ({detail})")

    if ship_correct < base_correct:
        print("FINDING: baseline beats shipping on delivered labels — report honestly.")
    elif ship_correct == base_correct:
        print("FINDING: tied on delivered labels at n=%d." % n)
    else:
        print("FINDING: shipping beats baseline by %d delivered label(s)." % delta)

    rc5 = next(r for r in ship_detail if r["id"] == "RC5")
    if rc5["label"] == "SOURCED":
        print("RC5: shipping false-SOURCED on delivered label — would fail on camera.")


if __name__ == "__main__":
    main()
