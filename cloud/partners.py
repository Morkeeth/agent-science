"""Partner manifest — track compliance surface for judges and probes."""
from __future__ import annotations

import os
from pathlib import Path

from clearance import search as parallel_search
from cloud import agent as adk_agent


def detect_gemini_path() -> str:
    """Return the runtime Gemini path label for /health and /partners."""
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


def adk_is_default() -> bool:
    """True when AGENT_BUILDER is on and google-adk imports."""
    flag = os.environ.get("AGENT_BUILDER", "1").strip().lower()
    enabled = flag not in ("0", "false", "no", "off")
    return enabled and adk_agent.adk_available()


def health_payload(*, mode: str | None = None) -> dict:
    """Judge-facing /health shape — partners must remain visible on hosted."""
    gemini_path = detect_gemini_path()
    adk_ok = adk_agent.adk_available()
    adk_default = adk_is_default()
    payload = {
        "ok": True,
        "service": "agent-science",
        "gemini": gemini_path != "none",
        "gemini_path": gemini_path,
        "parallel": bool(os.environ.get("PARALLEL_API_KEY")),
        "parallel_sdk": parallel_search.sdk_available(),
        "parallel_sdk_version": parallel_search.sdk_version(),
        "parallel_transport": parallel_search.integration_info()["transport"],
        "last_parallel_search_id": parallel_search.last_search_id(),
        "agent_builder": adk_ok,
        "adk_version": adk_agent.adk_version(),
        "engine_default": "adk" if adk_default else "direct",
    }
    if mode:
        payload["mode"] = mode
    revision = os.getenv("K_REVISION")
    if revision:
        payload["revision"] = revision
    return payload


def manifest(*, gemini_path: str | None = None, adk_default: bool | None = None) -> dict:
    root = Path(__file__).resolve().parents[1]
    gemini_path = detect_gemini_path() if gemini_path is None else gemini_path
    adk_default = adk_is_default() if adk_default is None else adk_default
    return {
        "event": "Agentic Cinema",
        "track": "Parallel",
        "mode": (
            "private-workspaces"
            if (os.getenv("AGENT_SCIENCE_HOSTED") == "1" or os.getenv("K_SERVICE"))
            else "local-desk"
        ),
        "partners": {
            "gemini_vertex": {
                "role": "claim extraction + passage locate",
                "module": "clearance/gemini.py",
                "runtime": gemini_path != "none",
                "gemini_path": gemini_path,
                "secret_manager": False,
                "notes": "Vertex ADC on Cloud Run; API key local dev only",
            },
            "parallel": {
                **parallel_search.integration_info(),
                "runtime": bool(os.environ.get("PARALLEL_API_KEY")),
                "module": "clearance/search.py",
                "called_from": "clearance/facts.py → judge_claim; clearance/cases.py → find_sources",
            },
            "google_cloud": {
                "role": "Cloud Run desk + private workspaces + GCS corpus shelf",
                "module": "cloud/service.py",
                "deploy": "deploy.sh",
                "corpus_gcs": os.environ.get("CORPUS_GCS_URI"),
                "refusal_log_gcs": os.environ.get("REFUSAL_LOG_GCS_URI"),
            },
            "agent_builder_adk": {
                "role": "default /clear engine (local desk); model path for hosted research",
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
            "gemini_at_runtime": gemini_path != "none",
            "adk_agent_builder": adk_agent.adk_available() and adk_default,
            "hosted_url_required": True,
            "public_clear_local_only": True,
        },
        "surfaces": {
            "health": "GET /health — partner fields always public",
            "partners": "GET /partners — track manifest always public",
            "clear": "POST /clear — local desk only (not on hosted private-workspaces)",
            "cases": "GET|POST /cases · /api/cases — hosted workspace (auth required)",
        },
        "receipts": [
            "docs/PARTNER-INTEGRATIONS-2026-08-30.md",
            "docs/PARTNER-INTEGRATION-RESEARCH-2026-08-31.md",
            "docs/RECEIPT-adk-default-path-2026-08-30.md",
        ],
        "repo_root": str(root),
    }
