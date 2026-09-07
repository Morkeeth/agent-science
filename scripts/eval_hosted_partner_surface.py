#!/usr/bin/env python3
"""Baseline vs shipping: hosted partner dual surface.

Naive arm: anything with ok=true and service=agent-science passes.
Shipping arm: partner fields on /health + public /partners JSON + public /clear
reachable (not workspace-auth 401) + private /api/cases still 401.

Against live revision 00026 (pre-fix), naive wins and shipping fails —
that is the finding. Against a local hosted-mode server with the dual-surface
fix, shipping wins. Re-run after Oscar deploys this branch.

Usage:
  python3 scripts/eval_hosted_partner_surface.py
  python3 scripts/eval_hosted_partner_surface.py --no-local
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import secrets
import socket
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIVE = "https://agent-science-568004190078.us-central1.run.app"


def fetch(url: str, method: str = "GET", body: bytes | None = None) -> tuple[int, object]:
    class _NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: ANN001
            return None

    req = urllib.request.Request(url, data=body, method=method)
    if body is not None:
        req.add_header("Content-Type", "application/json")
    opener = urllib.request.build_opener(_NoRedirect)
    try:
        with opener.open(req, timeout=20) as resp:
            raw = resp.read()
            ctype = resp.headers.get("Content-Type", "")
            if "application/json" in ctype:
                return resp.status, json.loads(raw.decode())
            return resp.status, raw.decode(errors="replace")
    except urllib.error.HTTPError as e:
        raw = e.read() if hasattr(e, "read") else b""
        try:
            return e.code, json.loads(raw.decode())
        except Exception:
            return e.code, raw.decode(errors="replace") if raw else ""


def naive_score(health: dict) -> bool:
    return bool(health.get("ok") is True and health.get("service") == "agent-science")


def shipping_score(
    health: dict,
    partners_code: int,
    partners: object,
    clear_code: int,
    cases_code: int,
) -> bool:
    required = (
        "gemini",
        "gemini_path",
        "parallel",
        "parallel_sdk",
        "agent_builder",
        "engine_default",
    )
    if not all(k in health for k in required):
        return False
    if health.get("engine_default") not in ("adk", "direct"):
        return False
    # Dual surface names itself — bare private-workspaces liveness is RED.
    if health.get("mode") == "private-workspaces" and not health.get("public_desk"):
        return False
    if partners_code != 200 or not isinstance(partners, dict):
        return False
    if "track_checklist" not in partners or "partners" not in partners:
        return False
    # Public /clear is the partner Parallel path on dual surface.
    if clear_code == 401:
        return False
    # Private workspaces must stay private.
    if cases_code != 401:
        return False
    return True


def score_target(base: str) -> dict:
    h_code, health = fetch(f"{base.rstrip('/')}/health")
    p_code, partners = fetch(f"{base.rstrip('/')}/partners")
    c_code, _ = fetch(
        f"{base.rstrip('/')}/clear",
        method="POST",
        body=b'{"script":"x","subject":"y"}',
    )
    cases_code, _ = fetch(f"{base.rstrip('/')}/api/cases")
    if h_code != 200 or not isinstance(health, dict):
        health = {}
    naive = naive_score(health) if h_code == 200 else False
    shipping = (
        shipping_score(health, p_code, partners, c_code, cases_code)
        if h_code == 200
        else False
    )
    return {
        "base": base,
        "health_http": h_code,
        "partners_http": p_code,
        "clear_http": c_code,
        "cases_http": cases_code,
        "health": health if isinstance(health, dict) else {},
        "naive_pass": naive,
        "shipping_pass": shipping,
    }


def start_local() -> tuple[str, subprocess.Popen, tempfile.TemporaryDirectory]:
    tmp = tempfile.TemporaryDirectory()
    token = secrets.token_hex(24)
    access = json.dumps(
        {
            "session_key": "s" * 48,
            "users": {"judge": hashlib.sha256(token.encode()).hexdigest()},
        }
    )
    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.close()
    base = f"http://127.0.0.1:{port}"
    env = os.environ.copy()
    env.update(
        {
            "AGENT_SCIENCE_HOSTED": "1",
            "AGENT_SCIENCE_ALLOW_HTTP": "1",
            "AGENT_SCIENCE_PUBLIC_ORIGIN": base,
            "AGENT_SCIENCE_WORKSPACE_DIR": tmp.name,
            "AGENT_SCIENCE_ACCESS_CONFIG": access,
            "GCP_PROJECT": "hack-fleet",
            "AGENT_BUILDER": "1",
            "PORT": str(port),
            "PYTHONPATH": str(ROOT),
        }
    )
    # Never assign PARALLEL_API_KEY in this script — secret_surfaces scans .sh/.py surfaces.
    proc = subprocess.Popen(
        [sys.executable, "cloud/service.py"],
        cwd=str(ROOT),
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    for _ in range(50):
        try:
            code, _ = fetch(f"{base}/health")
            if code == 200:
                return base, proc, tmp
        except Exception:
            pass
        time.sleep(0.1)
    proc.kill()
    tmp.cleanup()
    raise RuntimeError("local hosted server failed to start")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-local", action="store_true", help="skip local fix arm")
    ap.add_argument("--live-url", default=LIVE)
    args = ap.parse_args()

    rows = []
    live = score_target(args.live_url)
    rows.append(("live", live))

    local_row = None
    if not args.no_local:
        base, proc, tmp = start_local()
        try:
            local_row = score_target(base)
            rows.append(("local-fix", local_row))
        finally:
            proc.kill()
            proc.wait(timeout=5)
            tmp.cleanup()

    print("HOSTED PARTNER SURFACE EVAL")
    print("naive arm: ok+service only")
    print("shipping arm: partner fields + public /partners + /clear≠401 + /api/cases=401")
    print()
    for name, row in rows:
        print(f"[{name}] {row['base']}")
        print(
            f"  health={row['health_http']} partners={row['partners_http']} "
            f"clear={row['clear_http']} cases={row['cases_http']}"
        )
        print(f"  health.keys={sorted((row['health'] or {}).keys())}")
        print(f"  naive_pass={row['naive_pass']}  shipping_pass={row['shipping_pass']}")
        print()

    live_naive, live_ship = live["naive_pass"], live["shipping_pass"]
    loc_ship = local_row["shipping_pass"] if local_row else None

    if live_naive and not live_ship:
        print(
            "FINDING: live hosted loses to naive liveness — partner dual surface absent "
            f"(revision={live['health'].get('revision')}). Oscar must deploy this branch."
        )
    elif live_ship:
        print("FINDING: live hosted passes shipping partner dual surface.")
    else:
        print("FINDING: live hosted failed both arms (unreachable or broken).")

    if loc_ship is False:
        print("FAIL: local fix server did not pass shipping arm")
        return 1
    if loc_ship is True:
        print("LOCAL FIX: shipping arm passes on private-workspaces+public-desk.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
