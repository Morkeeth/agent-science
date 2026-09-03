"""Traffic class — human vs gate/demo/fleet."""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from clearance import refusal_log, traffic, query_analytics, stack_search


def test_classify_gate_probe():
    assert traffic.classify("xyzzy-nonexistent-claim-99999") == "gate"
    assert traffic.classify("science_lookup MCP cursor") == "gate"


def test_classify_demo_ralph():
    assert traffic.classify("ralph loop agentic") == "demo"
    assert traffic.classify("Ralph Loop Agentic Practice") == "demo"


def test_explicit_traffic_wins():
    assert traffic.classify("ralph loop agentic", traffic="human") == "human"
    assert traffic.classify("anything", traffic="fleet") == "fleet"


def test_gate_subject_prefix():
    assert traffic.classify("Directive 2012/28/EU", subject="trial-1200") == "gate"


def test_popular_human_excludes_demo(tmp_path: Path | None = None):
    db = Path(tempfile.mkdtemp()) / "refusal_log.db"
    con = refusal_log.connect(db)
    # seed via lookup with traffic tags
    stack_search.lookup("ralph loop agentic", live=False, db=db, traffic="demo")
    stack_search.lookup(
        "xyzzy-nonexistent-claim-99999", live=False, db=db, traffic="gate"
    )
    # a non-probe ask
    stack_search.lookup("zenity-human-only-ask-zzz", live=False, db=db, traffic="human")
    all_q = query_analytics.popular_queries(db=db, limit=20, traffic="all")
    human = query_analytics.popular_queries(db=db, limit=20, traffic="human")
    all_norm = {r["qnorm"] for r in all_q}
    human_norm = {r["qnorm"] for r in human}
    assert "ralph loop agentic" in all_norm
    assert "ralph loop agentic" not in human_norm
    assert "xyzzy-nonexistent-claim-99999" not in human_norm
    assert "zenity-human-only-ask-zzz" in human_norm
    notes = query_analytics.traffic_notes(db=db)
    assert notes["by_traffic"].get("demo", 0) >= 1
    assert notes["by_traffic"].get("gate", 0) >= 1
    assert "traffic_notes" in query_analytics.report(db=db, limit=5)


def test_log_query_stores_traffic():
    db = Path(tempfile.mkdtemp()) / "r.db"
    con = refusal_log.connect(db)
    refusal_log.log_query(
        con,
        query="xyzzy-nonexistent-claim-99999",
        result={"label": "NOT_CLEARED", "cause": "not_in_registry"},
    )
    row = dict(con.execute("SELECT traffic FROM queries").fetchone())
    assert row["traffic"] == "gate"


if __name__ == "__main__":
    test_classify_gate_probe()
    test_classify_demo_ralph()
    test_explicit_traffic_wins()
    test_gate_subject_prefix()
    test_popular_human_excludes_demo()
    test_log_query_stores_traffic()
    print("traffic tests OK")
