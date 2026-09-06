#!/usr/bin/env python3
"""Probe the advertised hosted stranger / judge path at the live URL.

A nearer proxy (reading STATUS.md) said the desk was public. This script opens
the object. Login-wall or missing partner fields → RED.

Self-test (--self-test) watches the control go RED on a planted login redirect
before accepting a planted 200 JSON — so an empty/outage read cannot look green.

Run:
  python3 scripts/probe_hosted_stranger_path.py
  python3 scripts/probe_hosted_stranger_path.py --self-test
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Callable

DEFAULT_URL = "https://agent-science-568004190078.us-central1.run.app"

# Paths the pitch / SUBMISSION-PACK / new_user_trial tell a stranger to hit.
STRANGER_PATHS = (
    "/search?q=2012/28/EU&live=false",
    "/stats",
    "/partners",
    "/registry",
    "/popular/ui",
    "/truths/ui",
    "/visibility/ui?q=ralph+loop+agentic",
)


@dataclass
class FetchResult:
    url: str
    status: int
    location: str | None
    body: bytes
    final_url: str | None = None


Fetcher = Callable[[str], FetchResult]


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    """Do not follow redirects — stranger path truth is the first response."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: ANN001
        return None


def _http_fetch(url: str, *, timeout: float = 20.0) -> FetchResult:
    req = urllib.request.Request(
        url, method="GET", headers={"User-Agent": "agent-science-stranger-probe/1.0"}
    )
    opener = urllib.request.build_opener(_NoRedirect)
    try:
        with opener.open(req, timeout=timeout) as resp:
            return FetchResult(
                url=url,
                status=int(resp.status),
                location=resp.headers.get("Location"),
                body=resp.read(65536),
                final_url=resp.geturl(),
            )
    except urllib.error.HTTPError as exc:
        loc = exc.headers.get("Location") if exc.headers else None
        body = exc.read(65536) if hasattr(exc, "read") else b""
        return FetchResult(url=url, status=int(exc.code), location=loc, body=body)


def _looks_like_login(fr: FetchResult) -> bool:
    loc = (fr.location or "").lower()
    if "/login" in loc:
        return True
    if fr.status in (301, 302, 303, 307, 308) and loc and "run.app" in loc:
        # Cross-host bounce — follow one hop mentally: still a stranger failure
        # if the stranger path did not return the resource itself.
        return True
    text = fr.body[:2000].decode("utf-8", errors="ignore").lower()
    if "sign in" in text and "agent science" in text:
        return True
    return False


def _health_ok_for_public_desk(health: dict) -> tuple[bool, str]:
    if not health.get("ok"):
        return False, "health.ok is not true"
    mode = health.get("mode")
    if mode == "private-workspaces":
        return False, "mode=private-workspaces (legacy public /search /clear not exposed)"
    # Legacy public desk advertised engine_default + partners on /health.
    if "engine_default" not in health:
        return False, "health missing engine_default (not the public desk shape)"
    return True, "health looks like public desk"


