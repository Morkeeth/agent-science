"""Partner manifest + shared health payload — track compliance for judges and probes.

Hosted private-workspace mode and local desk must report the same partner fields.
A thin /health that only says ok=true is not partner proof.
"""
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


def health_payload(*, mode: str | None = None, revision: str | None = None) -> dict:
    """Judge-readable partner surface. Same shape on local desk and hosted Cloud Run."""
    gemini_path = resolve_gemini_path()
    adk_ok = adk_agent.adk_available()
    adk_default = adk_default_enabled() and adk_ok
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
    if mode is not None:
        payload["mode"] = mode
    if revision is not None:
        payload["revision"] = revision
    return payload


def partner_manifest_for_runtime() -> dict:
    gemini_path = resolve_gemini_path()
    adk_default = adk_default_enabled() and adk_agent.adk_available()
    return manifest(gemini_path=gemini_path, adk_default=adk_default)


def manifest(*, gemini_path: str, adk_default: bool) -> dict:
    root = Path(__file__).resolve().parents[1]
    hosted = bool(os.environ.get("AGENT_SCIENCE_HOSTED") or os.environ.get("K_SERVICE"))
    return {
        "event": "Agentic Cinema",
        "track": "Parallel",
        "mode": "private-workspaces" if hosted else "local-desk",
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
                "called_from": (
                    "clearance/facts.py → judge_claim (local /clear); "
                    "clearance/cases.py → research create/refresh live (hosted workspaces)"
                ),
            },
            "google_cloud": {
                "role": "Cloud Run private workspaces + Secret Manager + GCS shelves",
                "module": "cloud/service.py → cloud/case_http.py when hosted",
                "deploy": "deploy.sh",
                "workspace_bucket": os.environ.get("AGENT_SCIENCE_WORKSPACE_BUCKET"),
                "corpus_gcs": os.environ.get("CORPUS_GCS_URI"),
                "refusal_log_gcs": os.environ.get("REFUSAL_LOG_GCS_URI"),
                "notes": (
                    "Public /health + /partners remain unauthenticated for track proof. "
                    "/clear, /search, /cases mutations require workspace access."
                ),
            },
            "agent_builder_adk": {
                "role": "default /clear engine (local desk + image default)",
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
            "partner_health_public": True,
        },
        "receipts": [
            "docs/PARTNER-INTEGRATIONS-2026-08-30.md",
            "docs/PARTNER-INTEGRATION-RESEARCH-2026-08-31.md",
            "docs/RECEIPT-adk-default-path-2026-08-30.md",
            "docs/RECEIPT-partner-hosted-admissibility-2026-09-15.md",
        ],
        "repo_root": str(root),
    }
