#!/usr/bin/env python3
"""Partner admissibility gate — three arms, measured at objects.

Arms (riskiest first):
  A  naive liveness — ok/status only. The control any team ships in two hours.
  B  partner fields — gemini / parallel / engine_default / agent_builder.
  C  local unpatched import — real google-adk + parallel-web, no unittest.mock.

A result where A passes and B fails on our hosted URL is a FINDING, not a pass.
Comparing B against PeriodCheck's hosted /api/health is the external baseline:
their health is also liveness-only (measured at object, not from their README).

Usage:
  python3 scripts/partner_admissibility_gate.py
  python3 scripts/partner_admissibility_gate.py --ours URL --baseline URL
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OURS = "https://agent-science-568004190078.us-central1.run.app"
DEFAULT_BASELINE = "https://periodcheck-697827662390.us-central1.run.app"


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    """Do not follow 303 — hosted /partners redirecting to login is the defect."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: ANN001
        return None


def _get_json(url: str, timeout: float = 30.0) -> tuple[int, dict | list | None, str]:
    """Fetch JSON without following redirects (partner proof must be on this URL)."""
    req = urllib.request.Request(url, headers={"Accept": "application/json, text/html"})
    opener = urllib.request.build_opener(_NoRedirect)
    try:
        with opener.open(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            code = getattr(resp, "status", 200) or 200
            loc = resp.headers.get("Location")
            if loc:
                raw = f"redirect:{loc}"
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="replace")
        code = e.code
        loc = e.headers.get("Location") if e.headers else None
        if not raw and loc:
            raw = f"redirect:{loc}"
    except Exception as e:
        return 0, None, f"{type(e).__name__}: {e}"
    try:
        return code, json.loads(raw), raw[:500]
    except json.JSONDecodeError:
        return code, None, raw[:500]


def arm_a_naive(body: dict | None) -> tuple[bool, str]:
    """Two-hour baseline: any ready/ok signal counts."""
    if not isinstance(body, dict):
        return False, "body not JSON object"
    if body.get("ok") is True:
        return True, "ok=true"
    if str(body.get("status", "")).lower() in ("ready", "ok", "healthy", "up"):
        return True, f"status={body.get('status')!r}"
    return False, f"no naive liveness key in {sorted(body)}"


def arm_b_partner_fields(body: dict | None) -> tuple[bool, str]:
    """Admissibility: partner wiring visible without a workspace key."""
    if not isinstance(body, dict):
        return False, "body not JSON object"
    required = {
        "gemini": True,
        "parallel": True,
        "agent_builder": True,
        "engine_default": "adk",
    }
    missing = []
    for key, want in required.items():
        got = body.get(key)
        if got != want:
            missing.append(f"{key}: expected {want!r}, got {got!r}")
    if missing:
        return False, "; ".join(missing) + f" (keys={sorted(body)})"
    path = body.get("gemini_path") or ""
    if not str(path).startswith("vertex:"):
        return False, f"gemini_path must be vertex ADC, got {path!r}"
    return True, f"engine_default=adk revision={body.get('revision')}"


