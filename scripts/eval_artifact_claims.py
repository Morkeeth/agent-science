#!/usr/bin/env python3
"""Qwen-style gate — every submission claim measured at its object.

Baseline arm: the near proxy a competent team trusts in two hours
  · hosted claims → if GET /health returns ok, assume the claim holds
  · doc numbers  → trust the written figure / checkbox without opening the object

Shipping arm: open the object
  · hosted → real HTTP (follow redirects; inspect login wall / JSON shape)
  · docs   → read the fixture, re-run the suite, or parse the pack row

Gold is the shipping measurement (the object). We score whether baseline
matches shipping. False-GREEN baseline on a false claim is the embarrassment
this gate exists to catch — the same failure mode as the Qwen loss retros.

Run: python3 scripts/eval_artifact_claims.py
Env:  AGENT_SCIENCE_HOST (default hosted URL)
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from eval_stats import format_ci, mcnemar_exact  # noqa: E402

SET = json.loads((ROOT / "fixtures/artifact-claims/set.json").read_text())
HOST = os.environ.get(
    "AGENT_SCIENCE_HOST",
    "https://agent-science-568004190078.us-central1.run.app",
).rstrip("/")


def _http(method: str, path: str, body: str | None = None) -> tuple[int, str, str]:
    url = HOST + path
    data = body.encode() if body is not None else None
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={"Content-Type": "application/json", "User-Agent": "agent-science-artifact-claims/1"},
    )
    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            raw = resp.read().decode("utf-8", "replace")
            return resp.status, raw, dict(resp.headers).get("Content-Type", "")
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", "replace")
        return e.code, raw, dict(e.headers).get("Content-Type", "")
    except Exception as e:  # noqa: BLE001 — gate must record transport failure
        return 0, f"TRANSPORT_ERROR: {type(e).__name__}: {e}", ""


def _health_ok() -> bool:
    code, raw, _ = _http("GET", "/health")
    if code != 200:
        return False
    try:
        return bool(json.loads(raw).get("ok"))
    except Exception:
        return False


def _shipping_http(item: dict) -> tuple[bool, str]:
    method = item.get("method", "GET")
    code, raw, _ctype = _http(method, item["path"], item.get("body"))
    rules = item["shipping_pass"]
    reasons = []
    ok = True
    want = rules.get("status")
    if want is not None and code != want:
        ok = False
        reasons.append(f"status={code} want={want}")
    for needle in rules.get("body_must_contain", []):
        if needle.lower() not in raw.lower():
            ok = False
            reasons.append(f"missing:{needle!r}")
    for needle in rules.get("body_must_not_contain", []):
        if needle.lower() in raw.lower():
            ok = False
            reasons.append(f"forbidden:{needle!r}")
    key = rules.get("json_key")
    if key:
        try:
            payload = json.loads(raw)
            if key not in payload:
                ok = False
                reasons.append(f"json_missing:{key}")
        except Exception:
            ok = False
            reasons.append("not_json")
    detail = f"HTTP {code}" + ("; " + "; ".join(reasons) if reasons else " OK")
    # Truncate body hint for login walls
    if "Sign in" in raw[:500]:
        detail += " [login wall]"
    return ok, detail


def _shipping_doc(item: dict) -> tuple[bool, str]:
    kind = item["shipping"]
    if kind == "fixture_contains":
        text = (ROOT / item["fixture"]).read_text()
        hit = item["must_contain"] in text
        return hit, f"fixture {'HAS' if hit else 'MISSING'} {item['must_contain']!r}"
    if kind == "run_suite":
        proc = subprocess.run(
            [sys.executable, str(ROOT / item["suite"]), "-q"],
            capture_output=True,
            text=True,
            cwd=str(ROOT),
        )
        out = (proc.stdout or "") + (proc.stderr or "")
        expect = item["expect_pass_total"]  # e.g. 16/16
        # Accept "16/16 passed" or "72 passed, 0 failed"
        n, total = expect.split("/")
        ok = (
            f"{n}/{total} passed" in out
            or (f"{n} passed" in out and ("0 failed" in out or "failed" not in out.lower()))
        )
        # watch_it_go_red prints "72 passed, 0 failed"
        if not ok and re.search(rf"\b{n}\s+passed,\s+0\s+failed", out):
            ok = True
        last = out.strip().splitlines()[-1] if out.strip() else f"exit={proc.returncode}"
        return ok, last[-160:]
    if kind == "pack_public_repo_row":
        pack = (ROOT / "docs/SUBMISSION-PACK-2026-08-29.md").read_text()
        # Claim under test: pack still says Private until submit (stale).
        # Shipping PASS means the claim-as-stated is TRUE in the pack text.
        # We want this to FAIL once the pack is corrected to PUBLIC.
        stale = "Private until submit" in pack
        # Also check live GitHub visibility via public cloneability is not
        # required here — constitution already records PublicEvent 2026-08-22.
        # Gold for "pack still says Private" is the pack text itself.
        return stale, ("pack contains 'Private until submit'" if stale
                       else "pack no longer claims Private until submit")
    return False, f"unknown shipping kind {kind}"


def _baseline(item: dict, health: bool) -> tuple[bool, str]:
    kind = item["baseline"]
    if kind == "health_ok_implies_pass":
        return health, "health ok → assume claim holds" if health else "health down → claim fail"
    if kind == "trust_pack_checkbox":
        # Naive: whatever the pack checkbox says is believed without git/GitHub.
        # For D1 the asserted claim is "still Private" — baseline trusts pack text
        # the same way shipping reads it, BUT without checking the constitution
        # date. Treat as always-true proxy (docs are trusted).
        return True, "trust pack checkbox as written"
    if kind == "trust_pack_number":
        return True, "trust written number / suite count"
    return False, f"unknown baseline {kind}"


def main() -> int:
    health = _health_ok()
    print("ARTIFACT-CLAIM EVAL — submission claims at their objects")
    print(f"Host: {HOST}")
    print(f"Health ok: {health}")
    print(f"Baseline: near proxy (health→hosted pass; trust written docs)")
    print(f"Shipping: open the HTTP/fixture/suite object\n")
    print(f"{'id':<5} {'cat':<16} {'baseline':<8} {'shipping':<8} {'b_ok':<5} {'s_ok':<5} detail")

    base_correct = ship_correct = 0
    b_win = c = 0
    rows = []
    n = len(SET["items"])

    for item in SET["items"]:
        if item["category"] == "hosted_stranger":
            ship_ok, ship_detail = _shipping_http(item)
        else:
            ship_ok, ship_detail = _shipping_doc(item)
        base_ok_raw, base_detail = _baseline(item, health)

        # Gold = shipping measurement of whether the asserted claim holds.
        gold = ship_ok
        base_matches = base_ok_raw == gold
        ship_matches = True  # shipping defines gold

        # For scoring "arm correctness at detecting truth":
        # baseline is correct when its verdict equals shipping (gold).
        base_correct += int(base_matches)
        ship_correct += int(ship_matches)
        if base_matches and not ship_matches:
            b_win += 1
        elif ship_matches and not base_matches:
            c += 1

        mark_b = "PASS" if base_ok_raw else "FAIL"
        mark_s = "PASS" if ship_ok else "FAIL"
        print(
            f"{item['id']:<5} {item['category']:<16} {mark_b:<8} {mark_s:<8} "
            f"{str(base_matches):<5} {str(ship_matches):<5} {ship_detail}"
        )
        rows.append({
            "id": item["id"],
            "claim": item["claim"],
            "baseline_says_holds": base_ok_raw,
            "shipping_says_holds": ship_ok,
            "baseline_matches_object": base_matches,
            "detail": ship_detail,
            "baseline_detail": base_detail,
        })

    print()
    print(f"Baseline matches object:  {format_ci(base_correct, n)}")
    print(f"Shipping is the object:   {format_ci(ship_correct, n)}")
    print(f"Delta (shipping - baseline match rate): {ship_correct - base_correct:+d}")
    p, interp = mcnemar_exact(b_win, c)
    print(f"McNemar:   p={p:.4f} ({interp})")

    false_green = [r for r in rows if r["baseline_says_holds"] and not r["shipping_says_holds"]]
    true_holds = [r for r in rows if r["shipping_says_holds"]]
    false_holds = [r for r in rows if not r["shipping_says_holds"]]

    print()
    if false_green:
        print(f"FINDING: baseline false-GREEN on {len(false_green)}/{n} claims — proxy said TRUE, object said FALSE:")
        for r in false_green:
            print(f"  · {r['id']}: {r['claim']}")
            print(f"      {r['detail']}")
    else:
        print("FINDING: no baseline false-GREEN — proxy matched the object on every item.")

    print(f"Object truth: {len(true_holds)} claims HOLD · {len(false_holds)} claims DO NOT HOLD at measurement time.")

    # Exit 0 always after a complete measurement — this gate reports, it does not
    # hide embarrassment. Callers read the FINDING. Non-zero only on eval crash.
    out_path = ROOT / "docs" / "ARTIFACT-CLAIM-EVAL-2026-09-07.json"
    out_path.write_text(json.dumps({
        "host": HOST,
        "health_ok": health,
        "n": n,
        "baseline_match": base_correct,
        "shipping_is_object": ship_correct,
        "false_green": [r["id"] for r in false_green],
        "holds": [r["id"] for r in true_holds],
        "does_not_hold": [r["id"] for r in false_holds],
        "rows": rows,
        "mcnemar_p": p,
    }, indent=2) + "\n")
    print(f"\nWrote {out_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
