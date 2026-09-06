#!/usr/bin/env python3
"""Qwen eval gate — cost from billing, with price-card date stated.

Baseline arm (naive two-hour team): multiply receipt Parallel call counts by the
public price card. That invents a USD figure. It is not billing.

Shipping arm: accept only a real billing export (fixtures/billing/export.json or
BILLING_EXPORT_PATH). Missing export → REFUSE. Inventing dollars from a price
card is not allowed on the shipping arm.

Call counts are re-derived from receipt files at run time — not carried from
this prompt.

Run: python3 scripts/eval_cost_from_billing.py
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CARD_PATH = ROOT / "fixtures/billing/PRICE-CARD.json"
EXPORT_DEFAULT = ROOT / "fixtures/billing/export.json"

# How to re-derive parallel_calls from each receipt object (no hardcoded USD).
RECEIPT_EXTRACTORS = [
    {
        "id": "compound-mini-offline",
        "receipt": "docs/COMPOUND-EXHIBIT-2026-08-29.md",
        "kind": "compound_table",
    },
    {
        "id": "hosted-fresh-compound",
        "receipt": "docs/RECEIPT-live-compound-exhibit-2026-08-31.md",
        "kind": "run_ab_dict",
        "marker": "compound-fresh-c1eb52fe",
    },
    {
        "id": "longrun-0902",
        "receipt": "docs/LONG-RUN-RECEIPT-2026-09-02.md",
        "kind": "json_parallel_fields",
    },
]


def _load_card() -> dict:
    if not CARD_PATH.is_file():
        raise SystemExit(f"MISSING price card: {CARD_PATH}")
    card = json.loads(CARD_PATH.read_text())
    for key in ("fetched_at", "source_url", "usd_per_request", "verbatim_span"):
        if key not in card:
            raise SystemExit(f"PRICE CARD incomplete — missing {key}")
    return card


def _extract_compound_table(text: str) -> list[tuple[str, int]]:
    """Parse | Run A parallel_calls | Run B parallel_calls | table body."""
    # Header then separator then data row with integers.
    m = re.search(
        r"\|\s*Run A parallel_calls\s*\|\s*Run B parallel_calls\s*\|[^\n]*\n"
        r"\|[-:\s|]+\|\n"
        r"\|\s*(\d+)\s*\|\s*(\d+)\s*\|",
        text,
    )
    if not m:
        raise SystemExit("could not parse compound exhibit parallel_calls table")
    return [("A", int(m.group(1))), ("B", int(m.group(2)))]


def _extract_run_ab_dict(text: str, marker: str) -> list[tuple[str, int]]:
    idx = text.find(marker)
    if idx < 0:
        raise SystemExit(f"marker not found in receipt: {marker!r}")
    chunk = text[idx : idx + 2500]
    rows = []
    for label in ("A", "B"):
        m = re.search(
            rf"RUN_{label}\s+\{{[^}}]*'parallel_calls':\s*(\d+)",
            chunk,
        )
        if not m:
            # also allow double quotes
            m = re.search(
                rf'RUN_{label}\s+\{{[^}}]*"parallel_calls":\s*(\d+)',
                chunk,
            )
        if not m:
            raise SystemExit(f"could not parse RUN_{label} parallel_calls after {marker!r}")
        rows.append((label, int(m.group(1))))
    return rows


def _extract_json_parallel_fields(text: str) -> list[tuple[str, int]]:
    """First two \"parallel_calls\": N occurrences in a long-run receipt (A then B)."""
    found = re.findall(r'"parallel_calls"\s*:\s*(\d+)', text)
    if len(found) < 2:
        raise SystemExit(
            f"expected ≥2 parallel_calls JSON fields in long-run receipt, got {len(found)}"
        )
    return [("A", int(found[0])), ("B", int(found[1]))]


def _derive_runs() -> list[dict]:
    runs = []
    for spec in RECEIPT_EXTRACTORS:
        path = ROOT / spec["receipt"]
        if not path.is_file():
            raise SystemExit(f"MISSING receipt: {path}")
        text = path.read_text()
        kind = spec["kind"]
        if kind == "compound_table":
            pairs = _extract_compound_table(text)
        elif kind == "run_ab_dict":
            pairs = _extract_run_ab_dict(text, spec["marker"])
        elif kind == "json_parallel_fields":
            pairs = _extract_json_parallel_fields(text)
        else:
            raise SystemExit(f"unknown extractor kind: {kind}")
        for label, calls in pairs:
            runs.append(
                {
                    "id": f"{spec['id']}-{label}",
                    "receipt": spec["receipt"],
                    "parallel_calls": calls,
                }
            )
    return runs


