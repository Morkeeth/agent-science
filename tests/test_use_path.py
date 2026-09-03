"""Use-bar interceptor + session receipts."""
from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from clearance import use_path


def test_intercept_writes_receipt_and_lookup():
    tmp = Path(tempfile.mkdtemp())
    receipts = tmp / "receipts.jsonl"
    db = tmp / "refusal_log.db"
    os.environ["AGENT_SCIENCE_RECEIPTS"] = str(receipts)
    sid = "sess-test-use-bar"
    res = use_path.intercept(
        "2012/28/EU",
        mode="lookup",
        live=False,
        traffic="human",
        session_id=sid,
        db=db,
    )
    assert res.get("receipt_id")
    assert res.get("session_id") == sid
    assert receipts.exists()
    rows = use_path.read_receipts(path=receipts, limit=5)
    assert any(r["query"] == "2012/28/EU" for r in rows)
    found = use_path.assert_receipt_exists("2012/28/EU", session_id=sid, path=receipts)
    assert found["path"] == "agent-science-use-bar"
    # missing query must fail
    try:
        use_path.assert_receipt_exists("never-asked-zzz", path=receipts)
        raise AssertionError("expected AssertionError")
    except AssertionError as e:
        assert "no use-bar receipt" in str(e)


def test_intercept_gate_traffic_on_probe():
    tmp = Path(tempfile.mkdtemp())
    os.environ["AGENT_SCIENCE_RECEIPTS"] = str(tmp / "r.jsonl")
    res = use_path.intercept(
        "xyzzy-nonexistent-claim-99999",
        traffic="gate",
        db=tmp / "db.sqlite",
    )
    assert res["traffic"] == "gate"
    assert res["label"] == "NOT_CLEARED"


def test_use_bar_summary():
    tmp = Path(tempfile.mkdtemp())
    path = tmp / "r.jsonl"
    os.environ["AGENT_SCIENCE_RECEIPTS"] = str(path)
    use_path.intercept("2012/28/EU", db=tmp / "a.db", traffic="human")
    use_path.intercept(
        "xyzzy-nonexistent-claim-99999", db=tmp / "a.db", traffic="gate"
    )
    summary = use_path.use_bar_summary(path=path)
    assert summary["n"] == 2
    assert summary["by_traffic"].get("human", 0) >= 1
    assert summary["by_traffic"].get("gate", 0) >= 1


def test_mcp_tool_registered():
    from clearance import mcp_server
    names = {t["name"] for t in mcp_server.TOOLS}
    assert "science_use_bar" in names
    assert "science_lookup" in names
    out = mcp_server.handle_tool(
        "science_use_bar",
        {"query": "xyzzy-nonexistent-claim-99999", "traffic": "gate"},
    )
    import json
    data = json.loads(out)
    assert data["label"] == "NOT_CLEARED"
    assert data.get("receipt_id")


if __name__ == "__main__":
    test_intercept_writes_receipt_and_lookup()
    test_intercept_gate_traffic_on_probe()
    test_use_bar_summary()
    test_mcp_tool_registered()
    print("use_path tests OK")
