#!/usr/bin/env python3
"""Clearance memo HTML — compound strip + action list + sourced evidence.

Moonshot slice 2: gap report reads like a clearance memo, not a log dump.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from cloud.service import _report_html  # noqa: E402


def _fixture(*, hits: int = 1) -> dict:
    return {
        "subject": "orphan-works",
        "claims_extracted": 3,
        "sourced": 1,
        "unsourced": 2,
        "parallel_calls": 2 if hits else 5,
        "corpus_hits": hits,
        "corpus_remembered": 7,
        "rows": [
            {
                "claim_id": "C1",
                "label": "UNSOURCED",
                "text": "The directive entered force in 2012.",
                "why": "search_found_no_admissible_source",
            },
            {
                "claim_id": "C2",
                "label": "SOURCED",
                "text": "Orphan works may be used after diligent search.",
                "citation_url": "https://example.org/instrument",
                "quoted_terms": "A diligent search must be documented.",
                "corpus_hit": bool(hits),
            },
        ],
    }


def test_compound_strip_when_corpus_hits():
    html = _report_html(_fixture(hits=2))
    assert "Compounding — this run" in html
    assert "Parallel API" in html
    assert "Corpus hits" in html
    assert "2" in html  # hits count visible
    print("PASS  test_compound_strip_when_corpus_hits")


def test_first_pass_cold_strip():
    html = _report_html(_fixture(hits=0))
    assert "First pass on this shelf" in html
    assert "second" in html.lower()
    print("PASS  test_first_pass_cold_strip")


def test_action_items_before_sourced():
    html = _report_html(_fixture())
    action = html.index("<h2>Claims requiring action</h2>")
    sourced = html.index("<section class='sourced'>")
    assert action < sourced
    assert "UNSOURCED" in html
    assert "search_found_no_admissible_source" in html
    print("PASS  test_action_items_before_sourced")


def test_sourced_verbatim_blockquote():
    html = _report_html(_fixture())
    assert "blockquote" in html
    assert "diligent search must be documented" in html.lower()
    assert "https://example.org/instrument" in html
    print("PASS  test_sourced_verbatim_blockquote")


def test_clearance_memo_meta():
    html = _report_html(_fixture())
    assert "clearance memo" in html
    assert "orphan-works" in html
    print("PASS  test_clearance_memo_meta")


if __name__ == "__main__":
    test_compound_strip_when_corpus_hits()
    test_first_pass_cold_strip()
    test_action_items_before_sourced()
    test_sourced_verbatim_blockquote()
    test_clearance_memo_meta()
    print("\n5/5 passed")
