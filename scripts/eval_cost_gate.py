#!/usr/bin/env python3
"""Cost gate — price card dated + naive always-search baseline arm.

PRIOR LOSS checklist item: "Cost from billing, with the price card's date stated."

This gate:
  1. States the public Parallel price card URL + fetch date (re-derived at object).
  2. Measures shipping compound (exact-assertion offline A→B) Parallel call counts.
  3. Measures a naive always-search baseline (corpus/log recall forced miss).
  4. Multiplies calls × price-card unit costs → estimated USD range.
  5. Prints billing: UNKNOWN unless AGENT_SCIENCE_BILLING_INVOICE_USD is set.

It does NOT invent an invoice. A green "billing verified" line requires Oscar's
console export. Until then the checkbox in hack.md stays open and this script
says so explicitly.

Re-derive numbers every run — do not carry from docs.
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

PRICE_CARD_URL = "https://docs.parallel.ai/resources/pricing"
# Public card (fetched live below; these are fallbacks only if fetch fails):
# Search $1–$5 / 1,000 requests. We price the gate on Search only (our Parallel
# boundary is find_sources). Extract/Gemini omitted unless invoice says otherwise.
SEARCH_LOW_PER_1K = 1.0
SEARCH_HIGH_PER_1K = 5.0

SUBJECT = "orphan-works-cost-gate"
_URL = "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32012L0028"
_URL_FORTY = "https://www.bl.uk/help/copyright-and-permissions"
_DOC = (
    "Directive 2012/28/EU of the European Parliament and of the Council.\n"
    "Member States shall bring into force the laws necessary to comply with this "
    "Directive by 29 October 2014.\n"
    "Directive 2012/28/EU — the Orphan Works Directive — was adopted in 2012.\n"
)
_DOC_FORTY = (
    "British Library copyright guidance.\n"
    "The British Library has estimated that forty percent of its copyrighted collection "
    "is orphaned.\n"
)


@dataclass
class _Raw:
    text: str
    source_url: str | None
    must_contain: str


CLAIMS_A = [
    _Raw("In 2012 the European Union passed Directive 2012/28/EU, the Orphan Works Directive.",
         None, "Directive 2012/28/EU"),
    _Raw("Member states had until 29 October 2014 to bring it into national law.",
         None, "29 October 2014"),
]
CLAIMS_B = [
    _Raw("In 2012 the European Union passed Directive 2012/28/EU, the Orphan Works Directive.",
         None, "Directive 2012/28/EU"),
    _Raw("Member states had until 29 October 2014 to bring it into national law.",
         None, "29 October 2014"),
    _Raw("The British Library has estimated that forty percent of its copyrighted collection is orphaned.",
         None, "forty percent"),
]


class _FakeExtractor:
    name = "cost-gate-fixed"

    def __init__(self, model="x", *, claims):
        self.model = model
        self._claims = claims

    def extract(self, script):
        return list(self._claims)


class _Net:
    def __init__(self):
        self.find_calls = 0

    def find_sources(self, objective, queries, *, live=False, max_results=5, **kw):
        self.find_calls += 1
        blob = objective + " " + " ".join(str(q) for q in queries)
        from clearance import search as _search
        if "forty percent" in blob:
            return [_search.Candidate(url=_URL_FORTY, title="t", excerpt="e")]
        return [_search.Candidate(url=_URL, title="t", excerpt="e")]


def _fake_document(url, fetch=False, **kw):
    return {_URL: _DOC, _URL_FORTY: _DOC_FORTY}.get(url)


def fetch_price_card() -> dict:
    """Fetch the public price card; record date and the Search band we use."""
    fetched_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    body = ""
    status = None
    try:
        req = urllib.request.Request(
            PRICE_CARD_URL,
            headers={"Accept": "text/markdown", "User-Agent": "agent-science-cost-gate"},
        )
        with urllib.request.urlopen(req, timeout=20) as resp:
            status = getattr(resp, "status", None) or resp.getcode()
            body = resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        return {
            "ok": False,
            "url": PRICE_CARD_URL,
            "fetched_at": fetched_at,
            "error": f"{type(e).__name__}: {e}",
            "search_low_per_1k": SEARCH_LOW_PER_1K,
            "search_high_per_1k": SEARCH_HIGH_PER_1K,
            "band_source": "fallback constants (fetch failed)",
        }
    has_band = ("$1" in body or "\\$1" in body) and ("$5" in body or "\\$5" in body)
    return {
        "ok": True,
        "url": PRICE_CARD_URL,
        "fetched_at": fetched_at,
        "http_status": status,
        "bytes": len(body),
        "search_band_visible": has_band,
        "search_low_per_1k": SEARCH_LOW_PER_1K,
        "search_high_per_1k": SEARCH_HIGH_PER_1K,
        "band_source": "docs.parallel.ai Search $1–$5 / 1,000 requests (card text visible)"
                       if has_band else "fallback constants (band markers not found)",
    }


def _run_pair(*, disable_reuse: bool) -> dict:
    import agent_science
    from clearance import instruments, search as _search, corpus, refusal_log
    from clearance.locate import DEFAULT

    net = _Net()
    saved = (_search.find_sources, instruments.document,
             agent_science.GeminiExtractor, agent_science.GeminiLocator)
    recall_saved = corpus.recall
    lookup_saved = refusal_log.lookup
    _search.find_sources = net.find_sources
    instruments.document = _fake_document
    agent_science.GeminiLocator = lambda model="x": DEFAULT

    if disable_reuse:
        corpus.recall = lambda *a, **k: None
        refusal_log.lookup = lambda *a, **k: None

    try:
        with tempfile.TemporaryDirectory() as d:
            db = Path(d) / "corpus.db"
            log_db = Path(d) / "refusal_log.db"
            agent_science.GeminiExtractor = (
                lambda model="x": _FakeExtractor(model, claims=CLAIMS_A))
            a = agent_science.clear_script(
                "A", subject=SUBJECT, corpus_db=db, log_db=log_db)
            agent_science.GeminiExtractor = (
                lambda model="x": _FakeExtractor(model, claims=CLAIMS_B))
            b = agent_science.clear_script(
                "B", subject=SUBJECT, corpus_db=db, log_db=log_db)
    finally:
        (_search.find_sources, instruments.document,
         agent_science.GeminiExtractor, agent_science.GeminiLocator) = saved
        corpus.recall = recall_saved
        refusal_log.lookup = lookup_saved

    return {
        "a_parallel": a["parallel_calls"],
        "b_parallel": b["parallel_calls"],
        "b_corpus_hits": b["corpus_hits"],
        "total_parallel": a["parallel_calls"] + b["parallel_calls"],
        "net_find_calls": net.find_calls,
    }


def usd_range(calls: int, low_per_1k: float, high_per_1k: float) -> tuple[float, float]:
    return (calls * low_per_1k / 1000.0, calls * high_per_1k / 1000.0)


def main() -> int:
    card = fetch_price_card()
    shipping = _run_pair(disable_reuse=False)
    baseline = _run_pair(disable_reuse=True)

    lo, hi = card["search_low_per_1k"], card["search_high_per_1k"]
    s_lo, s_hi = usd_range(shipping["total_parallel"], lo, hi)
    b_lo, b_hi = usd_range(baseline["total_parallel"], lo, hi)

    invoice = os.environ.get("AGENT_SCIENCE_BILLING_INVOICE_USD")
    billing = {
        "status": "UNKNOWN",
        "reason": "no AGENT_SCIENCE_BILLING_INVOICE_USD in env — Oscar console export required",
    }
    if invoice is not None and invoice.strip() != "":
        try:
            billing = {
                "status": "PROVIDED",
                "invoice_usd": float(invoice),
                "note": "operator-supplied; not verified against Parallel dashboard in this gate",
            }
        except ValueError:
            billing = {"status": "INVALID", "raw": invoice}

    print("COST GATE — Parallel Search price card × measured calls")
    print(f"Price card: {card['url']}")
    print(f"Fetched at: {card['fetched_at']}  ok={card.get('ok')}  "
          f"band_source={card.get('band_source')}")
    print(f"Unit band: ${lo:.2f}–${hi:.2f} per 1,000 Search requests")
    print()
    print("ARM shipping (exact-assertion reuse ON)")
    print(f"  A_parallel={shipping['a_parallel']}  B_parallel={shipping['b_parallel']}  "
          f"B_corpus_hits={shipping['b_corpus_hits']}  total={shipping['total_parallel']}")
    print(f"  estimated USD: ${s_lo:.6f} – ${s_hi:.6f}")
    print("ARM baseline (always-search — recall/lookup forced miss)")
    print(f"  A_parallel={baseline['a_parallel']}  B_parallel={baseline['b_parallel']}  "
          f"B_corpus_hits={baseline['b_corpus_hits']}  total={baseline['total_parallel']}")
    print(f"  estimated USD: ${b_lo:.6f} – ${b_hi:.6f}")
    print()
    saved_calls = baseline["total_parallel"] - shipping["total_parallel"]
    print(f"Delta calls (baseline - shipping): {saved_calls:+d}")
    print(f"Delta estimated USD (low–high): "
          f"${(b_lo - s_lo):+.6f} – ${(b_hi - s_hi):+.6f}")
    print()
    print(f"Billing invoice: {billing['status']}"
          + (f" — {billing.get('reason') or billing.get('note') or ''}"))
    if billing["status"] != "PROVIDED":
        print("CHECKLIST: 'Cost from billing' remains OPEN — price-card estimate only.")
    else:
        print("CHECKLIST: invoice USD provided in env; still confirm against Parallel console.")

    # Persist a machine-readable receipt next to other eval outputs.
    out = ROOT / "docs/RECEIPT-cost-gate-2026-09-16.json"
    out.write_text(json.dumps({
        "price_card": card,
        "shipping": shipping,
        "baseline_always_search": baseline,
        "estimated_usd": {
            "shipping": {"low": s_lo, "high": s_hi},
            "baseline": {"low": b_lo, "high": b_hi},
            "delta_baseline_minus_shipping": {
                "low": b_lo - s_lo, "high": b_hi - s_hi,
            },
        },
        "billing": billing,
    }, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {out}")

    # Exit 0 if we measured both arms and price card fetch attempted.
    # Exit 3 if shipping does not beat baseline on call count (embarrassment).
    if shipping["total_parallel"] >= baseline["total_parallel"]:
        print("FINDING: shipping does not save Parallel calls vs always-search — exhibit failed.")
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
