#!/usr/bin/env python3
"""Qwen eval gate — cost from published price card × measured Parallel calls.

Baseline arm (naive, ~2h team): clear every claim with a fresh search — no shared
corpus between Run A and Run B.

Shipping arm: one shared corpus DB — exact-assertion reuse (current engine).

Paraphrase counter-arm: B uses different wording for the same facts — must NOT
compound under exact-assertion binding (the regression that made the old exhibit
look green after Sep 4).

Always-silent arm: $0 Parallel; accuracy on the held-out refusal set only.

Price card: Parallel Search API docs, fetched 2026-09-10.
  https://docs.parallel.ai/getting-started/pricing
  mode advanced (shipping default in clearance/search.py) = $5 / 1,000 requests
  → $0.005 per successful search call.

NOT from the Parallel / GCP billing console — that requires Oscar credentials.
This gate is falsifiable offline: re-run and the USD figures move with call counts.

Run: python3 scripts/seed_document_cache.py && python3 scripts/eval_cost_baseline.py
"""
from __future__ import annotations

import html
import json
import re
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import agent_science
from clearance import instruments, search as _search
from clearance.facts import Claim, judge_claim
from clearance.locate import DEFAULT
from clearance.verdict import GREEN, UNKNOWN

sys.path.insert(0, str(ROOT / "scripts"))
from eval_stats import format_ci, mcnemar_exact  # noqa: E402

# --- Price card (re-fetched 2026-09-10 from docs.parallel.ai; do not invent) ---
PRICE_CARD = {
    "source": "https://docs.parallel.ai/getting-started/pricing",
    "fetched_utc_date": "2026-09-10",
    "api": "Search",
    "mode": "advanced",  # clearance.search.find_sources default
    "usd_per_1000": 5.0,
}
USD_PER_CALL = PRICE_CARD["usd_per_1000"] / 1000.0

SET = json.loads((ROOT / "fixtures/refusal-correctness/set.json").read_text())

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

A_CLAIMS = [
    ("In 2012 the European Union passed Directive 2012/28/EU, the Orphan Works Directive.",
     "Directive 2012/28/EU"),
    ("Member states had until 29 October 2014 to bring it into national law.",
     "29 October 2014"),
]
B_IDENTICAL = A_CLAIMS + [
    ("The British Library has estimated that forty percent of its copyrighted collection is orphaned.",
     "forty percent"),
]
# Old compound-mini-B shape — paraphrases of A. Must cost like a cold run on overlap.
B_PARAPHRASE = [
    ("Europe's answer was Directive 2012/28/EU — known as the Orphan Works Directive —",
     "Directive 2012/28/EU"),
    ("and the deadline for national transposition was 29 October 2014.",
     "29 October 2014"),
    ("The British Library has estimated that forty percent of its copyrighted collection is orphaned.",
     "forty percent"),
]


@dataclass
class _Raw:
    text: str
    source_url: str | None
    must_contain: str


class _FakeExtractor:
    name = "cost-eval-fixed"

    def __init__(self, model="x", *, claims):
        self.model = model
        self._claims = claims

    def extract(self, script):
        return [_Raw(t, None, m) for t, m in self._claims]


class _Net:
    def __init__(self):
        self.find_calls = 0

    def find_sources(self, objective, queries, *, live=False, max_results=5, **kw):
        self.find_calls += 1
        blob = objective + " " + " ".join(str(q) for q in queries)
        if "Directive 2012/28/EU" in blob or "2012/28/EU" in blob:
            return [_search.Candidate(url=_URL_DIRECTIVE, title="t", excerpt="e")]
        if "29 October 2014" in blob:
            return [_search.Candidate(url=_URL_DIRECTIVE, title="t", excerpt="e")]
        if "forty percent" in blob:
            return [_search.Candidate(url=_URL_FORTY, title="t", excerpt="e")]
        return []


def _fake_document(url, fetch=False, **kw):
    return {_URL_DIRECTIVE: _DOC_DIRECTIVE, _URL_FORTY: _DOC_FORTY}.get(url)


def _usd(calls: int) -> float:
    return round(calls * USD_PER_CALL, 6)


def _clear(claims, *, corpus_db: Path, log_db: Path, net: _Net) -> dict:
    agent_science.GeminiExtractor = (
        lambda model="x", c=claims: _FakeExtractor(model, claims=c)
    )
    return agent_science.clear_script(
        "\n".join(t for t, _ in claims),
        subject="orphan-works-cost-eval",
        corpus_db=corpus_db,
        log_db=log_db,
    )


def _run_pair(b_claims) -> dict:
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
    try:
        with tempfile.TemporaryDirectory() as d:
            db = Path(d) / "corpus.db"
            log_db = Path(d) / "refusal_log.db"
            a = _clear(A_CLAIMS, corpus_db=db, log_db=log_db, net=net)
            b = _clear(b_claims, corpus_db=db, log_db=log_db, net=net)
        return {
            "a_parallel": a["parallel_calls"],
            "b_parallel": b["parallel_calls"],
            "b_corpus_hits": b["corpus_hits"],
            "total_parallel": a["parallel_calls"] + b["parallel_calls"],
            "net_find_calls": net.find_calls,
        }
    finally:
        (
            _search.find_sources,
            instruments.document,
            agent_science.GeminiExtractor,
            agent_science.GeminiLocator,
        ) = saved


