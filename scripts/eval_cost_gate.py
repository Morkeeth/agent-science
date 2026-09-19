#!/usr/bin/env python3
"""Qwen PRIOR LOSS gate — cost with a dated price card + always-silent null arm.

The unchecked checklist row is "Cost from billing, with the price card's date
stated." This script separates those two objects on purpose:

  PRICE CARD   fixtures/price-card/parallel.json  (required; date stated)
  BILLING      fixtures/billing/invoice.json      (required for GREEN; RED if absent)

Three accuracy arms on the held-out refusal set (offline — Parallel spend is $0
for every arm, which is itself a finding):

  NULL      always UNSOURCED / UNKNOWN — the trivial refuse-everything floor
  BASELINE  substring must_contain anywhere in the document (two-hour naive arm)
  SHIPPING  StringLocator + verify + judge_claim

Compound cost arm: re-runs the offline compound exhibit path, prices the metered
parallel_calls against the dated Search API card, and compares the hardcoded
constant in measure_compounding.py so a carried figure cannot hide.

Run:
  python3 scripts/eval_cost_gate.py

Exit:
  0  ran; price card OK; prints FINDING (billing may still be RED)
  2  price card missing / undated / unreadable
  3  --require-billing and invoice absent or invalid
"""
from __future__ import annotations

import argparse
import html
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from clearance import instruments  # noqa: E402
from clearance.facts import Claim, judge_claim  # noqa: E402
from clearance.locate import DEFAULT  # noqa: E402
from clearance.verdict import GREEN, UNKNOWN  # noqa: E402

sys.path.insert(0, str(ROOT / "scripts"))
from eval_stats import format_ci, mcnemar_exact  # noqa: E402

SET = json.loads((ROOT / "fixtures/refusal-correctness/set.json").read_text())
PRICE_CARD = ROOT / "fixtures/price-card/parallel.json"
BILLING = ROOT / "fixtures/billing/invoice.json"
COMPOUND_SCRIPT = ROOT / "scripts/compound_exhibit_receipt.py"
MEASURE_COMPOUNDING = ROOT / "measure_compounding.py"


def _visible(raw: str) -> str:
    raw = re.sub(r"<(script|style).*?</\1>", " ", raw, flags=re.S | re.I)
    txt = html.unescape(re.sub(r"<[^>]+>", " ", raw))
    return re.sub(r"\s+", " ", txt).strip()


def _gold(expected: str) -> str:
    return GREEN if expected == "SUPPORTED" else UNKNOWN


def _null_verdict(_body: str, _claim: str, _must: str) -> str:
    """Always-silent null — refuse everything. $0. Can beat us if we over-assert."""
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


def _load_price_card() -> dict:
    if not PRICE_CARD.exists():
        raise SystemExit(f"PRICE CARD MISSING: {PRICE_CARD}")
    card = json.loads(PRICE_CARD.read_text())
    if not card.get("retrieved_at"):
        raise SystemExit("PRICE CARD UNDATED: retrieved_at required")
    rates = card.get("search_api_usd_per_request") or {}
    proc = card.get("default_processor_for_agent_science")
    if proc not in rates:
        raise SystemExit(
            f"PRICE CARD: default processor {proc!r} not in search_api_usd_per_request"
        )
    return card


def _billing_status() -> dict:
    if not BILLING.exists():
        return {
            "status": "RED",
            "reason": "fixtures/billing/invoice.json absent — not a price card",
            "path": str(BILLING),
        }
    try:
        inv = json.loads(BILLING.read_text())
    except json.JSONDecodeError as e:
        return {"status": "RED", "reason": f"invoice JSON invalid: {e}", "path": str(BILLING)}
    required = ("provider", "period_start", "period_end", "currency", "line_items", "exported_at")
    missing = [k for k in required if k not in inv]
    if missing:
        return {
            "status": "RED",
            "reason": f"invoice missing fields: {missing}",
            "path": str(BILLING),
        }
    if not isinstance(inv["line_items"], list):
        return {"status": "RED", "reason": "line_items must be a list", "path": str(BILLING)}
    return {
        "status": "GREEN",
        "reason": "invoice present with required fields",
        "path": str(BILLING),
        "total": inv.get("total"),
        "period": f"{inv['period_start']} → {inv['period_end']}",
        "provider": inv["provider"],
    }


