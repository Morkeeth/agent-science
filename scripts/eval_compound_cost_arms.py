#!/usr/bin/env python3
"""Qwen gate — compound economics with baseline arm + cost from price card.

Three arms on the same offline compound-mini A script, shared corpus DB per arm:

  NAIVE       always re-search (corpus recall patched off) — competent two-hour baseline
  PARAPHRASE  B rewrites overlapping facts in new words — what the old exhibit shipped
  EXACT       B keeps exact A wording + one new claim — sealed-prediction shape

Cost is computed from Parallel Search API *price card* (dated), not an invoice.
Billing console is Oscar-only; this gate states the card date and refuses to pretend
the figure is an invoice line.

Run: python3 scripts/eval_compound_cost_arms.py
"""
from __future__ import annotations

import json
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from clearance import instruments, search as _search  # noqa: E402
from clearance.locate import DEFAULT  # noqa: E402
import agent_science  # noqa: E402

PRICE_CARD = ROOT / "fixtures/price-cards/parallel-search-2026-09-12.json"
OFFLINE_A = ROOT / "fixtures/scripts/compound-mini-A.txt"
OFFLINE_B_EXACT = ROOT / "fixtures/scripts/compound-mini-B.txt"
OFFLINE_B_PARA = ROOT / "fixtures/scripts/compound-mini-B-paraphrase.txt"
SUBJECT = "orphan-works-eval"

_URL_DIRECTIVE = "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32012L0028"
_URL_FORTY = "https://www.bl.uk/help/copyright-and-permissions"
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


@dataclass
class _Raw:
    text: str
    source_url: str | None
    must_contain: str


# Fixed extractor lists mirror the script files — extraction is not live.
_CLAIMS = {
    "A": [
        _Raw("In 2012 the European Union passed Directive 2012/28/EU, the Orphan Works Directive.",
             None, "Directive 2012/28/EU"),
        _Raw("Member states had until 29 October 2014 to bring it into national law.",
             None, "29 October 2014"),
    ],
    "B_EXACT": [
        _Raw("In 2012 the European Union passed Directive 2012/28/EU, the Orphan Works Directive.",
             None, "Directive 2012/28/EU"),
        _Raw("Member states had until 29 October 2014 to bring it into national law.",
             None, "29 October 2014"),
        _Raw("The British Library has estimated that forty percent of its copyrighted collection is orphaned.",
             None, "forty percent"),
    ],
    "B_PARA": [
        _Raw("Europe's answer was Directive 2012/28/EU — known as the Orphan Works Directive —",
             None, "Directive 2012/28/EU"),
        _Raw("and the deadline for national transposition was 29 October 2014.",
             None, "29 October 2014"),
        _Raw("The British Library has estimated that forty percent of its copyrighted collection is orphaned.",
             None, "forty percent"),
    ],
}


class _FakeExtractor:
    name = "offline-fixed-claims"

    def __init__(self, model="x", *, script_key: str):
        self.model = model
        self.script_key = script_key

    def extract(self, script):
        return list(_CLAIMS[self.script_key])


class _Net:
    def __init__(self):
        self.find_calls = 0

    def find_sources(self, objective, queries, *, live=False, max_results=5, **kw):
        self.find_calls += 1
        blob = objective + " " + " ".join(str(q) for q in queries)
        if "Directive 2012/28/EU" in blob or "2012/28/EU" in blob:
            return [_cand(_URL_DIRECTIVE)]
        if "29 October 2014" in blob:
            return [_cand(_URL_DIRECTIVE)]
        if "forty percent" in blob:
            return [_cand(_URL_FORTY)]
        return []


def _cand(url):
    return _search.Candidate(url=url, title="t", excerpt="e")


def _fake_document(url, fetch=False, **kw):
    return {_URL_DIRECTIVE: _DOC_DIRECTIVE, _URL_FORTY: _DOC_FORTY}.get(url)


def _load_price_card() -> dict:
    return json.loads(PRICE_CARD.read_text())