def _baseline_usd(card: dict, runs: list[dict]) -> dict:
    unit = float(card["usd_per_request"])
    rows = []
    total_calls = 0
    total_usd = 0.0
    for run in runs:
        calls = int(run["parallel_calls"])
        usd = calls * unit
        total_calls += calls
        total_usd += usd
        rows.append(
            {
                "id": run["id"],
                "receipt": run["receipt"],
                "parallel_calls": calls,
                "invented_usd": round(usd, 6),
            }
        )
    return {
        "arm": "baseline_price_card_x_receipts",
        "price_card_fetched_at": card["fetched_at"],
        "price_card_source_url": card["source_url"],
        "verbatim_span": card["verbatim_span"],
        "usd_per_request": unit,
        "total_parallel_calls": total_calls,
        "invented_usd_total": round(total_usd, 6),
        "rows": rows,
        "is_billing": False,
        "warning": "ESTIMATE ONLY — not from a billing statement",
    }


def _shipping_from_export(path: Path) -> dict:
    if not path.is_file():
        return {
            "arm": "shipping_billing_export",
            "status": "REFUSE",
            "cause": "billing_export_missing",
            "expected_path": str(path),
            "hint": "Drop a real Parallel/GCP billing export at fixtures/billing/export.json "
            "or set BILLING_EXPORT_PATH. Do not invent line items.",
            "is_billing": False,
            "usd_total": None,
        }
    raw = json.loads(path.read_text())
    if not isinstance(raw, dict) or "line_items" not in raw:
        return {
            "arm": "shipping_billing_export",
            "status": "REFUSE",
            "cause": "billing_export_malformed",
            "expected": "JSON object with line_items[{run_id, usd}]",
            "is_billing": False,
            "usd_total": None,
        }
    items = raw["line_items"]
    if not isinstance(items, list) or not items:
        return {
            "arm": "shipping_billing_export",
            "status": "REFUSE",
            "cause": "billing_export_empty",
            "is_billing": False,
            "usd_total": None,
        }
    total = 0.0
    for item in items:
        if "usd" not in item:
            return {
                "arm": "shipping_billing_export",
                "status": "REFUSE",
                "cause": "billing_line_missing_usd",
                "is_billing": False,
                "usd_total": None,
            }
        total += float(item["usd"])
    return {
        "arm": "shipping_billing_export",
        "status": "SOURCED",
        "export_path": str(path),
        "export_statement_date": raw.get("statement_date"),
        "line_items": len(items),
        "usd_total": round(total, 6),
        "is_billing": True,
    }


def main() -> int:
    card = _load_card()
    runs = _derive_runs()
    baseline = _baseline_usd(card, runs)
    export_path = Path(os.environ.get("BILLING_EXPORT_PATH") or EXPORT_DEFAULT)
    shipping = _shipping_from_export(export_path)

    print("Qwen gate · cost from billing")
    print(f"Price card: {card['source_url']} · fetched_at={card['fetched_at']}")
    print(f"Verbatim: {card['verbatim_span']}")
    print()
    print(
        f"BASELINE (invented): {baseline['total_parallel_calls']} Parallel calls "
        f"× ${baseline['usd_per_request']:.3f} = "
        f"${baseline['invented_usd_total']:.4f}  [{baseline['warning']}]"
    )
    for row in baseline["rows"]:
        print(
            f"  {row['id']}: calls={row['parallel_calls']} "
            f"invented_usd=${row['invented_usd']:.4f}  ← {row['receipt']}"
        )
    print()
    if shipping["status"] == "SOURCED":
        print(
            f"SHIPPING (billing): SOURCED  usd_total=${shipping['usd_total']:.4f}  "
            f"lines={shipping['line_items']}  "
            f"statement_date={shipping.get('export_statement_date')}"
        )
        delta = shipping["usd_total"] - baseline["invented_usd_total"]
        print(f"Delta (shipping - baseline invented): ${delta:.4f}")
        print(
            "FINDING: billing export present — compare invented estimate to billed "
            "total; do not treat either as the other."
        )
        return 0

    print(
        f"SHIPPING (billing): REFUSE · {shipping['cause']} · "
        f"{shipping.get('expected_path') or shipping.get('expected')}"
    )
    print(
        "FINDING: baseline invents a dollar figure from the public price card; "
        "shipping correctly refuses without a billing export. "
        "Any submit-pack cost claim is UNSOURCED until Oscar drops a real export."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
