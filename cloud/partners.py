"""Partner manifest + health payload — track compliance surface for judges and probes."""
from __future__ import annotations

import os
from pathlib import Path

from clearance import search as parallel_search
from cloud import agent as adk_agent


def adk_default_enabled() -> bool:
    return os.environ.get("AGENT_BUILDER", "1").strip().lower() not in (
        "0", "false", "off", "no",
    )


def resolve_gemini_path() -> str:
    """How Gemini will be reached — never returns a secret."""
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


def health_payload(*, mode: str | None = None) -> dict:
    """Public readiness JSON for GET /health — local desk and hosted workspaces.

    Reports partner wiring without secrets. Used by both cloud/service.py (local
    desk) and cloud/case_http.py (private workspaces). A hosted mode that omits
    these fields is a regression: judges cannot see Parallel/Gemini/ADK.
    """
    path = resolve_gemini_path()
    adk_ok = adk_agent.adk_available()
    adk_default = adk_default_enabled() and adk_ok
    out = {
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
    }
    if mode is not None:
        out["mode"] = mode
        out["revision"] = os.getenv("K_REVISION", "local")
        # Hosted shared /clear is intentionally gated; Parallel still runs on
        # authenticated live research (cloud/case_worker.py → clearance/cases).
        out["clear_path"] = "local-desk"
        out["parallel_hosted_path"] = "workspace-live-research"
    return out


def manifest(*, gemini_path: str | None = None, adk_default: bool | None = None) -> dict:
    root = Path(__file__).resolve().parents[1]
    path = gemini_path if gemini_path is not None else resolve_gemini_path()
    if adk_default is None:
        adk_default = adk_default_enabled() and adk_agent.adk_available()
    return {
        "event": "Agentic Cinema",
        "track": "Parallel",
        "partners": {
            "gemini_vertex": {
                "role": "claim extraction + passage locate + research model",
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
                "called_from": (
                    "clearance/facts.py → judge_claim; "
                    "clearance/cases.py → live create/refresh; "
                    "cloud/case_worker.py (hosted research)"
                ),
            },
            "google_cloud": {
                "role": "Cloud Run private workspaces + Secret Manager + GCS",
                "module": "cloud/service.py → cloud/case_http.py when hosted",
                "deploy": "deploy.sh",
                "workspace_bucket": os.environ.get("AGENT_SCIENCE_WORKSPACE_BUCKET"),
                "corpus_gcs": os.environ.get("CORPUS_GCS_URI"),
                "refusal_log_gcs": os.environ.get("REFUSAL_LOG_GCS_URI"),
            },
            "agent_builder_adk": {
                "role": "default local /clear engine (AGENT_BUILDER=1)",
                "module": "cloud/agent.py",
                "package": "google-adk",
                "version": adk_agent.adk_version(),
                "importable": adk_agent.adk_available(),
                "engine_default": "adk" if adk_default else "direct",
                "tool": "clear_script_tool",
                "hosted_note": "Shared POST /clear is local-only; health still reports engine_default",
            },
        },
        "track_checklist": {
            "parallel_search_at_runtime": True,
            "parallel_web_sdk": parallel_search.sdk_available(),
            "gemini_at_runtime": path != "none",
            "adk_agent_builder": adk_agent.adk_available() and adk_default,
            "hosted_url_required": True,
            "public_partner_health": True,
            "shared_clear_local_only": True,
        },
        "receipts": [
            "docs/PARTNER-INTEGRATIONS-2026-08-30.md",
            "docs/PARTNER-INTEGRATION-RESEARCH-2026-08-31.md",
            "docs/RECEIPT-adk-default-path-2026-08-30.md",
            "docs/FINDING-hosted-partner-surfaces-2026-09-10.md",
        ],
        "repo_root": str(root),
    }
