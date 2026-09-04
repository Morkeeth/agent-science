"""Parallel SDK integration — transport selection and search_id lineage without live API."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def t_integration_info_shape():
    from clearance import search as S
    info = S.integration_info()
    assert info["partner"] == "parallel"
    assert info["sdk_package"] == "parallel-web"
    assert "transport" in info
    assert info["receipts_log"].endswith("search_receipts.jsonl")


def t_receipt_includes_search_id():
    import tempfile
    from clearance import search as S
    with tempfile.TemporaryDirectory() as td:
        saved = S.RECEIPTS
        S.RECEIPTS = Path(td) / "search_receipts.jsonl"
        try:
            S.log_receipt(
                source="parallel",
                objective="test objective",
                queries=["q1"],
                candidates=[S.Candidate(url="https://x", title="t", excerpt="e")],
                cache_hit=False,
                search_id="srch_test123",
            )
            row = json.loads(S.RECEIPTS.read_text().strip())
            assert row["search_id"] == "srch_test123"
            assert row["n_candidates"] == 1
        finally:
            S.RECEIPTS = saved


def t_sdk_path_sets_last_search_id():
    from clearance import search as S
    S.reset_calls()

    fake_result = MagicMock()
    fake_result.search_id = "srch_sdk_abc"
    fake_result.results = [
        MagicMock(url="https://example.com/doc", title="Doc", excerpts=["excerpt"]),
    ]
    fake_client = MagicMock()
    fake_client.search.return_value = fake_result

    with patch.object(S, "sdk_available", return_value=True):
        with patch.object(S, "load_key", return_value="test-key"):
            with patch.dict("sys.modules", {"parallel": MagicMock(Parallel=MagicMock(return_value=fake_client))}):
                payload, sid = S._live_search("obj", ["q"], mode="advanced")

    assert sid == "srch_sdk_abc"
    assert S.last_search_id() == "srch_sdk_abc"
    assert S.calls() == 1
    assert payload["results"][0]["url"] == "https://example.com/doc"


def t_partners_manifest_importable():
    from cloud import partners
    m = partners.manifest(gemini_path="vertex:hack-fleet", adk_default=True)
    assert m["track"] == "Parallel"
    assert "parallel" in m["partners"]
    assert "parallel_web_sdk" in m["track_checklist"]


def t_health_has_partners_route():
    svc = (ROOT / "cloud" / "service.py").read_text()
    assert 'path == "/partners"' in svc
    assert "parallel_sdk" in svc


def t_requirements_pins_parallel_web():
    req = (ROOT / "requirements.txt").read_text()
    assert "parallel-web==" in req


def t_cache_hits_meter_increments():
    """Search cache hits are metered separately from live Parallel calls."""
    import tempfile
    from clearance import search as S

    S.reset_calls()
    with tempfile.TemporaryDirectory() as td:
        saved_cache, saved_receipts = S.CACHE, S.RECEIPTS
        S.CACHE = Path(td) / "searches.json"
        S.RECEIPTS = Path(td) / "receipts.jsonl"
        try:
            # Seed cache as if a prior live call wrote it.
            S.CACHE.write_text(json.dumps({
                json.dumps({"o": "obj", "q": ["q1"], "m": "advanced"}, sort_keys=True): [
                    {"url": "https://example.com/a", "title": "A", "excerpt": "e"},
                ]
            }))
            out = S.find_sources("obj", ["q1"], mode="advanced", live=False)
            assert out and out[0].url.endswith("/a")
            assert S.cache_hits() == 1
            assert S.calls() == 0  # cache must not count as live
            info = S.integration_info()
            assert info["cache_hits"] == 1
        finally:
            S.CACHE, S.RECEIPTS = saved_cache, saved_receipts
            S.reset_calls()


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
