"""Vision wiring — registry on hosted desk + compound delta."""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from clearance import run_history
import ask_registry
from cloud.service import _desk_page, _report_html


def test_render_page_includes_stats_and_desk_link():
    html = ask_registry.render_page(q="")
    assert "claims in registry" in html
    assert "clearance desk" in html


def test_run_history_records_prior_for_compound_delta():
    with tempfile.TemporaryDirectory() as d:
        hist = Path(d) / "run_history.json"
        import os
        os.environ["RUN_HISTORY_JSON"] = str(hist)
        run_history.record("orphan-works", parallel_api_calls=5, corpus_hits=0, claims=3)
        prior = run_history.prior("orphan-works")
        assert prior["parallel_api_calls"] == 5
        html = _report_html({
            "subject": "orphan-works",
            "parallel_api_calls": 2,
            "corpus_hits": 2,
            "corpus_remembered": 4,
            "prior_run": prior,
            "rows": [],
        })
        assert "5" in html and "2" in html
        assert "Compound" in html


def test_desk_page_links_registry():
    page = _desk_page()
    assert "/registry" in page
    assert "websearch companion" in page


if __name__ == "__main__":
    test_render_page_includes_stats_and_desk_link()
    test_run_history_records_prior_for_compound_delta()
    test_desk_page_links_registry()
    print("3/3 passed")
