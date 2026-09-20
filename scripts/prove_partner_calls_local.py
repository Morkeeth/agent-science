#!/usr/bin/env python3
"""Prove partners are *called* on the clearance path — not merely configured.

Shape-only /health can green on GCP_PROJECT + PARALLEL_API_KEY env. This script
exercises the Parallel transport (mocked HTTP → real LIVE_CALLS + search_id) and
the ADK default engine selection, then prints a receipt JSON.

No network. No real keys. Exit 0 only when call-proof assertions hold.

Run: python3 scripts/prove_partner_calls_local.py
"""
from __future__ import annotations

import importlib
import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def _prove_parallel_call() -> dict:
    """Mock Parallel REST; call find_sources; require LIVE_CALLS + search_id."""
    from clearance import search

    search.reset_calls()
    body = {
        "search_id": "search_prove_local_partner_calls",
        "results": [
            {
                "url": "https://example.org/orphan-works",
                "title": "Orphan works",
                "excerpts": ["Directive 2012/28/EU establishes…"],
            }
        ],
    }
    fake_resp = MagicMock()
    fake_resp.read.return_value = json.dumps(body).encode()
    fake_resp.__enter__.return_value = fake_resp
    fake_resp.__exit__.return_value = False
    fake_resp.status = 200

    receipts = Path(tempfile.mkdtemp()) / "receipts.jsonl"
    cache = Path(tempfile.mkdtemp()) / "searches.json"
    real_receipts, real_cache = search.RECEIPTS, search.CACHE
    try:
        search.RECEIPTS = receipts
        search.CACHE = cache
        with patch.dict(os.environ, {"PARALLEL_API_KEY": "pk-prove-not-live"}, clear=False):
            # Force urllib path so the mock is hit regardless of SDK install.
            with patch.object(search, "sdk_available", return_value=False):
                with patch("urllib.request.urlopen", return_value=fake_resp):
                    hits = search.find_sources(
                        "The EU orphan works directive is Directive 2012/28/EU.",
                        ["Directive 2012/28/EU", "orphan works directive"],
                        live=True,
                        refresh=True,
                    )
        assert search.calls() >= 1, f"LIVE_CALLS stayed 0 (got {search.calls()})"
        assert search.last_search_id() == "search_prove_local_partner_calls"
        verified = search.last_verified_receipt()
        assert verified["verified_search_id"] == "search_prove_local_partner_calls"
        assert verified["verified_calls_logged"] >= 1
        assert hits, "find_sources returned no candidates"
        return {
            "live_calls": search.calls(),
            "last_search_id": search.last_search_id(),
            "verified_search_id": verified["verified_search_id"],
            "candidates": len(hits),
            "transport": "urllib-rest-mocked",
        }
    finally:
        search.RECEIPTS = real_receipts
        search.CACHE = real_cache


def _prove_adk_engine_selected() -> dict:
    """Default /clear path must select ADK when importable and AGENT_BUILDER on."""
    os.environ["AGENT_BUILDER"] = "1"
    svc = importlib.reload(importlib.import_module("cloud.service"))
    fake = {
        "ok": True,
        "engine": "adk",
        "claims_extracted": 1,
        "parallel_calls": 1,
        "adk_tool_calls": ["clear_script_tool"],
    }
    with patch.object(svc.adk_agent, "adk_available", return_value=True):
        with patch.object(svc.adk_agent, "run_clearance", return_value=fake) as run:
            out = svc._run_clearance("script", "prove-subject", "gemini-3.5-flash")
    assert out["engine"] == "adk", out
    run.assert_called_once()
    return {
        "engine": out["engine"],
        "adk_tool_calls": out.get("adk_tool_calls"),
        "parallel_calls_stamped": out.get("parallel_calls"),
    }


def _prove_health_honesty() -> dict:
    """GCP_PROJECT alone → gemini false; token present → gemini true."""
    from cloud import partners

    with patch.dict(
        os.environ,
        {
            "GCP_PROJECT": "hack-fleet",
            "GEMINI_API_KEY": "",
            "GOOGLE_API_KEY": "",
            "PARALLEL_API_KEY": "pk-prove",
            "AGENT_BUILDER": "1",
        },
        clear=False,
    ):
        with patch("clearance.gemini.vertex_project", return_value="hack-fleet"):
            with patch("clearance.gemini.vertex_token", return_value=None):
                bare = partners.health_payload(mode="prove", revision="honesty")
            with patch("clearance.gemini.vertex_token", return_value="ya29.prove"):
                with patch.object(partners.adk_agent, "adk_available", return_value=True):
                    with patch.object(
                        partners.adk_agent, "adk_version", return_value="2.7.1"
                    ):
                        callable_payload = partners.health_payload(
                            mode="prove", revision="honesty"
                        )
    assert bare["gemini"] is False and bare["gemini_path"] == "none", bare
    assert bare["gemini_configured"] is True, bare
    assert callable_payload["gemini"] is True, callable_payload
    assert callable_payload["gemini_path"] == "vertex:hack-fleet"
    assert callable_payload["engine_default"] == "adk"
    assert callable_payload["parallel"] is True
    return {
        "bare_gemini": bare["gemini"],
        "callable_gemini_path": callable_payload["gemini_path"],
        "engine_default": callable_payload["engine_default"],
    }


def main() -> int:
    receipt = {
        "script": "prove_partner_calls_local.py",
        "parallel_call": _prove_parallel_call(),
        "adk_engine": _prove_adk_engine_selected(),
        "health_honesty": _prove_health_honesty(),
        "adk_importable_now": __import__("cloud.agent", fromlist=["adk_available"]).adk_available(),
        "adk_version_now": __import__("cloud.agent", fromlist=["adk_version"]).adk_version(),
    }
    print(json.dumps(receipt, indent=2))
    print("PROVE_PARTNER_CALLS_LOCAL OK")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as e:
        print(f"PROVE_PARTNER_CALLS_LOCAL FAIL: {e}", file=sys.stderr)
        raise SystemExit(1)
