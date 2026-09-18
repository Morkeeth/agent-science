#!/usr/bin/env python3
"""Hosted partner-proof baseline vs shipping — measure at the live URL.

Naive arm any competent team ships in two hours: `ok: true` means healthy.
Shipping arm: require the four-partner fields judges and verify_partners_hosted.sh
actually read (gemini, parallel, agent_builder, engine_default=adk).

A result where naive PASSes and shipping FAILs is the finding — live looks
alive while partner admissibility is stripped. Do not paper over by skipping
the live URL; record the RED.

Usage:
  python3 scripts/eval_hosted_partner_baseline.py
  python3 scripts/eval_hosted_partner_baseline.py https://…
"""
from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone

DEFAULT_URL = "https://agent-science-568004190078.us-central1.run.app"


def _get_json(url: str) -> tuple[int, dict | None, str]:
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            try:
                return resp.status, json.loads(raw), raw
            except json.JSONDecodeError:
                return resp.status, None, raw
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="replace")
        try:
            return e.code, json.loads(raw), raw
        except json.JSONDecodeError:
            return e.code, None, raw
    except Exception as e:
        return 0, None, str(e)


def naive_ok(health: dict | None) -> bool:
    """Two-hour baseline: liveness only."""
    return bool(health and health.get("ok") is True)


def shipping_partner_proof(health: dict | None) -> tuple[bool, str]:
    """Shipping control — same asserts as verify_partners_hosted.sh step 1."""
    if not isinstance(health, dict):
        return False, "body not JSON object"
    req = {
        "ok": True,
        "gemini": True,
        "parallel": True,
        "parallel_sdk": True,
        "agent_builder": True,
        "engine_default": "adk",
    }
    for k, v in req.items():
        got = health.get(k)
        if got != v:
            return False, f"{k}: expected {v!r}, got {got!r} (keys={sorted(health)})"
    path = health.get("gemini_path") or ""
    if not str(path).startswith("vertex:"):
        return False, f"gemini_path must be vertex ADC, got {path!r}"
    return True, "partner fields present"


def main() -> int:
    base = (sys.argv[1] if len(sys.argv) > 1 else DEFAULT_URL).rstrip("/")
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    print(f"HOSTED PARTNER BASELINE EVAL · stamp={stamp}")
    print(f"URL: {base}/health\n")

    code, health, raw = _get_json(f"{base}/health")
    print(f"HTTP {code}")
    if health is not None:
        print(json.dumps(health, indent=2, sort_keys=True))
    else:
        print(raw[:400])

    n_ok = naive_ok(health)
    s_ok, s_why = shipping_partner_proof(health)

    print("\nid     arm                          result   note")
    print(f"H1     naive ok:true               {'PASS' if n_ok else 'FAIL'}     liveness only")
    print(f"H2     shipping partner fields     {'PASS' if s_ok else 'FAIL'}     {s_why}")

    print("\nNaive:    ", "1/1" if n_ok else "0/1")
    print("Shipping: ", "1/1" if s_ok else "0/1")
    if n_ok and not s_ok:
        print(
            "FINDING: naive PASS + shipping FAIL — live looks healthy while "
            "partner admissibility is stripped. Deploy the in-tree health fix "
            "(Oscar deploy.sh); do not claim hosted partners green."
        )
        return 2
    if n_ok and s_ok:
        print("FINDING: shipping matches naive — partner fields present on live.")
        return 0
    print("FINDING: live health unreachable or not ok — check URL / outage.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
