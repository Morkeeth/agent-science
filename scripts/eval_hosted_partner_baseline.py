#!/usr/bin/env python3
"""Hosted partner-proof baseline vs shipping — measure at the live URL.

Naive arm any competent team ships in two hours:
  · /health → ok:true
  · /partners → any HTTP < 500 (login HTML counts as "up")
  · /truths/ui → any HTTP < 500

Shipping arm — what admissibility and film actually need:
  · /health partner fields (gemini, parallel, parallel_sdk, agent_builder, engine_default=adk)
  · /partners JSON track_checklist (not login HTML / 303)
  · /truths/ui 200 with dashboard markup

A result where naive beats shipping is the finding — live looks alive while
partner admissibility and judge surfaces are stripped. Do not paper over by
skipping the live URL; record the RED.

Usage:
  python3 scripts/eval_hosted_partner_baseline.py
  python3 scripts/eval_hosted_partner_baseline.py https://…
  python3 scripts/eval_hosted_partner_baseline.py --offline-fixtures
"""
from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone

DEFAULT_URL = "https://agent-science-568004190078.us-central1.run.app"


def _get(url: str, *, follow: bool = False) -> tuple[int, dict | None, str]:
    """Fetch URL. Default: do NOT follow redirects (303 to login is a signal)."""
    req = urllib.request.Request(url, headers={"Accept": "application/json, text/html;q=0.9"})
    opener = urllib.request.build_opener()
    if not follow:
        class _NoRedirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: N803
                return None

        opener = urllib.request.build_opener(_NoRedirect)
    try:
        with opener.open(req, timeout=20) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            try:
                return resp.status, json.loads(raw), raw
            except json.JSONDecodeError:
                return resp.status, None, raw
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="replace")
        # 303/302 with empty body still carries Location
        try:
            return e.code, json.loads(raw), raw
        except json.JSONDecodeError:
            return e.code, None, raw
    except Exception as e:
        return 0, None, str(e)


def naive_health(health: dict | None) -> bool:
    return bool(health and health.get("ok") is True)


def shipping_health(health: dict | None) -> tuple[bool, str]:
    """Same asserts as verify_partners_hosted.sh step 1."""
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


def naive_up(code: int) -> bool:
    """Two-hour baseline: anything short of server death counts as up."""
    return 100 <= code < 500


def shipping_partners(code: int, body: dict | None, raw: str) -> tuple[bool, str]:
    if code != 200 or not isinstance(body, dict):
        hint = "login HTML" if "Sign in" in (raw or "")[:200] else f"HTTP {code}"
        return False, f"expected JSON manifest, got {hint}"
    tc = body.get("track_checklist") or {}
    for key in (
        "parallel_search_at_runtime",
        "gemini_at_runtime",
        "adk_agent_builder",
        "hosted_url_required",
    ):
        if tc.get(key) is not True:
            return False, f"track_checklist.{key}={tc.get(key)!r}"
    return True, "track_checklist JSON"


def shipping_film(code: int, raw: str) -> tuple[bool, str]:
    if code != 200:
        return False, f"HTTP {code} (want 200 public dashboard)"
    if "truth" not in raw.lower() and "dashboard" not in raw.lower():
        return False, "200 but missing dashboard markers"
    return True, "public truths dashboard"


def main() -> int:
    if len(sys.argv) > 1 and sys.argv[1] in ("--offline-fixtures", "--fixtures"):
        return _offline_fixtures()
    base = (sys.argv[1] if len(sys.argv) > 1 else DEFAULT_URL).rstrip("/")
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    print(f"HOSTED PARTNER BASELINE EVAL · stamp={stamp}")
    print(f"URL: {base}\n")

    h_code, health, h_raw = _get(f"{base}/health")
    print(f"--- /health HTTP {h_code} ---")
    if health is not None:
        print(json.dumps(health, indent=2, sort_keys=True))
    else:
        print(h_raw[:400])

    p_code, partners, p_raw = _get(f"{base}/partners")
    print(f"\n--- /partners HTTP {p_code} ---")
    if partners is not None:
        print(json.dumps({"keys": sorted(partners), "track_checklist": partners.get("track_checklist")}, indent=2))
    else:
        print((p_raw or "")[:180].replace("\n", " "))

    f_code, _, f_raw = _get(f"{base}/truths/ui")
    print(f"\n--- /truths/ui HTTP {f_code} ---")
    print((f_raw or "")[:120].replace("\n", " "))

    return _score_and_report(
        health=health,
        p_code=p_code,
        partners=partners,
        p_raw=p_raw or "",
        f_code=f_code,
        f_raw=f_raw or "",
    )


