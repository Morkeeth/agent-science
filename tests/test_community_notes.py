"""Tests for community notes stub."""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def t_list_seed():
    from clearance import community_notes as CN
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "notes.jsonl"
        rows = CN.list_notes(path=p)
        assert len(rows) >= 1
        assert rows[0].get("claim")


def t_upload_and_dispute():
    from clearance import community_notes as CN
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "notes.jsonl"
        row = CN.upload("test claim for film", submitter="test", path=p)
        assert row["id"]
        rows = CN.list_notes(path=p)
        assert any(r["id"] == row["id"] for r in rows)
        disputed = CN.dispute(row["id"], "disagree — no source", path=p)
        assert disputed and disputed["status"] == "disputed"


def t_cli_list():
    import subprocess
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "notes.jsonl"
        proc = subprocess.run(
            [sys.executable, "-m", "clearance.stack_cli", "notes", "list",
             "--path", str(p), "--json"],
            capture_output=True, text=True, cwd=str(ROOT),
        )
        assert proc.returncode == 0
        assert "claim" in proc.stdout


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
