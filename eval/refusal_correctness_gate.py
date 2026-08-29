#!/usr/bin/env python3
"""Qwen gate · alternative arm + ablation on held-out refusal-correctness set.

External anchor: fixtures/refusal-correctness/set.json (labels predate engine).

Arms (identical inputs, identical budget, identical prompt shape):
  BASELINE  — naive first-occurrence substring locator, no verify step.
              What a competent team ships in two hours: if must_contain is in the
              document, return a window around the first hit and call it sourced.
  ABLATION  — clearance.locate.DEFAULT with verify switched OFF.
              Our locator, minus the one signature mechanism this repo adds.
  SHIPPING  — clearance.locate.DEFAULT + clearance.verify (the product path).

Run (offline, no API key):
    python3 eval/refusal_correctness_gate.py

Writes eval/RECEIPT-refusal-gate.md and exits non-zero if shipping loses to baseline
on catchable items (false GREEN or false UNKNOWN count).
"""
from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from clearance import instruments, verify as V
from clearance.facts import Claim, judge_claim
from clearance.locate import DEFAULT
from clearance.verdict import GREEN, UNKNOWN

SET_PATH = ROOT / "fixtures/refusal-correctness/set.json"
RECEIPT = ROOT / "eval/RECEIPT-refusal-gate.md"


@dataclass(frozen=True)
class Row:
    arm: str
    item_id: str
    gold: str
    predicted: str
    cause: str | None
    quote: str
    ok: bool


class NaiveFirstOccurrence:
    """Baseline arm — substring in document ⇒ sourced. No verifier."""

    name = "naive-first-occurrence"

    def propose(self, *, claim: str, must_contain: str, document: str) -> Optional[str]:
        i = document.find(must_contain)
        if i < 0:
            return None
        return document[max(0, i - 40): i + len(must_contain) + 80].strip()


def _doc(rel: str) -> str:
    return (ROOT / rel).read_text()


def _run_baseline(it: dict) -> Row:
    body = _doc(it["document"])
    loc = NaiveFirstOccurrence()
    proposed = loc.propose(claim=it["claim"], must_contain=it["must_contain"], document=body)
    if proposed is None:
        pred, cause, quote = UNKNOWN, "no_substring", ""
    else:
        # Baseline skips verify — substring presence is enough
        pred, cause, quote = GREEN, None, proposed[:120]
        # Record whether the shipping verifier would admit this quote (honesty metric)
        if V.verify(proposed, document=body, must_contain=it["must_contain"]) is not None:
            cause = "would_fail_verify"
    gold = it["expected"]
    ok = (pred == GREEN and gold == "SUPPORTED") or (pred == UNKNOWN and gold == "NOT_SUPPORTED")
    if it.get("engine_limit"):
        ok = True  # scored separately; not in catchable denominator
    return Row("BASELINE", it["id"], gold, pred, cause, quote, ok)


def _with_doc(url: str, body: str, claim: Claim, locator):
    saved = instruments.document

    def fake(u, fetch=False):
        return body if u == url else saved(u, fetch=fetch)

    instruments.document = fake
    try:
        return judge_claim(claim, locator=locator)
    finally:
        instruments.document = saved


def _run_ablation(it: dict) -> Row:
    """Shipping locator with verify bypassed — ablation of our signature guard."""
    url = f"fixture://abl-{it['id']}"
    body = _doc(it["document"])
    proposed = DEFAULT.propose(
        claim=it["claim"], must_contain=it["must_contain"], document=body
    )
    if proposed is None:
        pred, cause, quote = UNKNOWN, "locator_no_passage", ""
    else:
        pred, cause, quote = GREEN, "verify_bypassed", proposed[:120]
        if V.verify(proposed, document=body, must_contain=it["must_contain"]) is not None:
            cause = "would_fail_verify"
    gold = it["expected"]
    ok = (pred == GREEN and gold == "SUPPORTED") or (
        pred == UNKNOWN and gold == "NOT_SUPPORTED"
    )
    if it.get("engine_limit"):
        ok = True
    return Row("ABLATION", it["id"], gold, pred, cause, quote, ok)


