#!/usr/bin/env python3
"""Agent Builder / ADK wrapper — clear_script as the only tool.

Tools work without ADK; build_agent() needs google-adk + GEMINI_MODEL.

`run_clearance()` is what makes this the DEFAULT path rather than dead code:
the hosted service calls it, the ADK runner decides to call the tool, and the
gap report is lifted out of the tool's own function_response — never out of the
model's prose, which would put a language model between you and your evidence.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import agent_science  # noqa: E402

INSTRUCTION = """You are Agent Science — a clearance desk for factual production.

When given a documentary script, call clear_script with the full text and an optional
subject tag (e.g. dust-bowl) for corpus compounding. Return the gap report: every claim
SOURCED with citation or UNSOURCED with the reason. Never infer unsourced claims as true.
"""

APP_NAME = "agent_science"
DEFAULT_MODEL = "gemini-3.5-flash-lite"


def clear_script_tool(script: str, subject: str = "default") -> dict:
    """Extract factual claims, source via Parallel, verify verbatim, return gap report."""
    model = os.environ.get("GEMINI_MODEL", DEFAULT_MODEL)
    return agent_science.clear_script(script, subject=subject, model=model)


TOOLS = [clear_script_tool]


def _use_vertex() -> bool:
    """Vertex when there is no API key and a project is reachable — the deployed shape."""
    if os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY"):
        return False
    return bool(_vertex_project())


def _vertex_project() -> str | None:
    for var in ("GOOGLE_CLOUD_PROJECT", "GCP_PROJECT"):
        if os.environ.get(var):
            return os.environ[var]
    try:
        from clearance import gemini as _g

        return _g.vertex_project()
    except Exception:
        return None


def _prepare_genai_env() -> str:
    """Point google-genai (ADK's model client) at the same identity the engine uses.

    Returns the routing label that /health and /clear report, so the receipt says
    which path actually ran instead of which path was configured.
    """
    if not _use_vertex():
        return "api-key"
    project = _vertex_project()
    os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "true")
    os.environ.setdefault("GOOGLE_CLOUD_PROJECT", project or "")
    # `global`, not a region. clearance/gemini.py already learned this the hard way:
    # only the global location publishes these models and every regional endpoint
    # 404s. Reusing GCP_REGION here reproduced that 404 through the ADK client.
    os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "global")
    return f"vertex:{project}"


def build_agent():
    model = os.environ.get("GEMINI_MODEL", DEFAULT_MODEL)
    if not model:
        raise RuntimeError("GEMINI_MODEL unset")
    try:
        from google.adk.agents import Agent
    except ImportError as e:
        raise RuntimeError("pip install google-adk for Agent Builder deploy") from e
    _prepare_genai_env()
    return Agent(
        name=APP_NAME,
        model=model,
        description="Clearance desk: script in, gap report out, corpus compounds.",
        instruction=INSTRUCTION,
        tools=TOOLS,
    )


def adk_available() -> bool:
    try:
        import google.adk  # noqa: F401

        return True
    except Exception:
        return False


def adk_version() -> str | None:
    try:
        from importlib.metadata import version

        return version("google-adk")
    except Exception:
        return None


def run_clearance(script: str, subject: str = "default") -> dict:
    """Run the clearance through the ADK agent and return the gap report.

    Raises RuntimeError if the agent never called the tool. A model that answers
    from its own head instead of calling clear_script has produced prose, not a
    clearance, and this desk refuses to serve prose as evidence.
    """
    import asyncio

    return asyncio.run(_run_clearance_async(script, subject))


async def _run_clearance_async(script: str, subject: str) -> dict:
    from google.adk.runners import InMemoryRunner
    from google.genai import types

    agent = build_agent()
    runner = InMemoryRunner(agent=agent, app_name=APP_NAME)
    session = await runner.session_service.create_session(
        app_name=APP_NAME, user_id="desk"
    )
    message = types.Content(
        role="user",
        parts=[
            types.Part(
                text=(
                    f"Clear this script. Use subject tag '{subject}'.\n\n"
                    f"---\n{script}\n---"
                )
            )
        ],
    )

    report: dict | None = None
    tool_calls: list[str] = []
    async for event in runner.run_async(
        user_id="desk", session_id=session.id, new_message=message
    ):
        for part in (getattr(event.content, "parts", None) or []) if event.content else []:
            call = getattr(part, "function_call", None)
            if call is not None and call.name:
                tool_calls.append(call.name)
            resp = getattr(part, "function_response", None)
            if resp is not None and resp.name == "clear_script_tool":
                payload = resp.response
                if isinstance(payload, dict):
                    report = payload.get("result", payload)

    if report is None:
        raise RuntimeError(
            "ADK agent returned without calling clear_script_tool "
            f"(tool calls seen: {tool_calls or 'none'})"
        )

    report = dict(report)
    report["engine"] = "adk"
    report["adk_version"] = adk_version()
    report["model_routing"] = _prepare_genai_env()
    report["adk_tool_calls"] = tool_calls
    return report
