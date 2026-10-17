"""Partner manifest — track compliance surface for judges and probes."""
from __future__ import annotations

import os
from pathlib import Path

from clearance import search as parallel_search
from cloud import agent as adk_agent


def adk_default_enabled() -> bool:
    """AGENT_BUILDER defaults on; only an explicit off switch selects direct."""
    return os.environ.get("AGENT_BUILDER", "1").strip().lower() not in (
        "0", "false", "off", "no",
    )


def resolve_gemini_path() -> str:
    """Report how Gemini is reached — never the secret itself."""
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
    """Public /health shape — partner proof without secrets.

    Private-workspaces Cloud Run must return the same partner fields as the
    local desk. A stripped liveness-only body made verify_partners_hosted.sh
    read green on ok=true while gemini/parallel/adk were invisible (2026-09-16).
    """
    gemini_path = resolve_gemini_path()
    adk_ok = adk_agent.adk_available()
    adk_default = adk_default_enabled() and adk_ok
    out = {
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
        out["mode"] = mode
    if revision is not None:
        out["revision"] = revision
    return out


def shipping_health_ok(health: dict | None) -> tuple[bool, str]:
    """Same asserts as verify_partners_hosted.sh step 1.

    Parallel callable ≠ SDK installed. A key + urllib-rest transport is a
    working Parallel path (clearance/search.py REST fallback). Requiring
    parallel_sdk=True false-reds that shape — FINDING-parallel-sdk-assert-vs-urllib-2026-09-23.
    """
    if not isinstance(health, dict):
        return False, "body not JSON object"
    req = {
        "ok": True,
        "gemini": True,
        "parallel": True,
        "agent_builder": True,
        "engine_default": "adk",
    }
    for k, v in req.items():
        got = health.get(k)
        if got != v:
            return False, f"{k}: expected {v!r}, got {got!r} (keys={sorted(health)})"
    if "parallel_sdk" not in health:
        return False, f"parallel_sdk missing (keys={sorted(health)})"
    if not isinstance(health.get("parallel_sdk"), bool):
        return False, f"parallel_sdk must be bool, got {health.get('parallel_sdk')!r}"
    transport = health.get("parallel_transport")
    allowed = ("parallel-web", "urllib-rest")
    if transport not in allowed:
        return False, (
            f"parallel_transport: expected one of {allowed!r}, got {transport!r}"
        )
    if transport == "parallel-web" and health.get("parallel_sdk") is not True:
        return False, "parallel-web transport requires parallel_sdk=True"
    if transport == "urllib-rest" and health.get("parallel_sdk") is not False:
        return False, "urllib-rest transport requires parallel_sdk=False"
    path = health.get("gemini_path") or ""
    if not str(path).startswith("vertex:"):
        return False, f"gemini_path must be vertex ADC, got {path!r}"
    return True, "partner fields present"


def manifest(*, gemini_path: str | None = None, adk_default: bool | None = None) -> dict:
    if gemini_path is None:
        gemini_path = resolve_gemini_path()
    if adk_default is None:
        adk_default = adk_default_enabled() and adk_agent.adk_available()
    root = Path(__file__).resolve().parents[1]
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
            "parallel_search_at_runtime": True,
            "parallel_web_sdk": parallel_search.sdk_available(),
            "gemini_at_runtime": gemini_path != "none",
            "adk_agent_builder": adk_agent.adk_available() and adk_default,
            "hosted_url_required": True,
        },
        "receipts": [
            "docs/PARTNER-INTEGRATIONS-2026-08-30.md",
            "docs/PARTNER-INTEGRATION-RESEARCH-2026-08-31.md",
            "docs/RECEIPT-adk-default-path-2026-08-30.md",
            "docs/RECEIPT-partner-admissibility-2026-09-16.md",
            "docs/FINDING-hosted-health-partner-strip-2026-09-16.md",
        ],
        "repo_root": str(root),
    }
