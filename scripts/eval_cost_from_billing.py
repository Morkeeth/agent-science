#!/usr/bin/env python3
"""Qwen PRIOR LOSS gate — Cost from billing, with the price card's date stated.

Re-derive every dollar at its object. Do not carry rates from docs or memory.

Price card object:
  fixtures/price-cards/parallel-search-advanced.json
  (fetched from https://docs.parallel.ai/resources/pricing — rate PARSED from body)

Code object for mode:
  clearance.search.find_sources default mode="advanced"

Arms (compound-mini claim counts measured from compound_exhibit_receipt fixtures):
  ALWAYS_SILENT   — 0 Parallel calls. Naive team that skips search. $0.
  NAIVE_NO_REUSE  — one Parallel Search per claim on A and on B (no registry).
  SHIPPING        — measured parallel_calls from offline compound exhibit A→B.

Correctness arm (same held-out RC set as baseline/ablation):
  ALWAYS_SILENT → always UNKNOWN
  SHIPPING      → judge_claim DEFAULT path (same as eval_refusal_baseline)

Honesty: this is a *price-card estimate*, not Parallel console billing. Without an
API key we cannot open the invoice object. The card date is printed every run.

Run: python3 scripts/eval_cost_from_billing.py
"""
from __future__ import annotations

import html
import inspect
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from clearance import instruments  # noqa: E402
from clearance.facts import Claim, judge_claim  # noqa: E402
from clearance.locate import DEFAULT  # noqa: E402
from clearance.search import find_sources  # noqa: E402
from clearance.verdict import GREEN, UNKNOWN  # noqa: E402

sys.path.insert(0, str(ROOT / "scripts"))
from eval_stats import format_ci, mcnemar_exact  # noqa: E402

CARD_PATH = ROOT / "fixtures/price-cards/parallel-search-advanced.json"
SET = json.loads((ROOT / "fixtures/refusal-correctness/set.json").read_text())

def _load_cer():
    """Load compound_exhibit_receipt.py (scripts/ is not a package)."""
    import runpy

    path = ROOT / "scripts/compound_exhibit_receipt.py"
    ns = runpy.run_path(str(path), run_name="compound_exhibit_receipt")
    return ns


CER = _load_cer()


def _cer_claims(key: str) -> int:
    return len(CER["_OFFLINE_CLAIMS"][key])


def _parse_rate_from_card(card: dict) -> tuple[float, str]:
    """Parse USD/1000 for advanced Search from the stored markdown body."""
    body = card.get("body_markdown") or ""
    m = re.search(
        r"Per 1,?000 [`']?basic[`']? or [`']?advanced[`']? requests[^\n]*\|\s*(\d+(?:\.\d+)?)",
        body,
        re.I,
    )
    if not m:
        m = re.search(
            r"basic[`']? or [`']?advanced[`']?[^\n]*?(\d+)\s*/\s*1,?000",
            body,
            re.I,
        )
    if not m:
        raise SystemExit(
            f"FAILED to parse advanced Search rate from {CARD_PATH} body — "
            "refetch fixtures/price-cards/parallel-search-advanced.json"
        )
    return float(m.group(1)), m.group(0).strip()[:120]


def _usd(calls: int, per_1000: float) -> float:
    return calls * (per_1000 / 1000.0)


def _visible(raw: str) -> str:
    raw = re.sub(r"<(script|style).*?</\1>", " ", raw, flags=re.S | re.I)
    txt = html.unescape(re.sub(r"<[^>]+>", " ", raw))
    return re.sub(r"\s+", " ", txt).strip()


def _gold(expected: str) -> str:
    return GREEN if expected == "SUPPORTED" else UNKNOWN


def _silent_verdict(url: str, body: str, claim: str, must_contain: str) -> str:
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


def _score_arm(name: str, fn) -> dict:
    correct = 0
    rows = []
    for item in SET["items"]:
        doc_path = ROOT / item["document"]
        body = _visible(doc_path.read_text())
        url = f"file://{doc_path.name}"
        gold = _gold(item["expected"])
        got = fn(url, body, item["claim"], item["must_contain"])
        ok = got == gold
        correct += int(ok)
        rows.append((item["id"], gold, got, ok))
    n = len(SET["items"])
    return {"name": name, "correct": correct, "n": n, "rows": rows}


def _measure_shipping_parallel() -> tuple[int, int, int]:
    """Run offline compound exhibit path; return (A, B, total) parallel_calls."""
    run = CER["_run_offline"]()
    if run.get("error"):
        raise SystemExit(f"compound offline failed: {run['error']}")
    a = int(run["a"]["parallel_calls"])
    b = int(run["b"]["parallel_calls"])
    return a, b, a + b


