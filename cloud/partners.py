"""Partner manifest — track compliance surface for judges and probes.

Hosted private-workspaces still expose GET /health and GET /partners without
auth. Legacy /clear · /search · /ingest stay local-only on Cloud Run.
"""
from __future__ import annotations

import os
from pathlib import Path

from clearance import search as parallel_search
from cloud import agent as adk_agent


def adk_default_enabled() -> bool:
    return os.environ.get("AGENT_BUILDER", "1").strip().lower() not in (
        "0",
        "false",
        "no",
        "off",
    )


def resolve_gemini_path() -> str:
    """How Gemini will be reached on this process — never invents a key."""
    if os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY"):
        return "api-key"
    proj = (
        os.environ.get("GCP_PROJECT")
        or os.environ.get("GOOGLE_CLOUD_PROJECT")
        or (os.environ.get("K_SERVICE") and "adc")
    )
    if proj:
        return f"vertex:{proj}"
    try:
        from clearance import gemini as _g

        p = _g.vertex_project()
        if p and _g.vertex_token():
            return f"vertex:{p}"
    except Exception:
        pass
    return "none"


def health(*, mode: str | None = None) -> dict:
    """Public partner liveness payload for GET /health (local desk and hosted)."""
    path = resolve_gemini_path()
    adk_ok = adk_agent.adk_available()
    adk_default = adk_default_enabled() and adk_ok
    payload = {
        "ok": True,
        "service": "agent-science",
        "gemini": path != "none",
        "gemini_path": path,
        "parallel": bool(os.environ.get("PARALLEL_API_KEY")),
        "parallel_sdk": parallel_search.sdk_available(),
        "parallel_sdk_version": parallel_search.sdk_version(),
        "parallel_transport": parallel_search.integration_info()["transport"],
        "last_parallel_search_id": parallel_search.last_search_id(),
        "agent_builder": adk_ok,
        "adk_version": adk_agent.adk_version(),
        "engine_default": "adk" if adk_default else "direct",
        "revision": os.getenv("K_REVISION", "local"),
    }
    if mode:
        payload["mode"] = mode
    return payload


def manifest(*, gemini_path: str | None = None, adk_default: bool | None = None) -> dict:
    root = Path(__file__).resolve().parents[1]
    path = resolve_gemini_path() if gemini_path is None else gemini_path
    if adk_default is None:
        adk_default = adk_default_enabled() and adk_agent.adk_available()
    return {
        "event": "Agentic Cinema",
        "track": "Parallel",
        "partners": {
            "gemini_vertex": {
                "role": "claim extraction + passage locate",
                "module": "clearance/gemini.py",
                "runtime": path != "none",
                "gemini_path": path,
                "secret_manager": False,
                "notes": "Vertex ADC on Cloud Run; API key local dev only",
            },
            "parallel": {
                **parallel_search.integration_info(),
                "runtime": bool(os.environ.get("PARALLEL_API_KEY")),
                "module": "clearance/search.py",
                "called_from": "clearance/facts.py → judge_claim",
            },
            "google_cloud": {
                "role": "Cloud Run desk + GCS corpus shelf",
                "module": "cloud/service.py",
                "deploy": "deploy.sh",
                "corpus_gcs": os.environ.get("CORPUS_GCS_URI"),
                "refusal_log_gcs": os.environ.get("REFUSAL_LOG_GCS_URI"),
            },
            "agent_builder_adk": {
                "role": "default /clear engine (local desk); hosted reports importability",
                "module": "cloud/agent.py",
                "package": "google-adk",
                "version": adk_agent.adk_version(),
                "importable": adk_agent.adk_available(),
                "engine_default": "adk" if adk_default else "direct",
                "tool": "clear_script_tool",
            },
        },
        "track_checklist": {
            "parallel_search_at_runtime": True,
            "parallel_web_sdk": parallel_search.sdk_available(),
            "gemini_at_runtime": path != "none",
            "adk_agent_builder": adk_agent.adk_available() and adk_default,
            "hosted_url_required": True,
            "public_health_partners": True,
            "public_partners_manifest": True,
            "hosted_clear_local_only": True,
        },
        "receipts": [
            "docs/PARTNER-INTEGRATIONS-2026-08-30.md",
            "docs/PARTNER-INTEGRATION-RESEARCH-2026-08-31.md",
            "docs/RECEIPT-adk-default-path-2026-08-30.md",
            "docs/FINDING-hosted-partner-health-regression-2026-09-11.md",
        ],
        "repo_root": str(root),
    }


def partner_proof_score(health_payload: dict, partners_payload: dict | None = None) -> dict:
    """Baseline-scorable stranger proof: how many partners are visible without auth.

    Naive arm (stripped private-workspaces health) scores low. Shipping arm must
    expose Gemini, Parallel, Cloud Run revision, and ADK engine_default.
    """
    h = health_payload or {}
    checks = {
        "gemini_path": "gemini_path" in h,
        "gemini_flag": "gemini" in h,
        "parallel_flag": "parallel" in h,
        "parallel_sdk": "parallel_sdk" in h,
        "engine_default": h.get("engine_default") in ("adk", "direct"),
        "agent_builder": "agent_builder" in h,
        "revision": bool(h.get("revision")),
        "partners_checklist": bool(
            partners_payload
            and isinstance(partners_payload.get("track_checklist"), dict)
            and partners_payload["track_checklist"].get("parallel_search_at_runtime") is True
        ),
    }
    scored = sum(1 for v in checks.values() if v)
    return {
        "score": scored,
        "denominator": len(checks),
        "checks": checks,
    }
