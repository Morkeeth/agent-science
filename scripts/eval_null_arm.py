#!/usr/bin/env python3
"""Qwen eval gate — always-silent null arm on the held-out refusal set.

Arms (delivered gap-report labels only):

  NULL      always UNSOURCED — refuse every claim
  BASELINE  substring-in-document → SOURCED if must_contain appears
  SHIPPING  DEFAULT locator + verify + judge_claim → gap label

Accuracy alone often flatters shipping. The metric that can embarrass us is
false-SOURCED rate on gold-UNSOURCED items (false GREEN). Null is always 0
there; baseline is not.

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

from clearance import instruments  # noqa: E402
from clearance.facts import Claim, judge_claim  # noqa: E402
from clearance.locate import DEFAULT  # noqa: E402
from clearance.verdict import GREEN  # noqa: E402

sys.path.insert(0, str(ROOT / "scripts"))
from eval_stats import format_ci, mcnemar_exact  # noqa: E402

SET = json.loads((ROOT / "fixtures/refusal-correctness/set.json").read_text())
GOLD_LABEL = {"SUPPORTED": "SOURCED", "NOT_SUPPORTED": "UNSOURCED"}


def _visible(raw: str) -> str:
    raw = re.sub(r"<(script|style).*?</\1>", " ", raw, flags=re.S | re.I)
    txt = html.unescape(re.sub(r"<[^>]+>", " ", raw))
    return re.sub(r"\s+", " ", txt).strip()


def _deliver(*, item_id: str, claim: str, label: str, span: str | None = None) -> dict:
    row = {"id": item_id, "claim": claim, "label": label}
    if span:
        row["span"] = span
    return row


def _null_deliver(item: dict) -> dict:
    return _deliver(item_id=item["id"], claim=item["claim"], label="UNSOURCED")


def _baseline_deliver(body: str, item: dict) -> dict:
    term = item["must_contain"]
    if term.lower() in body.lower():
        return _deliver(
            item_id=item["id"], claim=item["claim"], label="SOURCED", span=term
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
    return _deliver(item_id=item["id"], claim=item["claim"], label=label, span=span)


def _score(rows: list[dict], gold: dict[str, str]) -> tuple[int, list[dict]]:
    correct = 0
    detail = []
    for row in rows:
        ok = row["label"] == gold[row["id"]]
        correct += int(ok)
        detail.append({**row, "gold": gold[row["id"]], "ok": ok})
    return correct, detail


def _false_sourced(detail: list[dict]) -> tuple[int, int]:
    rows = [r for r in detail if r["gold"] == "UNSOURCED"]
    bad = sum(1 for r in rows if r["label"] == "SOURCED")
    return bad, len(rows)


def main() -> int:
    n = len(SET["items"])
    gold = {it["id"]: GOLD_LABEL[it["expected"]] for it in SET["items"]}

    null_rows, base_rows, ship_rows = [], [], []
    for item in SET["items"]:
        doc_path = ROOT / item["document"]
        body = _visible(doc_path.read_text())
        url = f"file://{doc_path.name}"
        null_rows.append(_null_deliver(item))
        base_rows.append(_baseline_deliver(body, item))
        ship_rows.append(_shipping_deliver(url, body, item))

    null_c, null_d = _score(null_rows, gold)
    base_c, base_d = _score(base_rows, gold)
    ship_c, ship_d = _score(ship_rows, gold)

    print("NULL-ARM EVAL — refusal-correctness held-out set")
    print("NULL:      always UNSOURCED")
    print("BASELINE:  substring → gap label")
    print("SHIPPING:  judge_claim → gap label")
    print()
    print(f"{'id':<6} {'gold':<10} {'null':<10} {'baseline':<10} {'shipping':<10} n b s")
    for nd, bd, sd in zip(null_d, base_d, ship_d):
        print(
            f"{nd['id']:<6} {nd['gold']:<10} {nd['label']:<10} {bd['label']:<10} {sd['label']:<10} "
            f"{str(nd['ok'])[0]} {str(bd['ok'])[0]} {str(sd['ok'])[0]}"
        )

    print()
    print(f"NULL:      {format_ci(null_c, n)}")
    print(f"BASELINE:  {format_ci(base_c, n)}")
    print(f"SHIPPING:  {format_ci(ship_c, n)}")
    print(f"Delta (shipping - null):     {ship_c - null_c:+d}")
    print(f"Delta (shipping - baseline): {ship_c - base_c:+d}")

    def disc(a, b):
        bw = c = 0
        for x, y in zip(a, b):
            if x["ok"] and not y["ok"]:
                bw += 1
            elif (not x["ok"]) and y["ok"]:
                c += 1
        return bw, c

    bw, c = disc(null_d, ship_d)
    p, note = mcnemar_exact(bw, c)
    print(f"McNemar null vs shipping:    p={p:.4f} ({note})")

    for name, detail in ("NULL", null_d), ("BASELINE", base_d), ("SHIPPING", ship_d):
        bad, tot = _false_sourced(detail)
        print(f"False-SOURCED rate {name}: {bad}/{tot}")

    nb, _ = _false_sourced(null_d)
    bb, _ = _false_sourced(base_d)
    sb, _ = _false_sourced(ship_d)
    if nb < bb and sb <= nb:
        print(
            "FINDING: on false-SOURCED, NULL ties or beats SHIPPING and beats BASELINE — "
            "accuracy alone hid the overclaim rate."
        )
    elif ship_c > null_c and sb == 0:
        print(
            "FINDING: SHIPPING beats NULL on accuracy with zero false-SOURCED on this set — "
            "semantic guard earns the RC5 refuse."
        )
    else:
        print("FINDING: see per-item table; do not summarise past the numbers.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
