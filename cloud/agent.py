#!/usr/bin/env python3
"""Agent Builder / ADK wrapper — clear_script as the only tool.

Tools work without ADK; build_agent() needs google-adk + GEMINI_MODEL.
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


def clear_script_tool(script: str, subject: str = "default") -> dict:
    """Extract factual claims, source via Parallel, verify verbatim, return gap report."""
    model = os.environ.get("GEMINI_MODEL", "gemini-3.5-flash-lite")
    return agent_science.clear_script(script, subject=subject, model=model)


TOOLS = [clear_script_tool]


def build_agent():
    model = os.environ.get("GEMINI_MODEL")
    if not model:
        raise RuntimeError("GEMINI_MODEL unset")
    try:
        from google.adk.agents import Agent
    except ImportError as e:
        raise RuntimeError("pip install google-adk for Agent Builder deploy") from e
    return Agent(
        name="agent_science",
        model=model,
        description="Clearance desk: script in, gap report out, corpus compounds.",
        instruction=INSTRUCTION,
        tools=TOOLS,
    )