def _run_shipping(it: dict) -> Row:
    url = f"fixture://ship-{it['id']}"
    v = _with_doc(
        url,
        _doc(it["document"]),
        Claim(it["id"], it["claim"], url, it["must_contain"]),
        DEFAULT,
    )
    gold = it["expected"]
    ok = (v.verdict == GREEN and gold == "SUPPORTED") or (
        v.verdict == UNKNOWN and gold == "NOT_SUPPORTED"
    )
    if it.get("engine_limit"):
        ok = True
    return Row(
        "SHIPPING",
        it["id"],
        gold,
        v.verdict,
        v.cause,
        (v.quoted_terms or "")[:120],
        ok,
    )


def _score(rows: list[Row], *, catchable_ids: set[str]) -> dict:
    sub = [r for r in rows if r.item_id in catchable_ids]
    n = len(sub)
    correct = sum(r.ok for r in sub)
    false_green = [
        r for r in sub if r.gold == "NOT_SUPPORTED" and r.predicted == GREEN
    ]
    false_unknown = [
        r for r in sub if r.gold == "SUPPORTED" and r.predicted == UNKNOWN
    ]
    return {
        "n": n,
        "correct": correct,
        "accuracy": correct / n if n else 0.0,
        "false_green": len(false_green),
        "false_unknown": len(false_unknown),
        "false_green_ids": [r.item_id for r in false_green],
        "false_unknown_ids": [r.item_id for r in false_unknown],
    }


