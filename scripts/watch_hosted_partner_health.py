#!/usr/bin/env python3
"""Watch hosted /health for partner admissibility — with a naive baseline arm.

THE CONTROL: a check that only asserts ok=true reads GREEN on a stripped
private-workspaces liveness payload. That is how partner fields stayed
"green" in docs for days after the pivot. This script prints both arms.

Exit codes:
  0  partner fields present (GREEN) — post-deploy expectation
  1  partner fields missing (RED) — current live until Oscar promotes fix
  2  transport / parse failure

Done-when:
  python3 scripts/watch_hosted_partner_health.py
  # Expect RED on live until deploy; GREEN after Oscar promotes.
"""
from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request

DEFAULT_URL = "https://agent-science-568004190078.us-central1.run.app/health"
PARTNER_FIELDS = (
    "gemini",
    "parallel",
    "parallel_sdk",
    "agent_builder",
    "engine_default",
    "gemini_path",
)


def naive_ok_only(payload: dict) -> bool:
    """Two-hour baseline any competent team ships — and it lies after the pivot."""
    return payload.get("ok") is True and payload.get("service") == "agent-science"


def partner_admissible(payload: dict) -> tuple[bool, list[str]]:
    missing = [k for k in PARTNER_FIELDS if k not in payload]
    if missing:
        return False, missing
    if payload.get("engine_default") not in ("adk", "direct"):
        return False, ["engine_default:invalid"]
    return True, []


def main(argv: list[str]) -> int:
    url = argv[1] if len(argv) > 1 else DEFAULT_URL
    print(f"url: {url}")
    try:
        with urllib.request.urlopen(url, timeout=30) as resp:
            raw = resp.read().decode()
            code = resp.status
    except urllib.error.HTTPError as exc:
        print(f"transport HTTP {exc.code}", file=sys.stderr)
        return 2
    except Exception as exc:  # noqa: BLE001 — surface any transport failure
        print(f"transport error: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2

    payload = json.loads(raw)
    print("payload:", json.dumps(payload, sort_keys=True))
    print(f"http: {code}")

    naive = naive_ok_only(payload)
    ok, missing = partner_admissible(payload)
    print(f"baseline_arm (ok-only): {'GREEN' if naive else 'RED'}")
    print(f"partner_arm  (fields):  {'GREEN' if ok else 'RED'}", end="")
    if missing:
        print(f"  missing={missing}")
    else:
        print()
    print(f"revision: {payload.get('revision')}")
    print(f"mode: {payload.get('mode')}")

    if naive and not ok:
        print(
            "FINDING: naive ok-only arm is GREEN while partner arm is RED — "
            "stripped liveness masquerading as healthy partner wiring."
        )

    if ok:
        # Stronger post-deploy expectations (informational if soft-fail fields wrong)
        soft = []
        if payload.get("engine_default") != "adk":
            soft.append(f"engine_default={payload.get('engine_default')!r} want adk")
        if payload.get("gemini") is not True:
            soft.append("gemini not true")
        if payload.get("parallel") is not True:
            soft.append("parallel not true")
        if soft:
            print("SOFT: partner fields present but wiring incomplete:", "; ".join(soft))
            return 1
        print("HOSTED PARTNER HEALTH GREEN")
        return 0

    print("HOSTED PARTNER HEALTH RED — Oscar must deploy partner-admissibility revision")
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