def _run_naive() -> dict:
    """No shared shelf — each production gets a fresh DB (competent 2h baseline)."""
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
    try:
        with tempfile.TemporaryDirectory() as d:
            a = _clear(
                A_CLAIMS,
                corpus_db=Path(d) / "a_corpus.db",
                log_db=Path(d) / "a_log.db",
                net=net,
            )
            b = _clear(
                B_IDENTICAL,
                corpus_db=Path(d) / "b_corpus.db",
                log_db=Path(d) / "b_log.db",
                net=net,
            )
        return {
            "a_parallel": a["parallel_calls"],
            "b_parallel": b["parallel_calls"],
            "b_corpus_hits": b["corpus_hits"],
            "total_parallel": a["parallel_calls"] + b["parallel_calls"],
            "net_find_calls": net.find_calls,
        }
    finally:
        (
            _search.find_sources,
            instruments.document,
            agent_science.GeminiExtractor,
            agent_science.GeminiLocator,
        ) = saved


def _visible(raw: str) -> str:
    raw = re.sub(r"<(script|style).*?</\1>", " ", raw, flags=re.S | re.I)
    txt = html.unescape(re.sub(r"<[^>]+>", " ", raw))
    return re.sub(r"\s+", " ", txt).strip()


def _silent_verdict(_body: str, _claim: str, _must: str) -> str:
    return "UNKNOWN"


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


def _refusal_silent_vs_shipping() -> dict:
    rows = []
    silent_ok = ship_ok = 0
    b = c = 0
    for item in SET["items"]:
        body = _visible((ROOT / item["document"]).read_text())
        url = f"file://{Path(item['document']).name}"
        gold = GREEN if item["expected"] == "SUPPORTED" else UNKNOWN
        s = _silent_verdict(body, item["claim"], item["must_contain"])
        sh = _shipping_verdict(url, body, item["claim"], item["must_contain"])
        s_correct = s == gold
        sh_correct = sh == gold
        silent_ok += int(s_correct)
        ship_ok += int(sh_correct)
        if s_correct and not sh_correct:
            b += 1
        if sh_correct and not s_correct:
            c += 1
        rows.append((item["id"], item["expected"], s, sh, s_correct, sh_correct))
    n = len(SET["items"])
    return {
        "n": n,
        "silent": silent_ok,
        "shipping": ship_ok,
        "rows": rows,
        "mcnemar": mcnemar_exact(b, c),
        "b": b,
        "c": c,
    }


def main() -> int:
    print("COST EVAL — price card × measured Parallel calls")
    print(f"Price card: {PRICE_CARD['source']}")
    print(f"Fetched:    {PRICE_CARD['fetched_utc_date']}")
    print(f"Mode:       Search/{PRICE_CARD['mode']} @ "
          f"${PRICE_CARD['usd_per_1000']:.0f}/1000 = ${USD_PER_CALL} per call")
    print("Billing console: NOT queried (Oscar-only) — this is card × counters.\n")

    naive = _run_naive()
    ship = _run_pair(B_IDENTICAL)
    para = _run_pair(B_PARAPHRASE)

    print("Arm                  A_par  B_par  B_hits  total  USD@advanced")
    for name, r in (
        ("naive (no shelf)", naive),
        ("shipping (exact)", ship),
        ("paraphrase B (counter)", para),
    ):
        print(
            f"{name:<24}{r['a_parallel']:>5}  {r['b_parallel']:>5}  "
            f"{r['b_corpus_hits']:>6}  {r['total_parallel']:>5}  ${_usd(r['total_parallel']):.4f}"
        )

    delta_calls = naive["total_parallel"] - ship["total_parallel"]
    print(f"\nDelta (naive − shipping) calls: {delta_calls:+d}  "
          f"USD: ${_usd(delta_calls):.4f}")
    if ship["b_corpus_hits"] < 1 or ship["b_parallel"] >= ship["a_parallel"]:
        print("FINDING: shipping failed to compound on identical overlap — RED.")
        compound_ok = False
    else:
        print("FINDING: shipping compounds on identical assertions; "
              f"saves {delta_calls} Parallel call(s) vs naive.")
        compound_ok = True

    if para["b_corpus_hits"] != 0:
        print("FINDING: paraphrase counter unexpectedly reused — integrity regression.")
        para_ok = False
    else:
        print("FINDING: paraphrase counter correctly spends like a cold run "
              f"(B_hits={para['b_corpus_hits']}, B_par={para['b_parallel']}).")
        para_ok = True

    print("\n--- Always-silent vs shipping on refusal holdout (accuracy, $0 Parallel) ---")
    acc = _refusal_silent_vs_shipping()
    n = acc["n"]
    print(f"id     gold           silent     shipping   s_ok   sh_ok")
    for rid, gold, s, sh, sok, shok in acc["rows"]:
        print(f"{rid:<6} {gold:<14} {s:<10} {sh:<10} {sok!s:<6} {shok!s}")
    print(f"Silent:    {format_ci(acc['silent'], n)}")
    print(f"Shipping:  {format_ci(acc['shipping'], n)}")
    p, detail = acc["mcnemar"]
    print(f"McNemar:   p={p:.4f} ({detail})")
    if acc["silent"] >= acc["shipping"]:
        print("FINDING: always-silent ties or beats shipping on accuracy — "
              "embarrassment; do not claim accuracy moat from this set alone.")
        silent_ok = False
    else:
        print("FINDING: shipping beats always-silent on holdout; silent stays $0.")
        silent_ok = True

    print("\n--- Gate ---")
    print(f"compound_ok={compound_ok} paraphrase_counter_ok={para_ok} "
          f"silent_does_not_win={silent_ok}")
    print("Billing console receipt: BLOCKED (no Parallel/GCP billing access on this VM).")

    if not (compound_ok and para_ok and silent_ok):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
