#!/usr/bin/env python3
"""Compound paraphrase gate — alternative arm that can beat shipping.

Product rule (exact-assertion reuse after f61635e): a paraphrased claim is a
different assertion. Same-subject corpus hits require identical wording.

Arms (identical inputs, offline, no API keys):
  shipping  — agent_science.clear_script (exact-assertion corpus + log)
  naive     — term-keyed reuse (must_contain / retrieval anchor only); the
              two-hour baseline any competent team ships before assertion identity

Done when: both arms print raw rows + compound metrics; finding states which arm
wins the Parallel-drop / corpus_hits score on paraphrased B.

Re-derive every time — do not carry numbers from docs.
"""
from __future__ import annotations

import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

SUBJECT = "orphan-works-paraphrase-gate"
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


# A establishes two facts. B paraphrases both and adds one new claim.
CLAIMS_A = [
    _Raw("In 2012 the European Union passed Directive 2012/28/EU, the Orphan Works Directive.",
         None, "Directive 2012/28/EU"),
    _Raw("Member states had until 29 October 2014 to bring it into national law.",
         None, "29 October 2014"),
]
CLAIMS_B_PARAPHRASE = [
    _Raw("Europe's answer was Directive 2012/28/EU — known as the Orphan Works Directive —",
         None, "Directive 2012/28/EU"),
    _Raw("and the deadline for national transposition was 29 October 2014.",
         None, "29 October 2014"),
    _Raw("The British Library has estimated that forty percent of its copyrighted collection is orphaned.",
         None, "forty percent"),
]


class _FakeExtractor:
    name = "paraphrase-gate-fixed"

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
        if "forty percent" in blob:
            from clearance import search as _search
            return [_search.Candidate(url=_URL_FORTY, title="t", excerpt="e")]
        from clearance import search as _search
        return [_search.Candidate(url=_URL, title="t", excerpt="e")]


def _fake_document(url, fetch=False, **kw):
    return {_URL: _DOC, _URL_FORTY: _DOC_FORTY}.get(url)


def _run_shipping() -> dict:
    import agent_science
    from clearance import instruments, search as _search
    from clearance.locate import DEFAULT

    net = _Net()
    saved = (_search.find_sources, instruments.document,
             agent_science.GeminiExtractor, agent_science.GeminiLocator)
    _search.find_sources = net.find_sources
    instruments.document = _fake_document
    agent_science.GeminiLocator = lambda model="x": DEFAULT

    with tempfile.TemporaryDirectory() as d:
        db = Path(d) / "corpus.db"
        log_db = Path(d) / "refusal_log.db"
        agent_science.GeminiExtractor = (
            lambda model="x": _FakeExtractor(model, claims=CLAIMS_A))
        a = agent_science.clear_script(
            "A", subject=SUBJECT, corpus_db=db, log_db=log_db)
        agent_science.GeminiExtractor = (
            lambda model="x": _FakeExtractor(model, claims=CLAIMS_B_PARAPHRASE))
        b = agent_science.clear_script(
            "B", subject=SUBJECT, corpus_db=db, log_db=log_db)

    (_search.find_sources, instruments.document,
     agent_science.GeminiExtractor, agent_science.GeminiLocator) = saved
    return {"arm": "shipping", "a": a, "b": b, "net_find_calls": net.find_calls}


def _run_naive_term() -> dict:
    """Baseline: reuse by retrieval anchor (must_contain) only — ignores assertion text."""
    import agent_science
    from clearance import instruments, search as _search
    from clearance.locate import DEFAULT
    from clearance.facts import judge_claim, Claim
    from clearance.verdict import GREEN

    net = _Net()
    shelf: dict[str, dict] = {}  # term -> settled verdict payload

    def clear_naive(claims, *, subject: str) -> dict:
        rows = []
        parallel_calls = 0
        corpus_hits = 0
        for i, raw in enumerate(claims, 1):
            term = (raw.must_contain or raw.text).strip().lower()
            if term in shelf:
                corpus_hits += 1
                hit = shelf[term]
                rows.append({
                    "claim_id": f"C{i}", "text": raw.text, "label": "SOURCED",
                    "corpus_hit": True, "term": term,
                    "citation_url": hit["citation_url"],
                })
                continue
            parallel_calls += 1
            c = Claim(f"C{i}", raw.text, raw.source_url, raw.must_contain)
            v = judge_claim(c, locator=DEFAULT, live_search=True, fetch=True)
            if v.verdict == GREEN:
                shelf[term] = {
                    "citation_url": v.citation_url,
                    "quoted_terms": v.quoted_terms,
                    "established": raw.text,
                }
            rows.append({
                "claim_id": f"C{i}", "text": raw.text,
                "label": "SOURCED" if v.verdict == GREEN else "UNSOURCED",
                "corpus_hit": False, "term": term,
                "citation_url": v.citation_url, "cause": v.cause,
            })
        return {
            "parallel_calls": parallel_calls,
            "corpus_hits": corpus_hits,
            "rows": rows,
            "shelf_terms": sorted(shelf),
        }

    saved = (_search.find_sources, instruments.document)
    _search.find_sources = net.find_sources
    instruments.document = _fake_document
    try:
        a = clear_naive(CLAIMS_A, subject=SUBJECT)
        b = clear_naive(CLAIMS_B_PARAPHRASE, subject=SUBJECT)
    finally:
        _search.find_sources, instruments.document = saved

    return {"arm": "naive_term", "a": a, "b": b, "net_find_calls": net.find_calls}


def _compound_ok(run: dict) -> bool:
    a, b = run["a"], run["b"]
    return (a["parallel_calls"] > 0
            and b["parallel_calls"] < a["parallel_calls"]
            and b["corpus_hits"] >= 1)


def _print_arm(run: dict) -> None:
    a, b = run["a"], run["b"]
    ok = _compound_ok(run)
    print(f"\n=== ARM {run['arm']} ===")
    print(f"A parallel_calls={a['parallel_calls']}  corpus_hits={a.get('corpus_hits', 0)}")
    print(f"B parallel_calls={b['parallel_calls']}  corpus_hits={b['corpus_hits']}")
    print(f"compound (B_parallel < A and B corpus_hits>=1): {'PASS' if ok else 'FAIL'}")
    print("B rows:")
    for r in b["rows"]:
        print(f"  {r.get('claim_id')} corpus_hit={r.get('corpus_hit')} "
              f"label={r.get('label')} text={r.get('text', '')[:70]!r}")


def main() -> int:
    shipping = _run_shipping()
    naive = _run_naive_term()
    _print_arm(shipping)
    _print_arm(naive)

    s_ok = _compound_ok(shipping)
    n_ok = _compound_ok(naive)
    print("\n=== FINDING ===")
    print("Held-out: paraphrased B claims (same must_contain anchors as A, different wording).")
    print(f"Shipping exact-assertion compound: {'PASS' if s_ok else 'FAIL'}")
    print(f"Naive term-keyed compound:         {'PASS' if n_ok else 'FAIL'}")
    if n_ok and not s_ok:
        print("EMBARRASSMENT: naive term reuse beats shipping on the compound score.")
        print("Shipping is correct under exact-assertion constitution; the killer-demo")
        print("metric on paraphrased scripts rewards the weaker arm.")
    elif s_ok and not n_ok:
        print("Shipping beats naive on this set.")
    elif s_ok and n_ok:
        print("Both arms compound — no differential on this set.")
    else:
        print("Both arms fail compound — check fixtures / network fakes.")

    # Gate always exits 0 when it measured both arms; the finding is the product.
    # Exit 2 only if an arm crashed or returned empty.
    if not shipping["a"] or not naive["a"]:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
