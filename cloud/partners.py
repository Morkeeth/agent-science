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


def gemini_env_configured() -> bool:
    """True when deploy/local env intends Gemini — not proof it can be called."""
    if os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY"):
        return True
    if os.environ.get("GCP_PROJECT") or os.environ.get("GOOGLE_CLOUD_PROJECT"):
        return True
    if os.environ.get("K_SERVICE"):
        return True
    return False


def resolve_gemini_path() -> str:
    """Report how Gemini is reached — never the secret itself.

    GCP_PROJECT / K_SERVICE alone must NOT claim ``vertex:…``. That presence-only
    path made ``gemini: true`` on local prove while ``vertex_token()`` was absent
    (measured 2026-09-20). Callable proof requires an API key or a working ADC token.
    """
    if os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY"):
        return "api-key"
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

    ``gemini`` / ``gemini_path`` are callable (token or API key). ``gemini_configured``
    is env intent. Parallel key presence is ``parallel``; durable call proof is the
    receipt-backed ``verified_search_id`` fields (PeriodCheck-style lineage).
    """
    gemini_path = resolve_gemini_path()
    adk_ok = adk_agent.adk_available()
    adk_default = adk_default_enabled() and adk_ok
    receipt = parallel_search.last_verified_receipt()
    out = {
        "ok": True,
        "service": "agent-science",
        "gemini": gemini_path != "none",
        "gemini_path": gemini_path,
        "gemini_configured": gemini_env_configured(),
        "parallel": bool(os.environ.get("PARALLEL_API_KEY")),
        "parallel_sdk": parallel_search.sdk_available(),
        "parallel_sdk_version": parallel_search.sdk_version(),
        "parallel_transport": parallel_search.integration_info()["transport"],
        "last_parallel_search_id": parallel_search.last_search_id(),
        "verified_search_id": receipt.get("verified_search_id"),
        "verified_calls_logged": receipt.get("verified_calls_logged"),
        "last_verified_utc": receipt.get("last_verified_utc"),
        "agent_builder": adk_ok,
        "adk_version": adk_agent.adk_version(),
        "engine_default": "adk" if adk_default else "direct",
    }
    if mode is not None:
        out["mode"] = mode
    if revision is not None:
        out["revision"] = revision
    return out


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
                "configured": gemini_env_configured(),
                "secret_manager": False,
                "notes": "Vertex ADC on Cloud Run; API key local dev only. runtime=callable token/key, not env alone",
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
            # Presence of wiring intent + key — not a live call count (cold start is 0).
            "parallel_search_at_runtime": bool(os.environ.get("PARALLEL_API_KEY")),
            "parallel_web_sdk": parallel_search.sdk_available(),
            "gemini_at_runtime": gemini_path != "none",
            "adk_agent_builder": adk_agent.adk_available() and adk_default,
            "hosted_url_required": True,
            "parallel_receipt_backed": bool(
                parallel_search.last_verified_receipt().get("verified_search_id")
            ),
        },
        "receipts": [
            "docs/PARTNER-INTEGRATIONS-2026-08-30.md",
            "docs/PARTNER-INTEGRATION-RESEARCH-2026-08-31.md",
            "docs/RECEIPT-adk-default-path-2026-08-30.md",
            "docs/RECEIPT-partner-admissibility-2026-09-16.md",
            "docs/RECEIPT-partner-callproof-2026-09-20.md",
            "docs/RECEIPT-partner-judge-surfaces-2026-09-18.md",
            "docs/RECEIPT-partner-callproof-night-2026-09-23.md",
            "docs/FINDING-hosted-health-partner-strip-2026-09-16.md",
            "docs/FINDING-gemini-health-env-alone-2026-09-20.md",
            "docs/FINDING-hosted-judge-surfaces-missing-2026-09-18.md",
            "docs/FINDING-partners-checklist-hardcoded-2026-09-18.md",
            "docs/BASELINE-periodcheck-partner-proof-2026-09-20.md",
        ],
        "repo_root": str(root),
    }
