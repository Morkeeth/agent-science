"""Popular queries endpoint."""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from clearance import query_analytics, stack_search


def test_popular_report_shape():
    data = query_analytics.report(limit=5)
    assert "popular_queries" in data
    assert "popular_human" in data
    assert "traffic_notes" in data
    assert "optimization_targets" in data
    assert "alias_candidates" in data


def test_popular_page_renders():
    from cloud.service import _popular_page
    html = _popular_page(limit=5)
    assert "Popular queries" in html
    assert "/popular" in html
    assert "Human view" in html


def test_human_view_drops_demo():
    db = Path(tempfile.mkdtemp()) / "p.db"
    stack_search.lookup("ralph loop agentic", live=False, db=db, traffic="demo")
    stack_search.lookup("human-unique-query-abc123", live=False, db=db, traffic="human")
    human = query_analytics.popular_queries(db=db, traffic="human")
    norms = {r["qnorm"] for r in human}
    assert "ralph loop agentic" not in norms
    assert "human-unique-query-abc123" in norms


if __name__ == "__main__":
    test_popular_report_shape()
    test_popular_page_renders()
    test_human_view_drops_demo()
    print("popular tests OK")
