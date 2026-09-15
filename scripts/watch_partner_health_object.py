#!/usr/bin/env python3
"""Watch partner admissibility at the hosted object — not at a proxy.

Naive private-workspace arm (revision agent-science-00028-hed):
  /health → {ok, service, mode, revision} only
  /partners → login HTML (auth wall)

Shipping arm (this tree, after Oscar deploy):
  /health → gemini · parallel · parallel_sdk · agent_builder · engine_default: adk
  /partners → JSON track_checklist with partner_health_public: true

Exit 2 = watched RED (current live defect).
Exit 0 = GREEN (partners provable on hosted URL).
Exit 1 = transport / parse failure.
"""
from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request

BASE = sys.argv[1] if len(sys.argv) > 1 else (
    "https://agent-science-568004190078.us-central1.run.app"
)
REQUIRED = ("gemini", "parallel", "parallel_sdk", "agent_builder", "engine_default")


def get(path: str) -> tuple[int, str]:
    req = urllib.request.Request(BASE + path, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")


def main() -> int:
    print(f"OBJECT  {BASE}")
    h_code, h_body = get("/health")
    p_code, p_body = get("/partners")
    print(f"/health  HTTP {h_code}")
    print(f"/partners HTTP {p_code}")

    try:
        health = json.loads(h_body)
    except json.JSONDecodeError:
        print("FAIL  /health is not JSON")
        return 1

    print("health keys:", sorted(health.keys()))
    missing = [k for k in REQUIRED if k not in health]
    partners_is_html = p_body.lstrip().lower().startswith("<!doctype")
    partners_ok = False
    if not partners_is_html and p_code == 200:
        try:
            partners = json.loads(p_body)
            tc = partners.get("track_checklist") or {}
            partners_ok = tc.get("partner_health_public") is True
            print("partners mode:", partners.get("mode"))
            print("track_checklist.partner_health_public:", tc.get("partner_health_public"))
        except json.JSONDecodeError:
            print("FAIL  /partners body is not JSON")
            return 1
    else:
        print("partners body starts as HTML login wall:", partners_is_html)

    thin = bool(missing) or not partners_ok
    if thin:
        print("WATCHED_RED  naive private-workspace arm still live")
        print("  missing health fields:", missing or "(none)")
        print("  partners public JSON:", partners_ok)
        print("  revision:", health.get("revision"))
        print("UNBLOCK  Oscar: bash deploy.sh then bash scripts/verify_partners_hosted.sh")
        return 2

    assert health.get("engine_default") == "adk", health
    assert health.get("ok") is True
    print("GREEN  partner fields + public /partners at hosted object")
    print("  revision:", health.get("revision"))
    print("  engine_default:", health.get("engine_default"))
    print("  gemini_path:", health.get("gemini_path"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
