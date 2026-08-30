"""Clearance memo HTML — compound strip, action items, SOURCED verbatim block.

Runs against fixture dicts; no live APIs.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from clearance import corpus
from cloud.service import _report_html

VERBATIM = (
    "Directive 2012/28/EU of the European Parliament and of the Council of 25 "
    "October 2012 on certain permitted uses of orphan works"
)

FIXTURE_COMPOUND = {
    "ok": True,
    "subject": "orphan-works-fixture",
    "claims_extracted": 2,
    "sourced": 1,
    "unsourced": 1,
    "parallel_calls": 1,
    "prior_parallel_calls": 3,
    "parallel_delta": 2,
    "corpus_hits": 2,
    "corpus_remembered": 5,
    "rows": [
        {
            "claim_id": "C1",
            "text": "The EU passed the Orphan Works Directive in 2012.",
            "label": "SOURCED",
            "why": "verbatim in source",
            "citation_url": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=celex:32012L0028",
            "quoted_terms": VERBATIM,
            "corpus_hit": True,
        },
        {
            "claim_id": "C2",
            "text": "Britain launched a licensing scheme in October 2014.",
            "label": "UNSOURCED",
            "why": "we searched and no document we read states it",
            "cause": "search_found_no_admissible_source",
        },
    ],
}

FIXTURE_COLD = {
    "ok": True,
    "subject": "cold-shelf",
    "claims_extracted": 1,
    "sourced": 0,
    "unsourced": 1,
    "parallel_calls": 2,
    "corpus_hits": 0,
    "corpus_remembered": 1,
    "rows": [
        {
            "claim_id": "C1",
            "text": "A claim with no memory yet.",
            "label": "UNSOURCED",
            "why": "search found nothing",
        },
    ],
}


def t_report_html_compound_strip_and_delta():
    html = _report_html(FIXTURE_COMPOUND)
    assert "Compounding — this run" in html
    assert "Corpus hits" in html
    assert "3 → 1" in html
    assert "−2 vs last run" in html
    assert "Resolved from corpus" in html


def t_report_html_claims_requiring_action():
    html = _report_html(FIXTURE_COMPOUND)
    assert "Claims requiring action" in html
    assert "C2" in html
    assert "UNSOURCED" in html
    assert "licensing scheme in October 2014" in html
    assert "we searched and no document we read states it" in html


def t_report_html_sourced_verbatim_block():
    html = _report_html(FIXTURE_COMPOUND)
    assert "C1 — SOURCED" in html
    assert VERBATIM in html
    assert "<blockquote>" in html
    assert "celex:32012L0028" in html


def t_report_html_cold_first_pass_no_delta():
    html = _report_html(FIXTURE_COLD)
    assert "First pass on this shelf" in html
    assert "vs last run" not in html
    assert "Claims requiring action" in html


def t_corpus_prior_parallel_persists_per_subject():
    con = corpus.connect(":memory:")
    assert corpus.prior_parallel(con, "sub-a") is None
    corpus.remember_parallel(con, "sub-a", 4)
    assert corpus.prior_parallel(con, "sub-a") == 4
    corpus.remember_parallel(con, "sub-a", 2)
    assert corpus.prior_parallel(con, "sub-a") == 2
    assert corpus.prior_parallel(con, "sub-b") is None


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("t_") and callable(v)]
    failed = 0
    for fn in fns:
        try:
            fn()
            print(f"PASS  {fn.__name__}")
        except AssertionError as e:
            failed += 1
            print(f"FAIL  {fn.__name__}: {e}")
    print(f"\n{len(fns) - failed}/{len(fns)} passed")
    sys.exit(1 if failed else 0)
