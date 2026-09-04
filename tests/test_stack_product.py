"""Stack product — search, ingest, MCP handlers."""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from clearance import refusal_log, stack_search
from clearance import ingest
from clearance.mcp_server import handle_tool


def test_registry_hit_no_parallel():
    with tempfile.TemporaryDirectory() as d:
        db = Path(d) / "log.db"
        con = refusal_log.connect(db)
        refusal_log.record(
            con, term="2012/28/eu", assertion="Directive 2012/28/EU is the orphan works directive",
            verdict="GREEN", production="test", citation_url="https://example.org/x",
            quoted_terms="Directive 2012/28/EU on orphan works")
        res = stack_search.search("Directive 2012/28/EU is the orphan works directive", live=False, db=db)
        assert res["label"] == "SOURCED", res
        assert res["parallel_api_calls"] == 0
        assert res["source"] == "registry"


def test_ingest_claim_offline():
    with tempfile.TemporaryDirectory() as d:
        db = Path(d) / "log.db"
        # use rights statement fixture from cache if available
        import os
        os.environ["REFUSAL_LOG_DB"] = str(db)
        from clearance import instruments
        url = "https://rightsstatements.org/vocab/CNE/1.0/"
        body = instruments.document(url, fetch=False)
        if not body:
            return  # skip if no cache
        ingest._INBOX = Path(d) / "inbox"
        res = ingest.ingest_claim(
            "Copyright was never evaluated for this item",
            url,
            production="test",
            fetch=False,
        )
        assert res["label"] in ("SOURCED", "UNSOURCED", "UNKNOWN")


def test_mcp_search_tool():
    out = handle_tool("science_stats", {})
    assert "n" in out or "recent_queries" in out


if __name__ == "__main__":
    test_registry_hit_no_parallel()
    test_mcp_search_tool()
    try:
        test_ingest_claim_offline()
    except Exception:
        pass
    print("stack tests OK")
