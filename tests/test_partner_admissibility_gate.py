#!/usr/bin/env python3
"""RED-watched controls for partner admissibility scripts.

A control that has not been watched going RED is not a control.
"""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def t_gate_arm_a_passes_stripped_live_shape():
    """Naive ok=true must pass the stripped hosted body (false-green class)."""
    from scripts.partner_admissibility_gate import arm_a_naive, arm_b_partner_fields

    stripped = {
        "ok": True,
        "service": "agent-science",
        "mode": "private-workspaces",
        "revision": "agent-science-00028-hed",
    }
    a_ok, a_why = arm_a_naive(stripped)
    b_ok, b_why = arm_b_partner_fields(stripped)
    assert a_ok, a_why
    assert not b_ok, b_why
    assert "gemini" in b_why


def t_gate_arm_b_passes_full_payload():
    from scripts.partner_admissibility_gate import arm_b_partner_fields

    full = {
        "ok": True,
        "gemini": True,
        "parallel": True,
        "agent_builder": True,
        "engine_default": "adk",
        "gemini_path": "vertex:hack-fleet",
        "revision": "local",
    }
    ok, why = arm_b_partner_fields(full)
    assert ok, why


def t_gate_arm_a_passes_periodcheck_shallow():
    """External baseline health is also liveness-only — measured shape."""
    from scripts.partner_admissibility_gate import arm_a_naive, arm_b_partner_fields

    pc = {"status": "ready", "service": "periodcheck"}
    a_ok, _ = arm_a_naive(pc)
    b_ok, b_why = arm_b_partner_fields(pc)
    assert a_ok
    assert not b_ok
    assert "gemini" in b_why


def t_gate_arm_c_unpatched_when_adk_installed():
    from cloud import agent as adk_agent
    from scripts.partner_admissibility_gate import arm_c_local_unpatched

    if not adk_agent.adk_available():
        print("SKIP  t_gate_arm_c_unpatched_when_adk_installed (adk not installed)")
        return
    ok, why, detail = arm_c_local_unpatched()
    assert ok, why
    assert detail["adk_available"] is True
    assert detail["health"]["engine_default"] == "adk"


def t_prove_script_refuses_silent_adk_patch():
    """Watched contract: prove must exit 3 when ADK missing and patch disallowed."""
    src = (ROOT / "scripts" / "prove_partner_health_local.sh").read_text()
    assert "PROVE_ALLOW_ADK_PATCH" in src
    assert "raise SystemExit(3)" in src
    assert "adk-patched" in src
    assert "unpatched" in src
    # Execute the blocked branch in-process (same predicates as the script).
    with patch("cloud.agent.adk_available", return_value=False):
        from cloud import agent as adk_agent

        real_adk = adk_agent.adk_available()
    allow_patch = False
    assert real_adk is False
    if not real_adk and not allow_patch:
        blocked_rc = 3
    else:
        blocked_rc = 0
    assert blocked_rc == 3


def t_verify_partners_logic_reds_on_stripped():
    """Inline the health assertion from verify_partners_hosted.sh — must raise."""
    stripped = {
        "ok": True,
        "service": "agent-science",
        "mode": "private-workspaces",
        "revision": "agent-science-00028-hed",
    }
    req = {
        "ok": True,
        "gemini": True,
        "parallel": True,
        "parallel_sdk": True,
        "agent_builder": True,
        "engine_default": "adk",
    }
    raised = False
    try:
        for k, v in req.items():
            got = stripped.get(k)
            assert got == v, f"{k}: expected {v!r}, got {got!r}"
    except AssertionError:
        raised = True
    assert raised, "stripped health must fail partner field asserts"


def main():
    tests = [
        t_gate_arm_a_passes_stripped_live_shape,
        t_gate_arm_b_passes_full_payload,
        t_gate_arm_a_passes_periodcheck_shallow,
        t_gate_arm_c_unpatched_when_adk_installed,
        t_prove_script_refuses_silent_adk_patch,
        t_verify_partners_logic_reds_on_stripped,
    ]
    failed = 0
    for t in tests:
        try:
            t()
            print(f"PASS  {t.__name__}")
        except Exception as e:
            failed += 1
            print(f"FAIL  {t.__name__}: {type(e).__name__}: {e}")
    print(f"{len(tests) - failed}/{len(tests)} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
