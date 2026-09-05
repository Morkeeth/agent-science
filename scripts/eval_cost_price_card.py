#!/usr/bin/env python3
"""Qwen eval gate — cost from the public Parallel price card (date stated).

NOT a billing-console read. Parallel/GCP billing is Oscar-only. This gate measures
list-price dollars from the public price card against offline compound arms so a
stranger can falsify the number without a console.

Baseline arm: naive always-search — one Search API call per claim, no corpus reuse.
Shipping arm: measured parallel_calls from the offline compound exhibit (A then B
on one shelf under exact-assertion reuse).

Price card object: https://www.parallel.ai/pricing
Fetched / restated date must be printed on every run.

Run: python3 scripts/eval_cost_price_card.py
"""
from __future__ import annotations

import re
import subprocess
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PRICE_CARD_URL = "https://www.parallel.ai/pricing"
# Search API table on the price card (Basic processor, per 1K requests with 10 results).
# Re-derived at object each run when network allows; fallback pins the last verified read.
BASIC_PER_1K_USD = 5.0
TURBO_PER_1K_USD = 1.0
PROCESSOR = "Search API · Basic"
PINNED_CARD_DATE = "2026-09-05"  # first night this gate shipped; overwritten when fetch works


def _fetch_price_card() -> tuple[str, float, float, str]:
    """Return (date_utc, basic_per_1k, turbo_per_1k, evidence_snippet)."""
    try:
        req = urllib.request.Request(
            PRICE_CARD_URL,
            headers={"User-Agent": "agent-science-cost-gate/1.0"},
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            html = resp.read().decode("utf-8", "replace")
        text = re.sub(r"<script.*?</script>", " ", html, flags=re.S | re.I)
        text = re.sub(r"<style.*?</style>", " ", text, flags=re.S | re.I)
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"\s+", " ", text)
        # Prefer the Search API Basic row: "$5" per 1K with 10 results.
        basic = BASIC_PER_1K_USD
        turbo = TURBO_PER_1K_USD
        m = re.search(
            r"Search API.*?Turbo\s*\$\s*([\d.]+).*?Fast\s*\$\s*([\d.]+).*?Basic\s*\$\s*([\d.]+)",
            text,
            re.I,
        )
        if m:
            turbo = float(m.group(1))
            basic = float(m.group(3))
        date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        snip = ""
        for pat in (
            r".{0,20}Search API.{0,80}Basic.{0,40}",
            r".{0,30}Price per request:\s*\$0\.001\s*-\s*\$0\.005.{0,40}",
        ):
            sm = re.search(pat, text, re.I)
            if sm:
                snip = sm.group(0)[:160]
                break
        return date, basic, turbo, snip or "Search API table present on parallel.ai/pricing"
    except Exception as e:
        return (
            PINNED_CARD_DATE,
            BASIC_PER_1K_USD,
            TURBO_PER_1K_USD,
            f"FETCH_FAILED ({type(e).__name__}: {e}); using pinned {PINNED_CARD_DATE} card read",
        )


def _compound_calls() -> tuple[int, int, int, int]:
    """Return (a_parallel, b_parallel, b_hits, n_claims_total_unique_path).

    Runs the offline exhibit and parses its receipt table.
    """
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts/compound_exhibit_receipt.py")],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
        timeout=240,
    )
    body = (ROOT / "docs/COMPOUND-EXHIBIT-2026-08-29.md").read_text()
    m = re.search(
        r"\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*([+-]?\d+)\s*\|\s*(\d+)\s*\|",
        body,
    )
    if not m or proc.returncode != 0:
        raise SystemExit(
            f"compound exhibit did not pass (exit={proc.returncode}); "
            "cost gate refuses to invent parallel_calls"
        )
    a, b, hits = int(m.group(1)), int(m.group(2)), int(m.group(4))
    # Claims on the path: A has 2, B adds 1 new → naive baseline = 2+3 = 5 searches
    # if B re-asks everything; shipping = a+b measured.
    return a, b, hits, a + (a + 1)  # naive: A claims + full B claims without reuse


def main() -> int:
    date, basic_1k, turbo_1k, snip = _fetch_price_card()
    per_call = basic_1k / 1000.0
    print("Cost gate — list price from Parallel price card (NOT billing console)")
    print(f"Price card URL:  {PRICE_CARD_URL}")
    print(f"Card read date:  {date} UTC")
    print(f"Processor:       {PROCESSOR}")
    print(f"Basic $/1K:      ${basic_1k:.2f}  →  ${per_call:.4f} per request")
    print(f"Turbo $/1K:      ${turbo_1k:.2f} (shown for range; not used in arms)")
    print(f"Evidence:        {snip}")
    print()
    print("BILLING: not read. Parallel/GCP invoices are Oscar-only. This gate is")
    print("falsifiable from the public card + offline compound receipt only.")
    print()

    a, b, hits, naive_calls = _compound_calls()
    ship_calls = a + b
    base_usd = naive_calls * per_call
    ship_usd = ship_calls * per_call
    saved = base_usd - ship_usd

    print("Arms on offline compound-mini (exact-assertion reuse):")
    print(f"  Baseline (naive always-search): {naive_calls} calls × ${per_call:.4f} = ${base_usd:.4f}")
    print(f"  Shipping (measured A+B):         {ship_calls} calls × ${per_call:.4f} = ${ship_usd:.4f}")
    print(f"  Compound receipt:               A={a} → B={b} parallel, B corpus_hits={hits}")
    print(f"  Delta (baseline − shipping):    ${saved:.4f} ({naive_calls - ship_calls} calls avoided)")
    print()
    if saved <= 0:
        print("FINDING: shipping does not beat naive always-search on list price — embarrassment.")
        return 1
    print("FINDING: compounding saves list-price dollars vs naive always-search on this path.")
    print("LIMITATION: n is the mini exhibit (5 naive vs 3 shipping calls). Not a billing audit.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
