#!/usr/bin/env python3
"""Qwen PRIOR LOSS gate — cost from billing, with the price card's date stated.

This script never invents a spend figure. It:
  1. Loads the pinned Parallel Search price card (date + source URL).
  2. Looks for observed billing (PARALLEL_BILLING_JSON or console export).
  3. Prints UNKNOWN when billing is not available — that is the honest result.

Baseline arm: carry the order-of-magnitude guess from measure_compounding.py
(~$0.005 / search) without stating a price-card date.
Shipping arm: price card dated + billing observed or explicitly UNKNOWN.

Run: python3 scripts/eval_cost_from_billing.py
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CARD = ROOT / "fixtures/price-card/parallel-search-2026-09-07.json"
GUESS_SRC = ROOT / "measure_compounding.py"


def _baseline_guess() -> tuple[float | None, str]:
    text = GUESS_SRC.read_text()
    m = re.search(r"Parallel\s*~?\$([0-9.]+)\s*per search", text)
    if not m:
        return None, "no guess found in measure_compounding.py"
    return float(m.group(1)), f"undated guess from {GUESS_SRC.name}: ${m.group(1)} per search"


def _load_card() -> dict:
    return json.loads(CARD.read_text())


def _observed_billing() -> tuple[str, dict | None]:
    path = os.environ.get("PARALLEL_BILLING_JSON", "").strip()
    if path and Path(path).exists():
        data = json.loads(Path(path).read_text())
        return "file", data
    # Never scrape console cookies. No key on this VM → UNKNOWN.
    if not os.environ.get("PARALLEL_API_KEY") and not (
        Path.home() / ".config/keys/parallel.key"
    ).exists():
        return "unavailable", None
    return "key_present_no_invoice", None


def main() -> int:
    print("COST-FROM-BILLING EVAL — price card dated; spend never invented\n")
    guess, guess_detail = _baseline_guess()
    card = _load_card()
    card_rate = card["search_api"]["implied_per_request_basic_or_advanced_usd"]
    card_date = card["fetched_at"][:10]
    print("Arms")
    print(f"  Baseline: {guess_detail}")
    print(
        f"  Shipping: price card {card_date} from {card['source_url']} "
        f"→ Search Basic/Advanced ${card_rate} / request "
        f"({card['search_api']['unit']})"
    )
    print()

    source, billing = _observed_billing()
    print("Observed spend (billing object)")
    if source == "file" and billing is not None:
        print(f"  SOURCE: {os.environ['PARALLEL_BILLING_JSON']}")
        print(f"  PAYLOAD keys: {sorted(billing.keys())}")
        spend = billing.get("usd_total")
        print(f"  usd_total: {spend}")
        status = "MEASURED"
    elif source == "key_present_no_invoice":
        print("  SOURCE: PARALLEL_API_KEY present, but no invoice/export attached")
        print("  usd_total: UNKNOWN")
        status = "UNKNOWN"
        spend = None
    else:
        print("  SOURCE: none (no PARALLEL_API_KEY / parallel.key / PARALLEL_BILLING_JSON)")
        print("  usd_total: UNKNOWN")
        status = "UNKNOWN"
        spend = None

    print()
    print("Result")
    print(f"  price_card_date: {card_date}")
    print(f"  price_card_rate_usd_per_search: {card_rate}")
    print(f"  baseline_guess_usd_per_search: {guess}")
    print(f"  billing_status: {status}")
    print(f"  observed_usd_total: {spend}")
    if status == "UNKNOWN":
        print(
            "FINDING: gate ran; billing object absent. "
            "Do not print a spend number. Oscar: attach Parallel invoice "
            "as PARALLEL_BILLING_JSON to close this row."
        )
        # Rate card vs undated guess — informational only.
        if guess is not None and abs(guess - card_rate) < 1e-9:
            print(
                f"NOTE: undated baseline guess ${guess} matches dated card "
                f"${card_rate} — still not billing."
            )
        elif guess is not None:
            print(
                f"NOTE: undated baseline guess ${guess} differs from dated card "
                f"${card_rate}."
            )
    else:
        print("FINDING: billing measured from attached export.")

    out = ROOT / "docs" / "COST-FROM-BILLING-2026-09-07.json"
    out.write_text(json.dumps({
        "price_card_date": card_date,
        "price_card_path": str(CARD.relative_to(ROOT)),
        "price_card_rate_usd_per_search": card_rate,
        "baseline_guess_usd_per_search": guess,
        "billing_status": status,
        "observed_usd_total": spend,
        "source": source,
    }, indent=2) + "\n")
    print(f"\nWrote {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
