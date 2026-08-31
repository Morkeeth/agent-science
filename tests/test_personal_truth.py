"""Personal truth DB — index asks, skill verdicts, field fetches."""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def t_record_ask_and_lookup():
    from clearance import personal_truth as PT
    with tempfile.TemporaryDirectory() as td:
        db = Path(td) / "truth.db"
        primary = {
            "label": "SOURCED",
            "verdict": "GREEN",
            "citation_url": "https://example.com/x",
            "quoted_terms": "exact span here",
            "cost_tier": "free",
        }
        aid = PT.record_ask("demo query", primary, path=db)
        assert aid >= 1
        hit = PT.lookup_local("demo query", path=db)
        assert hit and hit["result_label"] == "SOURCED"
        truths = PT.recent_truths(kind="claim", path=db)
        assert len(truths) == 1
        assert truths[0]["citation_url"] == "https://example.com/x"


def t_skill_magnet_bridge():
    from clearance import personal_truth as PT
    with tempfile.TemporaryDirectory() as td:
        db = Path(td) / "truth.db"
        tid = PT.record_skill_truth(
            "agent-science-websearch", "helped",
            probe="demo-pass-rate", note="Magnet bridge stub", path=db,
        )
        assert tid >= 1
        rows = PT.recent_truths(kind="skill", path=db)
        assert rows[0]["verdict"] == "helped"
        st = PT.stats(path=db)
        assert st["skills"] == 1


def t_ingest_field_signals():
    from clearance import personal_truth as PT
    with tempfile.TemporaryDirectory() as td:
        db = Path(td) / "truth.db"
        out = PT.ingest_field_signals(path=db)
        assert out["ok"] is True
        assert out["fetched"] >= 1
        assert out["fetches"] == out["fetched"]


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