def _usd(calls: int, card: dict, mode: str = "turbo_or_fast") -> float:
    return calls * float(card["modes"][mode])


def _run_pair(*, b_key: str, b_path: Path, naive: bool) -> dict:
    """Run A then B on one temp corpus.

    naive=True disables *all* reuse (corpus recall + refusal_log lookup/search)
    — the two-hour baseline that re-searches every claim every time.
    """
    from clearance import corpus as corpus_mod, refusal_log as log_mod

    net = _Net()
    saved = (
        _search.find_sources,
        instruments.document,
        agent_science.GeminiExtractor,
        agent_science.GeminiLocator,
        corpus_mod.recall,
        log_mod.lookup,
        log_mod.search_registry,
    )
    _search.find_sources = net.find_sources
    instruments.document = _fake_document
    agent_science.GeminiLocator = lambda model="x": DEFAULT
    if naive:
        corpus_mod.recall = lambda *a, **k: None  # type: ignore[assignment]
        log_mod.lookup = lambda *a, **k: None  # type: ignore[assignment]
        # search_registry still runs for analytics shape, but never "established"
        def _no_establish(con, query, *, limit=5, log=True, reuse=True):
            return {"established": None, "matches": [], "unsettled": True}
        log_mod.search_registry = _no_establish  # type: ignore[assignment]

    try:
        with tempfile.TemporaryDirectory() as d:
            db = Path(d) / "corpus.db"
            log_db = Path(d) / "refusal_log.db"
            agent_science.GeminiExtractor = (
                lambda model="x": _FakeExtractor(model, script_key="A"))
            a = agent_science.clear_script(
                OFFLINE_A.read_text(), subject=SUBJECT, corpus_db=db, log_db=log_db)
            agent_science.GeminiExtractor = (
                lambda model="x", k=b_key: _FakeExtractor(model, script_key=k))
            b = agent_science.clear_script(
                b_path.read_text(), subject=SUBJECT, corpus_db=db, log_db=log_db)
    finally:
        (_search.find_sources, instruments.document,
         agent_science.GeminiExtractor, agent_science.GeminiLocator,
         corpus_mod.recall, log_mod.lookup, log_mod.search_registry) = saved

    return {
        "a": a,
        "b": b,
        "net_find_calls": net.find_calls,
        "fixtures": (OFFLINE_A.name, b_path.name),
    }


def _arm_row(name: str, run: dict, card: dict) -> dict:
    a, b = run["a"], run["b"]
    # Metered search boundary for this offline fake is net.find_calls across A+B.
    # Also report claims-searched (parallel_calls) — the exhibit's historical metric.
    api_ab = int(run["net_find_calls"])
    # Split is not separately metered; cost the A+B total and the B-only claims-searched.
    cost_ab_fast = _usd(api_ab, card, "turbo_or_fast")
    cost_ab_adv = _usd(api_ab, card, "basic_or_advanced")
    compound_ok = (
        a["parallel_calls"] > 0
        and b["parallel_calls"] < a["parallel_calls"]
        and b["corpus_hits"] >= 1
    )
    return {
        "arm": name,
        "A_parallel_calls": a["parallel_calls"],
        "B_parallel_calls": b["parallel_calls"],
        "B_corpus_hits": b["corpus_hits"],
        "A_sourced": a["sourced"],
        "B_sourced": b["sourced"],
        "net_find_calls_AB": api_ab,
        "cost_AB_turbo_usd": round(cost_ab_fast, 6),
        "cost_AB_advanced_usd": round(cost_ab_adv, 6),
        "compound_pass": compound_ok,
        "fixtures": run["fixtures"],
    }


