"""Popular queries endpoint."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from clearance import query_analytics


def test_popular_report_shape():
    data = query_analytics.report(limit=5)
    assert "popular_queries" in data
    assert "optimization_targets" in data
    assert "alias_candidates" in data


def test_popular_page_renders():
    from cloud.service import _popular_page
    html = _popular_page(limit=5)
    assert "Popular queries" in html
    assert "/popular" in html


if __name__ == "__main__":
    test_popular_report_shape()
    test_popular_page_renders()
    print("popular tests OK")