def main() -> int:
    if not CARD_PATH.exists():
        print(f"MISSING price card {CARD_PATH}")
        return 1

    card = json.loads(CARD_PATH.read_text())
    per_1000, parse_hit = _parse_rate_from_card(card)
    # Prefer re-parsed body over any stored number — never trust a carried field alone.
    stored = card.get("usd_per_1000_parsed")
    if stored is not None and float(stored) != per_1000:
        print(
            f"MISMATCH stored usd_per_1000_parsed={stored} vs body-parsed={per_1000}"
        )
        return 1

    mode_default = inspect.signature(find_sources).parameters["mode"].default
    if mode_default != "advanced":
        print(
            f"MODE DRIFT: find_sources default is {mode_default!r}, "
            f"price card is for advanced — update card or code"
        )
        return 1

    claims_a = _cer_claims("A")
    claims_b = _cer_claims("B")
    naive_calls = claims_a + claims_b  # every claim pays; no registry reuse
    silent_calls = 0

    ship_a, ship_b, ship_total = _measure_shipping_parallel()

    silent = _score_arm("ALWAYS_SILENT", _silent_verdict)
    shipping = _score_arm("SHIPPING", _shipping_verdict)

    # McNemar silent vs shipping on RC set
    b_only = c_only = 0
    for sr, hr in zip(silent["rows"], shipping["rows"]):
        s_ok, h_ok = sr[3], hr[3]
        if s_ok and not h_ok:
            b_only += 1
        if h_ok and not s_ok:
            c_only += 1
    p_mc = mcnemar_exact(b_only, c_only)

    print("COST-FROM-BILLING EVAL — price card estimate (not console invoice)")
    print(f"Price card: {CARD_PATH.relative_to(ROOT)}")
    print(f"  source:   {card.get('source_url')}")
    print(f"  fetched:  {card.get('fetched_at')}")
    print(f"  API/mode: {card.get('api')} / {mode_default} (code default)")
    print(f"  rate:     ${per_1000:g} / 1,000 requests  (parsed: {parse_hit!r})")
    print()
    print("COMPOUND COST ARMS (compound-mini claim counts + measured shipping calls)")
    print(f"  claims A={claims_a}  claims B={claims_b}")
    print(
        f"  {'arm':<16} {'parallel_calls':>14} {'USD':>10}  note"
    )
    rows_cost = [
        ("ALWAYS_SILENT", silent_calls, "skip all search — exhibit FAIL"),
        ("NAIVE_NO_REUSE", naive_calls, "1 Search per claim, A+B, no registry"),
        (
            "SHIPPING",
            ship_total,
            f"measured offline compound A={ship_a}→B={ship_b}",
        ),
    ]
    costs = {}
    for name, calls, note in rows_cost:
        usd = _usd(calls, per_1000)
        costs[name] = (calls, usd)
        print(f"  {name:<16} {calls:>14} {usd:>10.4f}  {note}")

    silent_usd = costs["ALWAYS_SILENT"][1]
    naive_usd = costs["NAIVE_NO_REUSE"][1]
    ship_usd = costs["SHIPPING"][1]
    save_vs_naive = naive_usd - ship_usd
    vs_silent = ship_usd - silent_usd

    print()
    print(
        f"Delta SHIPPING vs NAIVE_NO_REUSE:  "
        f"{costs['SHIPPING'][0] - costs['NAIVE_NO_REUSE'][0]:+d} calls · "
        f"${save_vs_naive:+.4f} saved (positive = shipping cheaper)"
    )
    print(
        f"Delta SHIPPING vs ALWAYS_SILENT:   "
        f"{costs['SHIPPING'][0] - costs['ALWAYS_SILENT'][0]:+d} calls · "
        f"${vs_silent:+.4f} extra (positive = shipping costs more)"
    )
    print()
    print("CORRECTNESS on refusal-correctness holdout (n=6) — silent vs shipping")
    print(f"  {'id':<6} {'gold':<14} {'silent':<10} {'shipping':<10} s_ok  h_ok")
    for sr, hr in zip(silent["rows"], shipping["rows"]):
        print(
            f"  {sr[0]:<6} {sr[1]:<14} {sr[2]:<10} {hr[2]:<10} "
            f"{str(sr[3]):<5} {str(hr[3])}"
        )
    print(
        f"ALWAYS_SILENT: {format_ci(silent['correct'], silent['n'])}"
    )
    print(
        f"SHIPPING:      {format_ci(shipping['correct'], shipping['n'])}"
    )
    print(
        f"Delta (shipping - silent): {shipping['correct'] - silent['correct']:+d}"
    )
    print(f"McNemar: p={p_mc[0]:.4f} ({p_mc[1]})")
    print()

    # Honest findings — including the ones that make us look worse.
    findings = []
    if silent_usd < ship_usd:
        findings.append(
            f"ALWAYS_SILENT wins on cost (${silent_usd:.4f} vs ${ship_usd:.4f}) — "
            f"expected; it also refuses every supported claim "
            f"({silent['correct']}/{silent['n']} vs {shipping['correct']}/{shipping['n']})."
        )
    if ship_usd < naive_usd:
        findings.append(
            f"SHIPPING beats NAIVE_NO_REUSE on cost by ${save_vs_naive:.4f} "
            f"({costs['NAIVE_NO_REUSE'][0]}→{costs['SHIPPING'][0]} Parallel calls) "
            f"on compound-mini — the compound claim is real at this object."
        )
    else:
        findings.append(
            "SHIPPING does NOT beat NAIVE_NO_REUSE on cost at this object — "
            "compound economics fail the cost gate."
        )
    if shipping["correct"] <= silent["correct"]:
        findings.append(
            "EMBARRASSMENT: ALWAYS_SILENT matches or beats SHIPPING on holdout "
            "correctness — verifier earns nothing at n=6 under this scorer."
        )
    else:
        findings.append(
            f"Shipping gains {shipping['correct'] - silent['correct']} correct "
            f"label(s) over silent at n=6; McNemar p={p_mc[0]:.4f} "
            f"(not a billing proof — price card estimate only)."
        )
    findings.append(
        "LIMIT: no Parallel console invoice on this VM (no API key). "
        "Dollars are price-card × measured call counts, not billed receipts."
    )
    # Dollar amounts on compound-mini are tiny — say so rather than inflate.
    findings.append(
        f"SCALE: shipping USD on this fixture is ${ship_usd:.4f}. "
        "A stranger reading only the dollar line will underweight the call-count "
        "delta (−2 vs naive). Report both."
    )

    print("FINDING:")
    for f in findings:
        print(f"  - {f}")

    # Gate passes if we produced dated card + three arms + correctness table.
    # It does NOT require shipping to win — losing is a valid measured result.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