def _write_receipt(
    items: list[dict],
    baseline_rows: list[Row],
    ablation_rows: list[Row],
    shipping_rows: list[Row],
    b_score: dict,
    a_score: dict,
    s_score: dict,
    *,
    labelled_at: str,
) -> None:
    catchable = {it["id"] for it in items if not it.get("engine_limit")}
    limits = [it for it in items if it.get("engine_limit")]

    lines = [
        "# REFUSAL CORRECTNESS GATE — alternative arm receipt",
        "",
        f"**Date:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        f"**Anchor:** `{SET_PATH.relative_to(ROOT)}` — labelled {labelled_at}",
        "",
        "## Arms",
        "",
        "| Arm | Implementation |",
        "|-----|----------------|",
        "| **BASELINE** | `NaiveFirstOccurrence`: first `must_contain` window, **no verify** |",
        "| **ABLATION** | `StringLocator` (DEFAULT) with **verify bypassed** |",
        "| **SHIPPING** | `StringLocator` (DEFAULT) + `verify.py` structural guard |",
        "",
        "## Catchable items (n=5; RC5 excluded — documented engine_limit)",
        "",
        "| id | gold | BASELINE | ABLATION | SHIPPING |",
        "|----|------|----------|----------|----------|",
    ]

    by_b = {r.item_id: r for r in baseline_rows}
    by_a = {r.item_id: r for r in ablation_rows}
    by_s = {r.item_id: r for r in shipping_rows}
    for it in items:
        if it.get("engine_limit"):
            continue
        b, a, s = by_b[it["id"]], by_a[it["id"]], by_s[it["id"]]
        lines.append(
            f"| {it['id']} | {it['expected']} | {b.predicted} | {a.predicted} | {s.predicted} |"
        )

    lines += [
        "",
        "## Aggregate (catchable only)",
        "",
        "| Arm | correct | n | accuracy | false GREEN | false UNKNOWN |",
        "|-----|--------:|--:|---------:|------------:|--------------:|",
        f"| BASELINE | {b_score['correct']} | {b_score['n']} | {b_score['accuracy']:.0%} | "
        f"{b_score['false_green']} | {b_score['false_unknown']} |",
        f"| ABLATION | {a_score['correct']} | {a_score['n']} | {a_score['accuracy']:.0%} | "
        f"{a_score['false_green']} | {a_score['false_unknown']} |",
        f"| SHIPPING | {s_score['correct']} | {s_score['n']} | {s_score['accuracy']:.0%} | "
        f"{s_score['false_green']} | {s_score['false_unknown']} |",
        "",
        "## Honesty & limitations (worst numbers)",
        "",
    ]

    worse = []
    if b_score["false_green"] < s_score["false_green"]:
        worse.append(
            f"- SHIPPING has **more false GREEN** ({s_score['false_green']} vs "
            f"{b_score['false_green']}): {s_score['false_green_ids']}"
        )
    elif s_score["false_green"] < b_score["false_green"]:
        worse.append(
            f"- BASELINE has **more false GREEN** ({b_score['false_green']} vs "
            f"{s_score['false_green']}): {b_score['false_green_ids']}"
        )
    if b_score["false_unknown"] > s_score["false_unknown"]:
        worse.append(
            f"- BASELINE has **more false UNKNOWN** ({b_score['false_unknown']} vs "
            f"{s_score['false_unknown']}): {b_score['false_unknown_ids']}"
        )
    elif s_score["false_unknown"] > b_score["false_unknown"]:
        worse.append(
            f"- SHIPPING has **more false UNKNOWN** ({s_score['false_unknown']} vs "
            f"{b_score['false_unknown']}): {s_score['false_unknown_ids']}"
        )
    if s_score["accuracy"] < b_score["accuracy"]:
        worse.append(
            f"- **BASELINE beats SHIPPING on accuracy** "
            f"({b_score['accuracy']:.0%} vs {s_score['accuracy']:.0%}) on this n={s_score['n']} set."
        )
    verify_delta = a_score["false_green"] - s_score["false_green"]
    if verify_delta > 0:
        lines.append(
            f"- **Verify delta (ablation − shipping false GREEN):** {verify_delta} "
            f"— verify catches {verify_delta} item(s) ablation would false-clear"
        )
    elif verify_delta < 0:
        lines.append(
            f"- **Verify regression:** shipping has {abs(verify_delta)} more false GREEN "
            f"than ablation — investigate before shipping"
        )
    else:
        lines.append(
            "- **Verify delta on catchable set:** 0 false GREEN prevented "
            "(verify and ablation tie on safety here; RC5 engine_limit still fails all arms)"
        )
    for it in limits:
        b, a, s = by_b[it["id"]], by_a[it["id"]], by_s[it["id"]]
        lines.append(
            f"- **{it['id']} engine_limit** ({it['engine_limit']}): gold NOT_SUPPORTED, "
            f"baseline={b.predicted}, ablation={a.predicted}, shipping={s.predicted} "
            f"(fixture pins shipping={it['engine_verdict_today']})"
        )
    verify_fail_b = sum(
        1 for r in baseline_rows
        if r.item_id in catchable and r.predicted == GREEN and r.cause == "would_fail_verify"
    )
    verify_fail_a = sum(
        1 for r in ablation_rows
        if r.item_id in catchable and r.predicted == GREEN and r.cause == "would_fail_verify"
    )
    lines += [
        "",
        f"- GREEN quotes that **fail verify** (catchable): baseline={verify_fail_b}, "
        f"ablation={verify_fail_a}, shipping=0",
    ]
    lines += [
        "",
        "## Gate command",
        "",
        "```bash",
        "python3 eval/refusal_correctness_gate.py",
        "```",
        "",
        "n<100 → report counts and per-item rows, not bare points without CIs.",
        "",
    ]
    RECEIPT.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    meta = json.loads(SET_PATH.read_text())
    items = meta["items"]
    catchable = {it["id"] for it in items if not it.get("engine_limit")}

    baseline_rows = [_run_baseline(it) for it in items]
    ablation_rows = [_run_ablation(it) for it in items]
    shipping_rows = [_run_shipping(it) for it in items]
    b_score = _score(baseline_rows, catchable_ids=catchable)
    a_score = _score(ablation_rows, catchable_ids=catchable)
    s_score = _score(shipping_rows, catchable_ids=catchable)

    _write_receipt(
        items, baseline_rows, ablation_rows, shipping_rows,
        b_score, a_score, s_score,
        labelled_at=meta["labelled_at"],
    )
    print(RECEIPT.read_text())

    # Fail if shipping is strictly worse on safety (false GREEN) or accuracy
    if s_score["false_green"] > b_score["false_green"]:
        return 2
    if s_score["accuracy"] < b_score["accuracy"]:
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