def _score_and_report(
    *,
    health: dict | None,
    p_code: int,
    partners: dict | None,
    p_raw: str,
    f_code: int,
    f_raw: str,
) -> int:
    rows: list[tuple[str, str, bool, str]] = []
    n_h = naive_health(health)
    s_h, s_h_why = shipping_health(health)
    rows.append(("H1", "naive health ok:true", n_h, "liveness only"))
    rows.append(("H2", "shipping health partners", s_h, s_h_why))

    n_p = naive_up(p_code)
    s_p, s_p_why = shipping_partners(p_code, partners, p_raw)
    rows.append(("H3", "naive partners HTTP<500", n_p, f"HTTP {p_code}"))
    rows.append(("H4", "shipping partners JSON", s_p, s_p_why))

    n_f = naive_up(f_code)
    s_f, s_f_why = shipping_film(f_code, f_raw)
    rows.append(("H5", "naive truths/ui HTTP<500", n_f, f"HTTP {f_code}"))
    rows.append(("H6", "shipping truths/ui public", s_f, s_f_why))

    print("\nid     arm                          result   note")
    for rid, name, ok, note in rows:
        print(f"{rid:<6} {name:<28} {'PASS' if ok else 'FAIL':<8} {note}")

    naive_pass = sum(1 for r in rows if r[0] in ("H1", "H3", "H5") and r[2])
    ship_pass = sum(1 for r in rows if r[0] in ("H2", "H4", "H6") and r[2])
    print(f"\nNaive:    {naive_pass}/3")
    print(f"Shipping: {ship_pass}/3")

    if naive_pass > ship_pass:
        print(
            "FINDING: naive beats shipping on live — desk looks up while "
            "partner proof and/or judge surfaces fail. Oscar deploy.sh required; "
            "do not claim hosted partners green."
        )
        return 2
    if naive_pass == 3 and ship_pass == 3:
        print("FINDING: shipping matches naive — partner fields + public film on live.")
        return 0
    print("FINDING: mixed or unreachable — inspect rows above.")
    return 1


def _offline_fixtures() -> int:
    """No network. Prove scoring: stripped desk → naive wins; full desk → tie."""
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    print(f"HOSTED PARTNER BASELINE EVAL · offline fixtures · stamp={stamp}\n")

    stripped = {"ok": True, "service": "agent-science", "mode": "private-workspaces", "revision": "fixture-stripped"}
    print("=== fixture A: stripped health + 303 partners/film (00028-hed shape) ===")
    rc_a = _score_and_report(
        health=stripped,
        p_code=303,
        partners=None,
        p_raw="",
        f_code=303,
        f_raw="",
    )
    if rc_a != 2:
        print(f"FAIL: expected exit 2 when naive beats shipping, got {rc_a}")
        return 1

    full = {
        "ok": True,
        "gemini": True,
        "parallel": True,
        "parallel_sdk": True,
        "agent_builder": True,
        "engine_default": "adk",
        "gemini_path": "vertex:hack-fleet",
    }
    partners = {
        "track_checklist": {
            "parallel_search_at_runtime": True,
            "gemini_at_runtime": True,
            "adk_agent_builder": True,
            "hosted_url_required": True,
        }
    }
    print("\n=== fixture B: full partner health + public film ===")
    rc_b = _score_and_report(
        health=full,
        p_code=200,
        partners=partners,
        p_raw="",
        f_code=200,
        f_raw="<html>truths dashboard</html>",
    )
    if rc_b != 0:
        print(f"FAIL: expected exit 0 when shipping matches naive, got {rc_b}")
        return 1

    print("\nOFFLINE FIXTURES OK — stripped → naive wins; full → shipping matches.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