def arm_c_local_unpatched() -> tuple[bool, str, dict]:
    """Real imports — no mock. Requires pip install -r requirements.txt."""
    sys.path.insert(0, str(ROOT))
    # Clear any prior forced env for a clean read of importability.
    from cloud import agent as adk_agent
    from clearance import search as parallel_search
    from cloud.partners import health_payload

    adk_ok = adk_agent.adk_available()
    sdk_ok = parallel_search.sdk_available()
    # Stamp env only for health_payload shape — does not mock imports.
    os.environ.setdefault("AGENT_BUILDER", "1")
    os.environ.setdefault("GCP_PROJECT", "hack-fleet")
    if not os.environ.get("PARALLEL_API_KEY"):
        os.environ["PARALLEL_API_KEY"] = "pk-gate-local-not-live"
    payload = health_payload(mode="local-unpatched", revision="partner-admissibility-gate")
    detail = {
        "adk_available": adk_ok,
        "adk_version": adk_agent.adk_version(),
        "parallel_sdk": sdk_ok,
        "parallel_sdk_version": parallel_search.sdk_version(),
        "health": payload,
    }
    if not adk_ok:
        return False, "google-adk not importable (pip install google-adk==2.7.1)", detail
    if payload.get("engine_default") != "adk":
        return False, f"engine_default={payload.get('engine_default')!r} with ADK importable", detail
    if not payload.get("agent_builder"):
        return False, "agent_builder false despite import", detail
    return True, f"adk {detail['adk_version']} · sdk {detail['parallel_sdk_version']}", detail


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--ours", default=os.environ.get("AGENT_SCIENCE_URL", DEFAULT_OURS))
    ap.add_argument("--baseline", default=DEFAULT_BASELINE)
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args()
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    ours_health_url = args.ours.rstrip("/") + "/health"
    ours_partners_url = args.ours.rstrip("/") + "/partners"
    baseline_health_url = args.baseline.rstrip("/") + "/api/health"

    ours_code, ours_body, ours_raw = _get_json(ours_health_url)
    partners_code, partners_body, partners_raw = _get_json(ours_partners_url)
    base_code, base_body, base_raw = _get_json(baseline_health_url)

    a_ours, a_ours_why = arm_a_naive(ours_body if isinstance(ours_body, dict) else None)
    b_ours, b_ours_why = arm_b_partner_fields(ours_body if isinstance(ours_body, dict) else None)
    a_base, a_base_why = arm_a_naive(base_body if isinstance(base_body, dict) else None)
    b_base, b_base_why = arm_b_partner_fields(base_body if isinstance(base_body, dict) else None)
    c_ok, c_why, c_detail = arm_c_local_unpatched()

    partners_ok = (
        partners_code == 200
        and isinstance(partners_body, dict)
        and isinstance(partners_body.get("track_checklist"), dict)
        and partners_body["track_checklist"].get("adk_agent_builder") is True
    )

    report = {
        "stamp": stamp,
        "ours_url": args.ours,
        "baseline_url": args.baseline,
        "arms": {
            "A_naive_ours": {"pass": a_ours, "detail": a_ours_why, "http": ours_code},
            "B_partner_fields_ours": {"pass": b_ours, "detail": b_ours_why, "http": ours_code},
            "A_naive_baseline_periodcheck": {"pass": a_base, "detail": a_base_why, "http": base_code},
            "B_partner_fields_baseline_periodcheck": {
                "pass": b_base,
                "detail": b_base_why,
                "http": base_code,
            },
            "C_local_unpatched_import": {"pass": c_ok, "detail": c_why, "payload": c_detail},
            "partners_public_ours": {
                "pass": partners_ok,
                "http": partners_code,
                "detail": (
                    "track_checklist.adk_agent_builder"
                    if partners_ok
                    else f"not public manifest (http={partners_code}, snippet={partners_raw[:160]!r})"
                ),
            },
        },
        "ours_health_keys": sorted(ours_body) if isinstance(ours_body, dict) else None,
        "baseline_health_keys": sorted(base_body) if isinstance(base_body, dict) else None,
        "ours_health_raw_snippet": ours_raw[:300],
        "baseline_health_raw_snippet": base_raw[:300],
    }

    # Verdict: hosted admissibility is B+partners. C is local proof. A alone is never enough.
    hosted_admissible = b_ours and partners_ok
    finding_naive_false_green = a_ours and not b_ours
    finding_baseline_also_shallow = a_base and not b_base

    print(f"=== Partner admissibility gate === {stamp}")
    print(f"ours:     {ours_health_url}  http={ours_code}")
    print(f"baseline: {baseline_health_url}  http={base_code}")
    print()
    print(f"A  naive liveness (ours)           {'PASS' if a_ours else 'FAIL'}  · {a_ours_why}")
    print(f"B  partner fields (ours)           {'PASS' if b_ours else 'FAIL'}  · {b_ours_why}")
    print(f"   /partners public (ours)         {'PASS' if partners_ok else 'FAIL'}  · {report['arms']['partners_public_ours']['detail']}")
    print(f"A  naive liveness (PeriodCheck)    {'PASS' if a_base else 'FAIL'}  · {a_base_why}")
    print(f"B  partner fields (PeriodCheck)    {'PASS' if b_base else 'FAIL'}  · {b_base_why}")
    print(f"C  local unpatched ADK+SDK         {'PASS' if c_ok else 'FAIL'}  · {c_why}")
    print()
    if finding_naive_false_green:
        print("FINDING: Arm A passes on our hosted /health while Arm B fails.")
        print("         ok=true is not partner admissibility. Revision still strips fields.")
    if finding_baseline_also_shallow:
        print("BASELINE: PeriodCheck /api/health is also liveness-only — no gemini/parallel/adk keys.")
        print("          External bar is first-run UX + live-evaluation.json, not health partner fields.")
    if c_ok and not hosted_admissible:
        print("LOCAL:    Unpatched engine_default=adk is true in this checkout; hosted stays RED until Oscar deploy.")
    print()
    if hosted_admissible and c_ok:
        print("VERDICT: HOSTED+LOCAL ADMISSIBLE")
        rc = 0
    elif c_ok and not hosted_admissible:
        print("VERDICT: LOCAL OK · HOSTED RED (deploy required)")
        rc = 2
    else:
        print("VERDICT: NOT ADMISSIBLE")
        rc = 1

    report["finding_naive_false_green"] = finding_naive_false_green
    report["finding_baseline_also_shallow"] = finding_baseline_also_shallow
    report["hosted_admissible"] = hosted_admissible
    report["verdict_rc"] = rc

    out = args.json_out or (ROOT / "docs" / f"RECEIPT-partner-admissibility-gate-{stamp[:10]}.json")
    out.write_text(json.dumps(report, indent=2) + "\n")
    print(f"wrote {out}")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
