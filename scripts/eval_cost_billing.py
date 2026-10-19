#!/usr/bin/env python3
"""PRIOR LOSS gate — cost from billing, with the price card's date stated.

Without a Parallel billing export this gate MUST go RED / BLOCKED. Estimated
cost from the public price card is printed for orientation only and is not
accepted as "from billing".

Billing export path (first match wins):
  $PARALLEL_BILLING_CSV
  fixtures/billing/parallel-export.csv

Price card:
  fixtures/artifact-claims/parallel-price-card.json  (pinned)
  optional refresh: --refresh-price-card (network)

Run: python3 scripts/eval_cost_billing.py
"""
from __future__ import annotations

import csv
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
CARD = ROOT / "fixtures/artifact-claims/parallel-price-card.json"
BILLING_CANDIDATES = [
    Path(os.environ["PARALLEL_BILLING_CSV"]) if os.environ.get("PARALLEL_BILLING_CSV") else None,
    ROOT / "fixtures/billing/parallel-export.csv",
]
PRICE_URL = "https://docs.parallel.ai/getting-started/pricing.md"


def _load_card() -> dict:
    return json.loads(CARD.read_text())


def _refresh_card() -> dict:
    req = Request(PRICE_URL, headers={"User-Agent": "agent-science-cost-gate/1.0"})
    with urlopen(req, timeout=30) as resp:  # noqa: S310 — explicit public docs URL
        body = resp.read().decode("utf-8", errors="replace")
    # Keep prior numeric pin; stamp refresh time + excerpt presence checks.
    card = _load_card()
    card["refreshed_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    card["refresh_url"] = PRICE_URL
    card["refresh_saw_turbo"] = "turbo" in body.lower()
    card["refresh_saw_advanced"] = "advanced" in body.lower()
    CARD.write_text(json.dumps(card, indent=2) + "\n")
    return card


def _find_billing() -> Path | None:
    for p in BILLING_CANDIDATES:
        if p is not None and p.is_file() and p.stat().st_size > 0:
            return p
    return None


def _estimate_from_receipts(card: dict) -> dict:
    """Orientation only — sealed/offline Parallel call counts × advanced unit price."""
    # Offline compound receipt: A=2, B=1 → 3 Parallel-shaped calls in the exhibit.
    offline_calls = 3
    # Sealed hosted prediction used A=1→B=0 on a warm shelf (1 live call class).
    sealed_calls = 1
    unit = float(card["search_usd_per_request"]["advanced"])
    return {
        "price_card_fetched_at": card.get("fetched_at"),
        "unit_usd_advanced": unit,
        "offline_compound_parallel_calls": offline_calls,
        "offline_compound_estimate_usd": round(offline_calls * unit, 6),
        "sealed_hosted_parallel_calls": sealed_calls,
        "sealed_hosted_estimate_usd": round(sealed_calls * unit, 6),
        "disclaimer": "ESTIMATE from price card × receipt call counts — NOT from billing",
    }


def _sum_billing(path: Path) -> dict:
    """Accept CSV with a numeric amount column named amount_usd|cost|total|usd."""
    with path.open(newline="") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise RuntimeError(f"billing CSV has no header: {path}")
        fields = {name.lower(): name for name in reader.fieldnames}
        amount_key = None
        for cand in ("amount_usd", "cost_usd", "total_usd", "usd", "cost", "amount", "total"):
            if cand in fields:
                amount_key = fields[cand]
                break
        if amount_key is None:
            raise RuntimeError(
                f"billing CSV missing amount column (tried amount_usd/cost/…): {list(fields)}"
            )
        total = 0.0
        n = 0
        for row in reader:
            raw = (row.get(amount_key) or "").strip().replace("$", "")
            if not raw:
                continue
            total += float(raw)
            n += 1
    return {"rows": n, "amount_usd": round(total, 6), "path": str(path)}


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    refresh = "--refresh-price-card" in argv

    print("COST-FROM-BILLING GATE")
    print("Price card must be dated. Amount must come from a billing export.\n")

    if refresh:
        try:
            card = _refresh_card()
            print(f"Refreshed price card → {CARD}")
        except Exception as exc:  # noqa: BLE001 — gate must name the failure
            print(f"REFRESH FAILED: {exc}")
            print("Falling back to pinned card.")
            card = _load_card()
    else:
        card = _load_card()

    fetched_at = card.get("fetched_at") or card.get("refreshed_at") or "UNKNOWN"
    print(f"Price card date: {fetched_at}")
    print(f"Price card path: {CARD}")
    print(
        "Search unit (advanced): "
        f"${card['search_usd_per_request']['advanced']} / request "
        f"(from {card.get('source_url')})"
    )

    estimate = _estimate_from_receipts(card)
    print("\nEstimate (NOT billing) — orientation only:")
    for k, v in estimate.items():
        print(f"  {k}: {v}")

    billing = _find_billing()
    if billing is None:
        print("\nBLOCKED: no Parallel billing export found.")
        print("  looked for $PARALLEL_BILLING_CSV and fixtures/billing/parallel-export.csv")
        print("  hack.md PRIOR LOSS checkbox 'Cost from billing' stays UNCHECKED.")
        print("GATE RED — price card dated, billing absent.")
        return 2

    try:
        summed = _sum_billing(billing)
    except Exception as exc:  # noqa: BLE001
        print(f"\nBLOCKED: billing export unreadable: {exc}")
        return 2

    print("\nFROM BILLING:")
    for k, v in summed.items():
        print(f"  {k}: {v}")
    print(
        f"GATE OK — billing ${summed['amount_usd']} with price card dated {fetched_at}."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
