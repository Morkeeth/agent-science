#!/usr/bin/env python3
"""Qwen PRIOR LOSS gate — Cost from billing, with the price card's date stated.

Arms (identical compound-mini scripts, offline Parallel boundary):
  Baseline  — competent two-hour team: clear A then B with *separate* corpus DBs
              (no shared shelf). Every claim re-searches.
  Shipping  — shared corpus DB on one subject (our compound path).

USD comes from Parallel *public price card* × metered find_sources calls.
Invoice/billing API is attempted when PARALLEL_API_KEY is present; otherwise
BILLING_INVOICE=BLOCKED — we never invent an invoice total.

Gemini extract cost is NOT priced here (no dated Gemini price card fetched).
Only Parallel Search is on the card.

Run:
  python3 scripts/eval_cost_from_billing.py
  python3 scripts/eval_cost_from_billing.py --fetch-card   # refresh snapshot (needs network)
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

PRICE_URL = "https://docs.parallel.ai/getting-started/pricing.md"
CARD_DIR = ROOT / "fixtures/price-cards"
CARD_SNAP = CARD_DIR / "parallel-search-2026-09-18.md"
RECEIPT = ROOT / "docs/COST-FROM-BILLING-2026-09-18.md"
OFFLINE_A = ROOT / "fixtures/scripts/compound-mini-A.txt"
OFFLINE_B = ROOT / "fixtures/scripts/compound-mini-B.txt"
SUBJECT = "orphan-works-cost-gate"
SHIPPING_MODE = "advanced"  # clearance/search.py find_sources default


@dataclass
class PriceCard:
    source: str
    fetched_at_utc: str
    rate_advanced: float
    rate_turbo_fast: float
    shipping_mode: str
    rate_used: float
    body: str


def _parse_card(text: str, *, source: str, fetched_at: str | None = None) -> PriceCard:
    """Derive rates from card body — refuse hardcoded fallbacks without the object."""
    m = re.search(
        r"Per 1,000 `turbo` or `fast` requests[^|]*\|\s*(\d+)\s*\|",
        text,
    )
    if not m:
        # markdown table variant without backticks nesting
        m = re.search(
            r"`turbo` or `fast` requests[^\n]*?\|\s*(\d+)\s*\|",
            text,
        )
    if not m:
        raise SystemExit("PRICE CARD PARSE FAIL — turbo/fast rate row not found in card body")
    turbo = float(m.group(1)) / 1000.0

    m2 = re.search(
        r"Per 1,000 `basic` or `advanced` requests[^|]*\|\s*(\d+)\s*\|",
        text,
    )
    if not m2:
        m2 = re.search(
            r"`basic` or `advanced` requests[^\n]*?\|\s*(\d+)\s*\|",
            text,
        )
    if not m2:
        raise SystemExit("PRICE CARD PARSE FAIL — basic/advanced rate row not found in card body")
    advanced = float(m2.group(1)) / 1000.0

    fetched = fetched_at
    hm = re.search(r"fetched_at_utc:\s*(\S+)", text)
    if hm:
        fetched = hm.group(1)
    if not fetched:
        raise SystemExit("PRICE CARD DATE MISSING — refuse to mint USD without fetched_at_utc")

    if SHIPPING_MODE not in ("advanced", "basic"):
        raise SystemExit(f"unexpected shipping mode {SHIPPING_MODE!r}")
    rate_used = advanced
    return PriceCard(
        source=source,
        fetched_at_utc=fetched,
        rate_advanced=advanced,
        rate_turbo_fast=turbo,
        shipping_mode=SHIPPING_MODE,
        rate_used=rate_used,
        body=text,
    )


def fetch_card(*, write_snapshot: bool) -> PriceCard:
    req = urllib.request.Request(
        PRICE_URL,
        headers={"Accept": "text/markdown", "User-Agent": "agent-science-cost-gate/1"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        body = resp.read().decode("utf-8", errors="replace")
    fetched = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    header = (
        "<!-- PRICE CARD SNAPSHOT\n"
        f"source: {PRICE_URL}\n"
        f"fetched_at_utc: {fetched}\n"
        "api: Search\n"
        f"shipping_mode: {SHIPPING_MODE}\n"
        "NOTE: public price card, NOT a Parallel invoice.\n"
        "-->\n\n"
    )
    if write_snapshot:
        CARD_DIR.mkdir(parents=True, exist_ok=True)
        CARD_SNAP.write_text(header + body, encoding="utf-8")
    return _parse_card(header + body, source=PRICE_URL, fetched_at=fetched)


def load_card(*, fetch: bool) -> PriceCard:
    if fetch:
        try:
            return fetch_card(write_snapshot=True)
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            print(f"WARN  live price card fetch failed: {type(e).__name__}: {e}", file=sys.stderr)
            print("WARN  falling back to fixture snapshot", file=sys.stderr)
    if not CARD_SNAP.exists():
        raise SystemExit(f"MISSING price card snapshot: {CARD_SNAP}")
    text = CARD_SNAP.read_text(encoding="utf-8")
    return _parse_card(text, source=str(CARD_SNAP.relative_to(ROOT)))


def _attempt_invoice() -> dict:
    """Try Parallel usage/billing surfaces. Never invent totals."""
    key = os.environ.get("PARALLEL_API_KEY", "").strip()
    key_file = Path.home() / ".config/keys/parallel.key"
    if not key and key_file.exists():
        key = key_file.read_text().strip()
    if not key:
        return {
            "status": "BLOCKED",
            "reason": "PARALLEL_API_KEY absent (env + ~/.config/keys/parallel.key)",
            "invoice_usd": None,
        }
    # Parallel has no stable public "invoice total" endpoint documented for agents.
    # Probe common usage paths; any 2xx with parseable spend wins; else BLOCKED.
    probes = [
        "https://api.parallel.ai/v1/usage",
        "https://api.parallel.ai/v1beta/usage",
        "https://api.parallel.ai/v1/billing",
    ]
    errors = []
    for url in probes:
        req = urllib.request.Request(
            url,
            headers={
                "Authorization": f"Bearer {key}",
                "x-api-key": key,
                "User-Agent": "agent-science-cost-gate/1",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                raw = resp.read().decode("utf-8", errors="replace")
                return {
                    "status": "PROBED",
                    "url": url,
                    "http": resp.status,
                    "body_head": raw[:500],
                    "invoice_usd": None,
                    "note": "usage endpoint responded; dollar total not auto-parsed — inspect body",
                }
        except urllib.error.HTTPError as e:
            errors.append(f"{url} → HTTP {e.code}")
        except Exception as e:  # noqa: BLE001 — probe surface; all failures → BLOCKED
            errors.append(f"{url} → {type(e).__name__}: {e}")
    return {
        "status": "BLOCKED",
        "reason": "no usable Parallel usage/billing endpoint",
        "probes": errors,
        "invoice_usd": None,
    }


# --- offline compound meters (reuse compound-mini claim lists) -----------------

@dataclass
class _Raw:
    text: str
    source_url: str | None
    must_contain: str


_OFFLINE_CLAIMS = {
    "A": [
        _Raw(
            "In 2012 the European Union passed Directive 2012/28/EU, the Orphan Works Directive.",
            None,
            "Directive 2012/28/EU",
        ),
        _Raw(
            "Member states had until 29 October 2014 to bring it into national law.",
            None,
            "29 October 2014",
        ),
    ],
    "B": [
        _Raw(
            "In 2012 the European Union passed Directive 2012/28/EU, the Orphan Works Directive.",
            None,
            "Directive 2012/28/EU",
        ),
        _Raw(
            "Member states had until 29 October 2014 to bring it into national law.",
            None,
            "29 October 2014",
        ),
        _Raw(
            "The British Library has estimated that forty percent of its copyrighted collection is orphaned.",
            None,
            "forty percent",
        ),
    ],
}

# Synthetic powered set — more overlapping exact assertions so absolute USD is not toy-scale.
# NOT the live powered-A/B script extract (those need Gemini keys). Same verifier path.
_POWERED_CLAIMS = {
    "A": [
        _Raw("In 2012 the European Union passed Directive 2012/28/EU, the Orphan Works Directive.", None, "Directive 2012/28/EU"),
        _Raw("Member states had until 29 October 2014 to bring it into national law.", None, "29 October 2014"),
        _Raw("The British Library has estimated that forty percent of its copyrighted collection is orphaned.", None, "forty percent"),
        _Raw("Canada Section 77 lets the Copyright Board issue a licence when the owner cannot be located.", None, "Section 77"),
        _Raw("The UK Intellectual Property Office opened an orphan works licensing scheme in October 2014.", None, "October 2014"),
        _Raw("EUIPO in Alicante maintains the single EU orphan works register.", None, "Alicante"),
        _Raw("The Shawn Bentley Orphan Works Act passed the Senate in 2008 and died in the House.", None, "Shawn Bentley"),
        _Raw("Judge Denny Chin rejected the Google Books settlement in March 2011.", None, "March 2011"),
    ],
    "B": [
        # Exact overlaps with A (compound shelf) + two new spends
        _Raw("In 2012 the European Union passed Directive 2012/28/EU, the Orphan Works Directive.", None, "Directive 2012/28/EU"),
        _Raw("Member states had until 29 October 2014 to bring it into national law.", None, "29 October 2014"),
        _Raw("The British Library has estimated that forty percent of its copyrighted collection is orphaned.", None, "forty percent"),
        _Raw("Canada Section 77 lets the Copyright Board issue a licence when the owner cannot be located.", None, "Section 77"),
        _Raw("The UK Intellectual Property Office opened an orphan works licensing scheme in October 2014.", None, "October 2014"),
        _Raw("EUIPO in Alicante maintains the single EU orphan works register.", None, "Alicante"),
        _Raw("The Shawn Bentley Orphan Works Act passed the Senate in 2008 and died in the House.", None, "Shawn Bentley"),
        _Raw("Judge Denny Chin rejected the Google Books settlement in March 2011.", None, "March 2011"),
        _Raw("By June 2023 the Copyright Board of Canada had issued 321 licences and denied 36 applications.", None, "321"),
        _Raw("Section 108 of the US Copyright Act still governs library and archive reproduction.", None, "Section 108"),
    ],
}

_URL_DIRECTIVE = "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32012L0028"
_URL_FORTY = "https://www.bl.uk/help/copyright-and-permissions"
_URL_CA = "https://laws-lois.justice.gc.ca/eng/acts/C-42/page-1.html"
_URL_UK = "https://www.gov.uk/guidance/copyright-orphan-works"
_URL_EUIPO = "https://euipo.europa.eu/ohimportal/en/web/observatory/orphan-works-database"
_URL_BENTLEY = "https://www.copyright.gov/orphan/"
_URL_CHIN = "https://www.nysd.uscourts.gov/"
_URL_108 = "https://www.copyright.gov/title17/92chap1.html"
_DOC_DIRECTIVE = (
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
_DOC_CA = (
    "Copyright Act (Canada).\n"
    "Canada Section 77 lets the Copyright Board issue a licence when the owner cannot be located.\n"
    "By June 2023 the Copyright Board of Canada had issued 321 licences and denied 36 applications.\n"
)
_DOC_UK = (
    "UK IPO guidance.\n"
    "The UK Intellectual Property Office opened an orphan works licensing scheme in October 2014.\n"
)
_DOC_EUIPO = (
    "EUIPO Observatory.\n"
    "EUIPO in Alicante maintains the single EU orphan works register.\n"
)
_DOC_BENTLEY = (
    "US Copyright Office orphan works.\n"
    "The Shawn Bentley Orphan Works Act passed the Senate in 2008 and died in the House.\n"
)
_DOC_CHIN = (
    "Court record.\n"
    "Judge Denny Chin rejected the Google Books settlement in March 2011.\n"
)
_DOC_108 = (
    "US Copyright Act.\n"
    "Section 108 of the US Copyright Act still governs library and archive reproduction.\n"
)

_CLAIM_BANK: dict[str, dict[str, list[_Raw]]] = {
    "mini": _OFFLINE_CLAIMS,
    "powered-synthetic": _POWERED_CLAIMS,
}


class _FakeExtractor:
    name = "offline-fixed-claims"

    def __init__(self, model="x", *, script_key: str, bank: str = "mini"):
        self.model = model
        self.script_key = script_key
        self.bank = bank

    def extract(self, script):
        return list(_CLAIM_BANK[self.bank][self.script_key])


class _Net:
    def __init__(self):
        self.find_calls = 0

    def find_sources(self, objective, queries, *, live=False, max_results=5, **kw):
        self.find_calls += 1
        blob = objective + " " + " ".join(str(q) for q in queries)
        rules = [
            (("Directive 2012/28/EU", "2012/28/EU"), _URL_DIRECTIVE),
            (("29 October 2014",), _URL_DIRECTIVE),
            (("forty percent",), _URL_FORTY),
            (("Section 77", "321"), _URL_CA),
            (("October 2014",), _URL_UK),
            (("Alicante",), _URL_EUIPO),
            (("Shawn Bentley",), _URL_BENTLEY),
            (("March 2011",), _URL_CHIN),
            (("Section 108",), _URL_108),
        ]
        for keys, url in rules:
            if any(k in blob for k in keys):
                return [_cand(url)]
        return []


def _cand(url):
    from clearance import search as _search

    return _search.Candidate(url=url, title="t", excerpt="e")


def _fake_document(url, fetch=False, **kw):
    return {
        _URL_DIRECTIVE: _DOC_DIRECTIVE,
        _URL_FORTY: _DOC_FORTY,
        _URL_CA: _DOC_CA,
        _URL_UK: _DOC_UK,
        _URL_EUIPO: _DOC_EUIPO,
        _URL_BENTLEY: _DOC_BENTLEY,
        _URL_CHIN: _DOC_CHIN,
        _URL_108: _DOC_108,
    }.get(url)


def _run_pair(*, shared_corpus: bool, bank: str = "mini") -> dict:
    """Run A then B. shared_corpus=True is shipping; False is naive baseline."""
    import agent_science
    from clearance import instruments, search as _search
    from clearance.locate import DEFAULT

    net = _Net()
    saved = (
        _search.find_sources,
        instruments.document,
        agent_science.GeminiExtractor,
        agent_science.GeminiLocator,
    )
    _search.find_sources = net.find_sources
    instruments.document = _fake_document
    agent_science.GeminiLocator = lambda model="x": DEFAULT

    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        results = {}
        shared_db = root / "corpus.db"
        shared_log = root / "refusal_log.db"
        for key, path in (("A", OFFLINE_A), ("B", OFFLINE_B)):
            if shared_corpus:
                db, log_db = shared_db, shared_log
            else:
                db = root / f"corpus-{key}.db"
                log_db = root / f"refusal-{key}.db"
            agent_science.GeminiExtractor = (
                lambda model="x", k=key, b=bank: _FakeExtractor(
                    model, script_key=k, bank=b
                )
            )
            results[key] = agent_science.clear_script(
                path.read_text(), subject=SUBJECT, corpus_db=db, log_db=log_db
            )

    (
        _search.find_sources,
        instruments.document,
        agent_science.GeminiExtractor,
        agent_science.GeminiLocator,
    ) = saved

    pa = results["A"]["parallel_calls"]
    pb = results["B"]["parallel_calls"]
    return {
        "a_parallel": pa,
        "b_parallel": pb,
        "total_parallel": pa + pb,
        "a_corpus_hits": results["A"]["corpus_hits"],
        "b_corpus_hits": results["B"]["corpus_hits"],
        "net_find_calls": net.find_calls,
        "a_claims": len(results["A"]["rows"]),
        "b_claims": len(results["B"]["rows"]),
        "bank": bank,
    }


def _usd(calls: int, rate: float) -> float:
    return calls * rate


def write_receipt(
    *,
    card: PriceCard,
    baseline: dict,
    shipping: dict,
    invoice: dict,
    commit: str,
    powered_baseline: dict | None = None,
    powered_shipping: dict | None = None,
) -> None:
    b_usd = _usd(baseline["total_parallel"], card.rate_used)
    s_usd = _usd(shipping["total_parallel"], card.rate_used)
    delta_calls = baseline["total_parallel"] - shipping["total_parallel"]
    delta_usd = b_usd - s_usd
    saving = (delta_usd / b_usd) if b_usd else float("nan")
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    finding = (
        f"shipping cheaper by {delta_calls} Parallel call(s), "
        f"${delta_usd:.4f} on price card ({saving:.0%} of baseline)"
        if delta_usd > 0
        else (
            "TIED on Parallel USD — compound shelf adds no measured dollar save at this n"
            if delta_usd == 0
            else "EMBARRASSMENT — shipping costs MORE Parallel USD than naive baseline"
        )
    )

    lines = [
        "# COST FROM BILLING — Qwen PRIOR LOSS gate",
        "",
        f"**Date:** {now} · **Commit:** `{commit}`",
        f"**Fixtures:** `{OFFLINE_A.name}` → `{OFFLINE_B.name}` · subject `{SUBJECT}`",
        "",
        "## Price card (not an invoice)",
        "",
        f"| Field | Value |",
        f"|-------|-------|",
        f"| Source | `{card.source}` |",
        f"| Fetched at (UTC) | **{card.fetched_at_utc}** |",
        f"| Shipping search mode | `{card.shipping_mode}` (`find_sources` default) |",
        f"| Rate used | **${card.rate_used:.3f}** / request "
        f"(= ${card.rate_used * 1000:.0f} / 1,000 `advanced` requests) |",
        f"| Turbo/fast (not used) | ${card.rate_turbo_fast:.3f} / request |",
        "",
        "## Invoice / billing API",
        "",
        f"- **Status:** `{invoice['status']}`",
        f"- **invoice_usd:** `{invoice.get('invoice_usd')}`",
        f"- **Reason / detail:** {invoice.get('reason') or invoice.get('note') or invoice.get('probes')}",
        "",
        "This gate **does not** claim invoice truth without a Parallel billing response.",
        "USD below is **price-card × meter** only.",
        "",
        "## Arms · compound-mini (default cold-clone gate)",
        "",
        "| Arm | Corpus shelf | A Parallel | B Parallel | Total Parallel | USD (card) | B corpus_hits |",
        "|-----|--------------|----------:|----------:|---------------:|-----------:|--------------:|",
        f"| **Baseline** (naive always-search) | separate DBs | "
        f"{baseline['a_parallel']} | {baseline['b_parallel']} | "
        f"**{baseline['total_parallel']}** | **${b_usd:.4f}** | {baseline['b_corpus_hits']} |",
        f"| **Shipping** (shared subject shelf) | one DB | "
        f"{shipping['a_parallel']} | {shipping['b_parallel']} | "
        f"**{shipping['total_parallel']}** | **${s_usd:.4f}** | {shipping['b_corpus_hits']} |",
        "",
        f"**Delta (baseline − shipping):** {delta_calls:+d} calls · "
        f"${delta_usd:+.4f} · {finding}",
        "",
    ]

    if powered_baseline and powered_shipping:
        pb_usd = _usd(powered_baseline["total_parallel"], card.rate_used)
        ps_usd = _usd(powered_shipping["total_parallel"], card.rate_used)
        pd_calls = powered_baseline["total_parallel"] - powered_shipping["total_parallel"]
        pd_usd = pb_usd - ps_usd
        lines += [
            "## Arms · powered-synthetic (larger n, still offline)",
            "",
            "Fixed claim lists (~8 A / ~10 B exact-assertion overlaps). "
            "**Not** live `powered-A-law.txt` / `powered-B-archive.txt` Gemini extract "
            "(those need keys — BLOCKED on this VM).",
            "",
            "| Arm | A Parallel | B Parallel | Total | USD (card) | B corpus_hits |",
            "|-----|----------:|----------:|------:|-----------:|--------------:|",
            f"| Baseline | {powered_baseline['a_parallel']} | {powered_baseline['b_parallel']} | "
            f"**{powered_baseline['total_parallel']}** | **${pb_usd:.4f}** | "
            f"{powered_baseline['b_corpus_hits']} |",
            f"| Shipping | {powered_shipping['a_parallel']} | {powered_shipping['b_parallel']} | "
            f"**{powered_shipping['total_parallel']}** | **${ps_usd:.4f}** | "
            f"{powered_shipping['b_corpus_hits']} |",
            "",
            f"**Powered delta:** {pd_calls:+d} calls · ${pd_usd:+.4f}",
            "",
        ]

    lines += [
        "## Honesty",
        "",
        "- Gemini extract / locate USD: **not priced** (no dated Gemini price card fetched tonight).",
        "- Absolute dollars even on powered-synthetic remain cents — shape and ratio matter more "
        "than the dollar printout at this fixture size.",
        "- `measure_compounding.py` still hardcodes `PARALLEL_CALL = 0.005` without a fetch date — "
        "that file is **not** this gate; do not carry its number.",
        "",
        "## Re-run",
        "",
        "```bash",
        "python3 scripts/eval_cost_from_billing.py",
        "python3 scripts/eval_cost_from_billing.py --fetch-card   # refresh snapshot",
        "```",
        "",
    ]
    RECEIPT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--fetch-card",
        action="store_true",
        help="Refresh fixtures/price-cards snapshot from Parallel docs (needs network)",
    )
    ap.add_argument(
        "--skip-powered",
        action="store_true",
        help="Only run compound-mini arms (faster)",
    )
    args = ap.parse_args()

    card = load_card(fetch=args.fetch_card)
    baseline = _run_pair(shared_corpus=False, bank="mini")
    shipping = _run_pair(shared_corpus=True, bank="mini")
    powered_baseline = powered_shipping = None
    if not args.skip_powered:
        powered_baseline = _run_pair(shared_corpus=False, bank="powered-synthetic")
        powered_shipping = _run_pair(shared_corpus=True, bank="powered-synthetic")
    invoice = _attempt_invoice()

    import subprocess

    commit = (
        subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            cwd=str(ROOT),
        ).stdout.strip()
        or "unknown"
    )

    write_receipt(
        card=card,
        baseline=baseline,
        shipping=shipping,
        invoice=invoice,
        commit=commit,
        powered_baseline=powered_baseline,
        powered_shipping=powered_shipping,
    )

    b_usd = _usd(baseline["total_parallel"], card.rate_used)
    s_usd = _usd(shipping["total_parallel"], card.rate_used)

    print("COST-FROM-BILLING EVAL")
    print(f"  price card: {card.source}")
    print(f"  fetched_at_utc: {card.fetched_at_utc}")
    print(f"  mode={card.shipping_mode} rate=${card.rate_used:.3f}/req")
    print(f"  invoice: {invoice['status']}  invoice_usd={invoice.get('invoice_usd')}")
    print(
        f"  mini baseline:  Parallel {baseline['total_parallel']}  "
        f"(A={baseline['a_parallel']} B={baseline['b_parallel']})  ${b_usd:.4f}"
    )
    print(
        f"  mini shipping:  Parallel {shipping['total_parallel']}  "
        f"(A={shipping['a_parallel']} B={shipping['b_parallel']})  ${s_usd:.4f}"
    )
    print(
        f"  mini delta:     Parallel {baseline['total_parallel'] - shipping['total_parallel']:+d}  "
        f"${b_usd - s_usd:+.4f}"
    )
    if powered_baseline and powered_shipping:
        pb = _usd(powered_baseline["total_parallel"], card.rate_used)
        ps = _usd(powered_shipping["total_parallel"], card.rate_used)
        print(
            f"  powered baseline: Parallel {powered_baseline['total_parallel']}  ${pb:.4f}"
        )
        print(
            f"  powered shipping: Parallel {powered_shipping['total_parallel']}  ${ps:.4f}"
        )
        print(
            f"  powered delta:    Parallel "
            f"{powered_baseline['total_parallel'] - powered_shipping['total_parallel']:+d}  "
            f"${pb - ps:+.4f}"
        )
    print(f"  receipt:   {RECEIPT.relative_to(ROOT)}")

    # Gate: shipping must not cost more Parallel USD than naive baseline.
    if s_usd > b_usd:
        print("FAIL  shipping Parallel USD exceeds naive baseline — compound shelf lost")
        return 2
    if shipping["b_corpus_hits"] < 1:
        print("FAIL  shipping B corpus_hits < 1 — compound shelf did not fire")
        return 3
    if not card.fetched_at_utc:
        print("FAIL  price card missing date")
        return 4
    if powered_baseline and powered_shipping:
        pb = _usd(powered_baseline["total_parallel"], card.rate_used)
        ps = _usd(powered_shipping["total_parallel"], card.rate_used)
        if ps > pb:
            print("FAIL  powered-synthetic shipping exceeds baseline")
            return 5
        if powered_shipping["b_corpus_hits"] < 1:
            print("FAIL  powered-synthetic B corpus_hits < 1")
            return 6
    print("PASS  shipping ≤ baseline on Parallel price-card USD; card dated; invoice status named")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
