"""Partner manifest — track compliance surface for judges and probes."""
from __future__ import annotations

import os
from pathlib import Path

from clearance import search as parallel_search
from cloud import agent as adk_agent

# Same rule as cloud.service.ADK_DEFAULT — kept here so /health works without
# importing the clearance desk module (avoids a hosted import cycle).
_ADK_OFF = ("0", "false", "no", "off")


def adk_default_enabled() -> bool:
    return os.environ.get("AGENT_BUILDER", "1").strip().lower() not in _ADK_OFF


def resolve_gemini_path() -> str:
    """How Gemini is reached — never returns a key value."""
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


def manifest(*, gemini_path: str | None = None, adk_default: bool | None = None) -> dict:
    root = Path(__file__).resolve().parents[1]
    if gemini_path is None:
        gemini_path = resolve_gemini_path()
    if adk_default is None:
        adk_default = adk_default_enabled() and adk_agent.adk_available()
    parallel_info = parallel_search.integration_info()
    parallel_key = bool(os.environ.get("PARALLEL_API_KEY"))
    # Do not hardcode True — a keyless cold start must read as not-yet-proven.
    parallel_at_runtime = parallel_key or bool(parallel_info.get("verified_search_id"))
    return {
        "event": "Agentic Cinema",
        "track": "Parallel",
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
                **parallel_info,
                "runtime": parallel_key,
                "module": "clearance/search.py",
                "called_from": "clearance/facts.py → judge_claim; clearance/cases.py live investigate",
            },
            "google_cloud": {
                "role": "Cloud Run dual surface: public clearance desk + private /cases",
                "module": "cloud/service.py · cloud/case_http.py · cloud/partner_status.py",
                "deploy": "deploy.sh",
                "mode": "private-workspaces+public-desk when AGENT_SCIENCE_HOSTED=1",
                "corpus_gcs": os.environ.get("CORPUS_GCS_URI"),
                "refusal_log_gcs": os.environ.get("REFUSAL_LOG_GCS_URI"),
                "public_partner_surfaces": [
                    "/health",
                    "/partners",
                    "/",
                    "/clear",
                    "/registry",
                    "/visibility/ui",
                ],
                "private_workspace_surfaces": ["/cases", "/api/cases", "/login"],
            },
            "agent_builder_adk": {
                "role": "default /clear engine",
                "module": "cloud/agent.py",
                "package": "google-adk",
                "version": adk_agent.adk_version(),
                "importable": adk_agent.adk_available(),
                "engine_default": "adk" if adk_default else "direct",
                "tool": "clear_script_tool",
            },
        },
        "track_checklist": {
            "parallel_search_at_runtime": parallel_at_runtime,
            "parallel_web_sdk": parallel_search.sdk_available(),
            "gemini_at_runtime": gemini_path != "none",
            "adk_agent_builder": adk_agent.adk_available() and adk_default,
            "hosted_url_required": True,
        },
        "receipts": [
            "docs/PARTNER-INTEGRATIONS-2026-08-30.md",
            "docs/FINDING-hosted-partner-strip-2026-09-05.md",
            "docs/FINDING-hosted-partner-strip-still-dark-2026-09-09.md",
            "docs/RECEIPT-adk-default-path-2026-08-30.md",
        ],
        "repo_root": str(root),
    }
