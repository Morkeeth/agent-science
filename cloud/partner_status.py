"""Shared partner health + path detection for hosted dual surface.

Private workspaces and the public clearance desk share one Cloud Run process.
/health and /partners must report partner wiring even when AGENT_SCIENCE_HOSTED=1 —
a stripped liveness JSON is how partner admissibility went dark on revision 00026.
"""
from __future__ import annotations

import os
from urllib.parse import urlparse

from clearance import search as parallel_search
from cloud import agent as adk_agent
from cloud import partners as partner_manifest


def is_hosted() -> bool:
    return os.getenv("AGENT_SCIENCE_HOSTED") == "1" or bool(os.getenv("K_SERVICE"))


def is_workspace_path(raw_path: str) -> bool:
    """Routes that stay behind workspace auth. Everything else is the public desk."""
    path = urlparse(raw_path).path.rstrip("/") or "/"
    if path in ("/login", "/logout", "/cases"):
        return True
    if path.startswith("/cases/") or path.startswith("/api/"):
        return True
    return False


def resolve_gemini_path() -> str:
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


def health_payload(*, adk_default: bool) -> dict:
    gemini_path = resolve_gemini_path()
    adk_ok = adk_agent.adk_available()
    adk_on = bool(adk_default and adk_ok)
    hosted = is_hosted()
    return {
        "ok": True,
        "service": "agent-science",
        "mode": "private-workspaces+public-desk" if hosted else "local",
        "revision": os.getenv("K_REVISION", "local"),
        "gemini": gemini_path != "none",
        "gemini_path": gemini_path,
        "parallel": bool(os.environ.get("PARALLEL_API_KEY")),
        "parallel_sdk": parallel_search.sdk_available(),
        "parallel_sdk_version": parallel_search.sdk_version(),
        "parallel_transport": parallel_search.integration_info()["transport"],
        "last_parallel_search_id": parallel_search.last_search_id(),
        "agent_builder": adk_ok,
        "adk_version": adk_agent.adk_version(),
        "engine_default": "adk" if adk_on else "direct",
        "workspace": hosted,
        "public_desk": True,
    }


def partners_payload(*, adk_default: bool) -> dict:
    gemini_path = resolve_gemini_path()
    adk_ok = adk_agent.adk_available()
    return partner_manifest.manifest(
        gemini_path=gemini_path,
        adk_default=bool(adk_default and adk_ok),
    )