def _accuracy_arms() -> dict:
    rows = []
    scores = {"NULL": 0, "BASELINE": 0, "SHIPPING": 0}
    # McNemar: null-only / shipping-only ; baseline-only / shipping-only
    null_only = ship_vs_null = 0
    base_only = ship_vs_base = 0

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
        scores["NULL"] += int(n_ok)
        scores["BASELINE"] += int(b_ok)
        scores["SHIPPING"] += int(s_ok)

        if n_ok and not s_ok:
            null_only += 1
        if s_ok and not n_ok:
            ship_vs_null += 1
        if b_ok and not s_ok:
            base_only += 1
        if s_ok and not b_ok:
            ship_vs_base += 1

        rows.append(
            {
                "id": item["id"],
                "gold": item["expected"],
                "null": null_v,
                "baseline": base_v,
                "shipping": ship_v,
                "n_ok": n_ok,
                "b_ok": b_ok,
                "s_ok": s_ok,
            }
        )

    n = len(SET["items"])
    p_null, note_null = mcnemar_exact(null_only, ship_vs_null)
    p_base, note_base = mcnemar_exact(base_only, ship_vs_base)
    return {
        "n": n,
        "scores": scores,
        "rows": rows,
        "mcnemar_null_vs_shipping": {"p": p_null, "note": note_null, "b": null_only, "c": ship_vs_null},
        "mcnemar_baseline_vs_shipping": {
            "p": p_base,
            "note": note_base,
            "b": base_only,
            "c": ship_vs_base,
        },
    }


def _rederive_compound_parallel() -> dict:
    """Run offline compound exhibit and parse metered parallel_calls at object."""
    proc = subprocess.run(
        [sys.executable, str(COMPOUND_SCRIPT)],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    out = (proc.stdout or "") + (proc.stderr or "")
    receipt = ROOT / "docs/COMPOUND-EXHIBIT-2026-08-29.md"
    text = receipt.read_text() if receipt.exists() else out
    # Table row: | 2 | 1 | +1 | 2 |
    m = re.search(
        r"\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*[+-]?\d+\s*\|\s*(\d+)\s*\|",
        text,
    )
    boundary = re.search(
        r"Ground-truth Parallel calls at fake boundary \(Run A only\):\s*`(\d+)`",
        text,
    )
    if not m:
        return {
            "ok": False,
            "error": "could not parse compound parallel_calls from receipt",
            "exit": proc.returncode,
            "tail": out[-800:],
        }
    return {
        "ok": True,
        "exit": proc.returncode,
        "a_parallel": int(m.group(1)),
        "b_parallel": int(m.group(2)),
        "b_corpus_hits": int(m.group(3)),
        "boundary_a_ground_truth": int(boundary.group(1)) if boundary else None,
    }


def _effective_parallel_rate() -> tuple[float | None, str]:
    """Import measure_compounding's live PARALLEL_CALL (must come from the price card)."""
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "measure_compounding_cost_gate", MEASURE_COMPOUNDING
    )
    if spec is None or spec.loader is None:
        return None, "could not load measure_compounding.py"
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
    except Exception as e:
        return None, f"measure_compounding import failed: {e}"
    rate = getattr(mod, "PARALLEL_CALL", None)
    if rate is None:
        return None, "PARALLEL_CALL missing after import"
    return float(rate), "imported from measure_compounding.PARALLEL_CALL"