def evaluate(base: str, fetch: Fetcher) -> dict:
    base = base.rstrip("/")
    health_fr = fetch(f"{base}/health")
    report: dict = {
        "base": base,
        "health_status": health_fr.status,
        "paths": [],
        "verdict": "RED",
        "causes": [],
    }
    if health_fr.status != 200:
        report["causes"].append(f"/health HTTP {health_fr.status}")
        return report
    try:
        health = json.loads(health_fr.body.decode("utf-8"))
    except json.JSONDecodeError:
        report["causes"].append("/health not JSON")
        return report
    report["health"] = {
        "ok": health.get("ok"),
        "mode": health.get("mode"),
        "revision": health.get("revision"),
        "engine_default": health.get("engine_default"),
    }
    ok, reason = _health_ok_for_public_desk(health)
    if not ok:
        report["causes"].append(reason)

    for path in STRANGER_PATHS:
        fr = fetch(f"{base}{path}")
        row = {
            "path": path,
            "status": fr.status,
            "location": fr.location,
            "login_wall": _looks_like_login(fr),
            "json_ok": False,
        }
        if fr.status == 200 and not row["login_wall"]:
            if path.startswith("/search") or path == "/stats" or path == "/partners":
                try:
                    json.loads(fr.body.decode("utf-8"))
                    row["json_ok"] = True
                except json.JSONDecodeError:
                    report["causes"].append(f"{path} HTTP 200 but not JSON")
            else:
                # UI pages: HTML 200 without login is enough for stranger browse.
                row["json_ok"] = True
        if row["login_wall"] or fr.status in (401, 403) or (
            fr.status in (301, 302, 303, 307, 308)
        ):
            report["causes"].append(
                f"{path} → HTTP {fr.status} location={fr.location!r} login_wall={row['login_wall']}"
            )
        elif fr.status != 200:
            report["causes"].append(f"{path} → HTTP {fr.status}")
        elif path.startswith("/search") and not row["json_ok"]:
            pass  # already recorded
        report["paths"].append(row)

    search_ok = any(
        p["path"].startswith("/search") and p["status"] == 200 and p["json_ok"] and not p["login_wall"]
        for p in report["paths"]
    )
    if not search_ok:
        report["causes"].append("no unauthenticated /search JSON for stranger")

    if not report["causes"]:
        report["verdict"] = "GREEN"
    # de-dupe causes while preserving order
    seen = set()
    uniq = []
    for c in report["causes"]:
        if c not in seen:
            seen.add(c)
            uniq.append(c)
    report["causes"] = uniq
    return report


def _self_test() -> int:
    """Watch RED on planted login-wall, then GREEN on planted public desk."""

    def login_wall(url: str) -> FetchResult:
        if url.endswith("/health"):
            body = json.dumps(
                {"ok": True, "service": "agent-science", "mode": "private-workspaces", "revision": "test"}
            ).encode()
            return FetchResult(url, 200, None, body)
        return FetchResult(url, 303, "/login", b"")

    red = evaluate("https://example.test", login_wall)
    if red["verdict"] != "RED":
        print("SELF-TEST FAIL: planted private-workspaces+login did not go RED")
        print(json.dumps(red, indent=2))
        return 1
    print("SELF-TEST RED ok — private-workspaces + /login redirect caught")

    def public_desk(url: str) -> FetchResult:
        if url.endswith("/health"):
            body = json.dumps(
                {
                    "ok": True,
                    "engine_default": "adk",
                    "parallel": True,
                    "gemini": "vertex",
                    "revision": "test-public",
                }
            ).encode()
            return FetchResult(url, 200, None, body)
        if "/search" in url:
            return FetchResult(url, 200, None, json.dumps({"label": "SOURCED"}).encode())
        if url.endswith("/stats"):
            return FetchResult(url, 200, None, json.dumps({"n": 1}).encode())
        if url.endswith("/partners"):
            return FetchResult(url, 200, None, json.dumps({"partners": []}).encode())
        return FetchResult(url, 200, None, b"<html>desk</html>")

    green = evaluate("https://example.test", public_desk)
    if green["verdict"] != "GREEN":
        print("SELF-TEST FAIL: planted public desk did not go GREEN")
        print(json.dumps(green, indent=2))
        return 1
    print("SELF-TEST GREEN ok — public desk shape accepted")

    # Empty / outage must not look green (the false-green this control exists to catch).
    def empty_outage(url: str) -> FetchResult:
        return FetchResult(url, 502, None, b"")

    out = evaluate("https://example.test", empty_outage)
    if out["verdict"] != "RED":
        print("SELF-TEST FAIL: outage read looked GREEN")
        return 1
    print("SELF-TEST RED ok — outage/empty cannot pass")
    print("SELF-TEST PASS")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default=DEFAULT_URL)
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return _self_test()

    report = evaluate(args.url, _http_fetch)
    print(json.dumps(report, indent=2))
    print()
    if report["verdict"] == "GREEN":
        print(f"HOSTED STRANGER PATH GREEN · {args.url}")
        return 0
    print(f"HOSTED STRANGER PATH RED · {args.url}")
    for c in report["causes"]:
        print(f"  - {c}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