def main() -> int:
    if not PRICE_CARD.exists():
        print(f"MISSING price card {PRICE_CARD}")
        return 2
    if not OFFLINE_B_PARA.exists():
        print(f"MISSING paraphrase fixture {OFFLINE_B_PARA}")
        return 2

    card = _load_price_card()
    print("COMPOUND COST ARMS — offline · price card (not invoice)")
    print(f"Price card: {card['source_url']}")
    print(f"Fetched at: {card['fetched_at']}")
    print(f"Search turbo/fast: ${card['modes']['turbo_or_fast']}/req · "
          f"basic/advanced: ${card['modes']['basic_or_advanced']}/req")
    print(f"NOTE: {card['billing_note']}")
    print()

    arms = [
        ("NAIVE", "B_EXACT", OFFLINE_B_EXACT, True),
        ("PARAPHRASE", "B_PARA", OFFLINE_B_PARA, False),
        ("EXACT", "B_EXACT", OFFLINE_B_EXACT, False),
    ]
    rows = []
    for name, b_key, b_path, naive in arms:
        run = _run_pair(b_key=b_key, b_path=b_path, naive=naive)
        row = _arm_row(name, run, card)
        rows.append(row)

    hdr = (f"{'arm':<12} {'A_pc':>4} {'B_pc':>4} {'B_hits':>6} "
           f"{'finds':>5} {'$turbo':>8} {'$adv':>8} pass")
    print(hdr)
    print("-" * len(hdr))
    for r in rows:
        print(
            f"{r['arm']:<12} {r['A_parallel_calls']:>4} {r['B_parallel_calls']:>4} "
            f"{r['B_corpus_hits']:>6} {r['net_find_calls_AB']:>5} "
            f"{r['cost_AB_turbo_usd']:>8.4f} {r['cost_AB_advanced_usd']:>8.4f} "
            f"{'YES' if r['compound_pass'] else 'NO'}"
        )

    by = {r["arm"]: r for r in rows}
    naive, para, exact = by["NAIVE"], by["PARAPHRASE"], by["EXACT"]

    print()
    print("FINDINGS (re-derived this run — do not carry forward):")
    print(
        f"- NAIVE baseline never compounds: B_pc={naive['B_parallel_calls']} "
        f"hits={naive['B_corpus_hits']} pass={naive['compound_pass']}"
    )
    print(
        f"- PARAPHRASE (old exhibit B wording) under exact-assertion binding: "
        f"B_pc={para['B_parallel_calls']} hits={para['B_corpus_hits']} "
        f"pass={para['compound_pass']} — "
        + ("embarrassing: demo shape broken by paraphrase" if not para["compound_pass"]
           else "unexpected PASS")
    )
    print(
        f"- EXACT overlapping claims restore sealed shape: "
        f"A={exact['A_parallel_calls']}→B={exact['B_parallel_calls']} "
        f"hits={exact['B_corpus_hits']} pass={exact['compound_pass']}"
    )
    delta_hits = exact["B_corpus_hits"] - para["B_corpus_hits"]
    delta_pc = para["B_parallel_calls"] - exact["B_parallel_calls"]
    print(
        f"- EXACT vs PARAPHRASE: corpus_hits delta={delta_hits:+d}, "
        f"B parallel_calls saved={delta_pc:+d}"
    )
    print(
        f"- Cost (price card {card['fetched_at'][:10]}, turbo): "
        f"NAIVE ${naive['cost_AB_turbo_usd']:.4f} · "
        f"PARAPHRASE ${para['cost_AB_turbo_usd']:.4f} · "
        f"EXACT ${exact['cost_AB_turbo_usd']:.4f} "
        f"(NOT invoice — {card['billing_note'][:48]}…)"
    )

    # Gate: exact must pass; paraphrase must fail; naive must fail.
    # This is the falsifiable checklist item — a green that cannot go red is not a control.
    if exact["compound_pass"] and (not para["compound_pass"]) and (not naive["compound_pass"]):
        print()
        print("GATE OK — EXACT compounds; PARAPHRASE and NAIVE do not.")
        return 0

    print()
    print("GATE FAIL — arm outcomes did not match expected pattern "
          "(EXACT pass, PARAPHRASE fail, NAIVE fail).")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