def _git_old_hardcoded_parallel() -> float | None:
    """Previous carried constant, if still visible in HEAD^ history of the file."""
    proc = subprocess.run(
        ["git", "log", "-p", "-n", "5", "--", "measure_compounding.py"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    matches = re.findall(r"^\+?PARALLEL_CALL\s*=\s*([0-9.]+)", proc.stdout, re.M)
    # Prefer an assignment that is not the current import-driven file.
    for m in matches:
        val = float(m)
        if abs(val - 0.005) < 1e-9 or abs(val - 0.001) < 1e-9:
            return val
    literal = re.findall(r"^PARALLEL_CALL\s*=\s*([0-9.]+)", proc.stdout, re.M)
    return float(literal[0]) if literal else None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--require-billing",
        action="store_true",
        help="exit 3 when fixtures/billing/invoice.json is absent or invalid",
    )
    args = ap.parse_args()

    try:
        card = _load_price_card()
    except SystemExit as e:
        print(f"FAIL  {e}")
        return 2

    proc = card["default_processor_for_agent_science"]
    unit = float(card["search_api_usd_per_request"][proc])
    billing = _billing_status()

    print("COST GATE — dated price card + null / baseline / shipping")
    print(f"Price card: {PRICE_CARD.relative_to(ROOT)}")
    print(f"  retrieved_at: {card['retrieved_at']}")
    print(f"  source_url:   {card['source_url']}")
    print(f"  processor:    {proc} @ ${unit:.4f} / Search API request")
    print(f"Billing:      {billing['status']} — {billing['reason']}")
    print()

    acc = _accuracy_arms()
    n = acc["n"]
    print("ACCURACY (held-out refusal set, offline — Parallel spend $0 every arm)")
    print(f"{'id':<6}{'gold':<14}{'null':<10}{'baseline':<10}{'shipping':<10}n b s")
    for r in acc["rows"]:
        print(
            f"{r['id']:<6}{r['gold']:<14}{r['null']:<10}{r['baseline']:<10}{r['shipping']:<10}"
            f"{r['n_ok']} {r['b_ok']} {r['s_ok']}"
        )
    print()
    print(f"NULL:      {format_ci(acc['scores']['NULL'], n)}")
    print(f"BASELINE:  {format_ci(acc['scores']['BASELINE'], n)}")
    print(f"SHIPPING:  {format_ci(acc['scores']['SHIPPING'], n)}")
    mn = acc["mcnemar_null_vs_shipping"]
    mb = acc["mcnemar_baseline_vs_shipping"]
    print(
        f"McNemar NULL vs SHIPPING:     p={mn['p']:.4f} ({mn['note']})"
    )
    print(
        f"McNemar BASELINE vs SHIPPING: p={mb['p']:.4f} ({mb['note']})"
    )

    null_beats = acc["scores"]["NULL"] > acc["scores"]["SHIPPING"]
    print()
    if null_beats:
        print(
            "FINDING (embarrassing): always-silent NULL beats SHIPPING on accuracy "
            f"({acc['scores']['NULL']}/{n} > {acc['scores']['SHIPPING']}/{n})."
        )
    else:
        print(
            "FINDING: always-silent NULL does NOT beat SHIPPING on accuracy "
            f"({acc['scores']['NULL']}/{n} vs {acc['scores']['SHIPPING']}/{n}). "
            "Cost, not accuracy, is where NULL wins tonight."
        )
    print(
        "FINDING: offline holdout Parallel spend is $0.0000 for NULL, BASELINE, and "
        "SHIPPING alike — a cost gate that only reads this set cannot discriminate arms."
    )

    print()
    print("COMPOUND COST (re-derived offline exhibit × dated Search API card)")
    compound = _rederive_compound_parallel()
    if not compound.get("ok"):
        print(f"COMPOUND PARSE FAIL: {compound.get('error')}")
        print(compound.get("tail", ""))
        return 2

    a_pc = compound["a_parallel"]
    b_pc = compound["b_parallel"]
    a_usd = a_pc * unit
    b_usd = b_pc * unit
    print(
        f"  metered parallel_calls  A={a_pc}  B={b_pc}  "
        f"corpus_hits_B={compound['b_corpus_hits']}  "
        f"(compound exit {compound['exit']})"
    )
    if compound.get("boundary_a_ground_truth") is not None:
        gt = compound["boundary_a_ground_truth"]
        print(f"  boundary ground-truth Parallel calls (Run A only): {gt}")
        if gt != a_pc:
            print(
                f"FINDING (embarrassing): meter reports A={a_pc} but fake-boundary "
                f"ground-truth is {gt} — parallel_calls under-counts the search door."
            )
    print(f"  priced @{proc} ${unit:.4f}/req → A=${a_usd:.4f}  B=${b_usd:.4f}")
    if a_usd:
        print(f"  compound saving (price-card): {1 - b_usd / a_usd:+.0%} on Parallel line")
    print(
        "  NOTE: price-card estimate, not an invoice. Billing status is "
        f"{billing['status']}."
    )

    effective, how = _effective_parallel_rate()
    old = _git_old_hardcoded_parallel()
    print()
    print("CARRIED FIGURE CHECK — measure_compounding.py PARALLEL_CALL")
    print(f"  effective PARALLEL_CALL = {effective} ({how})")
    print(f"  card fast      = ${card['search_api_usd_per_request']['fast']:.4f}")
    print(f"  card advanced  = ${card['search_api_usd_per_request']['advanced']:.4f}")
    if effective is not None and abs(effective - unit) < 1e-9:
        print(f"  OK — measure_compounding tracks default processor {proc!r} on today's card")
    elif effective is not None:
        print(
            f"FINDING: measure_compounding PARALLEL_CALL ${effective:.4f} ≠ "
            f"card {proc} ${unit:.4f}"
        )
    if old is not None and abs(old - card["search_api_usd_per_request"]["advanced"]) < 1e-9:
        print(
            f"FINDING (was carried): prior hardcoded PARALLEL_CALL=${old:.4f} matched "
            f"Search API *advanced*, not default {proc!r} (${unit:.4f}) — "
            f"{old / unit:.0f}× overstatement if Fast was the intended tier."
        )
    elif old is not None:
        print(f"  prior literal PARALLEL_CALL seen in git log: ${old:.4f}")

    print()
    print("BILLING CHECKLIST ROW")
    if billing["status"] == "GREEN":
        print(
            f"  GREEN — invoice {billing.get('period')} total={billing.get('total')} "
            f"provider={billing.get('provider')}"
        )
        print("  hack.md 'Cost from billing' may be ticked only after a human reads the invoice.")
    else:
        print(f"  RED — {billing['reason']}")
        print(
            "  Do NOT tick hack.md 'Cost from billing'. Price-card arm is shipped; "
            "invoice remains Oscar console export → fixtures/billing/invoice.json."
        )

    if args.require_billing and billing["status"] != "GREEN":
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
