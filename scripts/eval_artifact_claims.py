#!/usr/bin/env python3
"""Qwen eval gate — every artifact claim measured at the submitted commit.

Baseline arm: what a competent team does in two hours — trust the numbers printed
in SUBMISSION-PACK / COMPOUND exhibit without re-running the object.

Shipping arm: re-derive each claim at its object (suite exit, compound receipt,
hosted HTTP, GitHub visibility). A claim is correct only when the object agrees.

This gate exists because four retros of the Qwen loss failed the row
"Every artifact claim measured at the submitted commit."

Run: python3 scripts/eval_artifact_claims.py
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
from typing import Callable

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from eval_stats import format_ci, mcnemar_exact  # noqa: E402

PACK = ROOT / "docs/SUBMISSION-PACK-2026-08-29.md"
COMPOUND = ROOT / "docs/COMPOUND-EXHIBIT-2026-08-29.md"
HOST = os.environ.get(
    "AGENT_SCIENCE_HOST",
    "https://agent-science-568004190078.us-central1.run.app",
)
OFFLINE = "--offline" in sys.argv

SUITES = [
    ("test_watch_it_go_red.py", "watch_it_go_red"),
    ("test_adk_default_path.py", "adk_default_path"),
    ("test_registry_surface.py", "registry_surface"),
    ("test_cross_subject_reuse.py", "cross_subject_reuse"),
    ("test_backfill_seeds_reuse.py", "backfill_seeds_reuse"),
    ("test_clear_corpus.py", "clear_corpus"),
    ("test_search_path.py", "search_path"),
    ("test_source_map.py", "source_map"),
    ("test_refusal_correctness.py", "refusal_correctness"),
    ("test_partner_runtime.py", "partner_runtime"),
    ("test_parallel_integration.py", "parallel_integration"),
]


def _run(cmd: list[str], *, timeout: int = 180) -> tuple[int, str]:
    proc = subprocess.run(
        cmd, capture_output=True, text=True, cwd=str(ROOT), timeout=timeout
    )
    return proc.returncode, (proc.stdout or "") + (proc.stderr or "")


def _parse_suite_pass(out: str) -> tuple[int, int] | None:
    m = re.search(r"(\d+)\s+passed,\s+(\d+)\s+failed", out)
    if m:
        p, f = int(m.group(1)), int(m.group(2))
        return p, p + f
    m = re.search(r"(\d+)/(\d+)\s+passed", out)
    if m:
        return int(m.group(1)), int(m.group(2))
    if "all passed" in out.lower():
        passes = len(re.findall(r"^\s*PASS", out, re.M))
        return passes, passes
    return None


def _pack_suite_claim(key: str) -> str | None:
    text = PACK.read_text()
    m = re.search(rf"\|\s*{re.escape(key)}\s*\|[^|]*\|\s*\*\*(\d+)/(\d+)\*\*", text)
    if not m:
        return None
    return f"{m.group(1)}/{m.group(2)}"


def _measure_suite(filename: str, key: str) -> dict:
    pack = _pack_suite_claim(key)
    code, out = _run([sys.executable, str(ROOT / "tests" / filename)])
    parsed = _parse_suite_pass(out)
    if parsed is None:
        measured = f"UNPARSEABLE exit={code}"
        ok = False
    else:
        p, t = parsed
        measured = f"{p}/{t}"
        ok = pack == measured and code == 0 and p == t
    return {
        "pack_says": pack or "MISSING",
        "measured": measured,
        "ok": ok,
        "object": f"python3 tests/{filename}",
    }


def _measure_compound() -> dict:
    text = PACK.read_text()
    m = re.search(
        r"A=\*\*(\d+)\*\*.*?B=\*\*(\d+)\*\*.*?corpus hits?=\*\*(\d+)\*\*",
        text,
        re.S | re.I,
    )
    pack = f"A={m.group(1)}→B={m.group(2)} hits={m.group(3)}" if m else "MISSING"
    # Prefer live re-run of the receipt script (writes COMPOUND + exit code).
    code, out = _run([sys.executable, str(ROOT / "scripts/compound_exhibit_receipt.py")], timeout=240)
    body = COMPOUND.read_text() if COMPOUND.exists() else out
    cm = re.search(
        r"\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*([+-]?\d+)\s*\|\s*(\d+)\s*\|",
        body,
    )
    if cm:
        measured = f"A={cm.group(1)}→B={cm.group(2)} hits={cm.group(4)}"
        ok = (
            code == 0
            and int(cm.group(2)) < int(cm.group(1))
            and int(cm.group(4)) >= 1
            and pack == measured
        )
    else:
        measured = f"UNPARSEABLE exit={code}"
        ok = False
    return {
        "pack_says": pack,
        "measured": measured,
        "ok": ok,
        "object": "python3 scripts/compound_exhibit_receipt.py",
    }


def _http(path: str, *, follow: bool = False, method: str = "GET",
          body: bytes | None = None, timeout: float = 20.0) -> tuple[int, str, str]:
    url = HOST.rstrip("/") + path
    req = urllib.request.Request(url, data=body, method=method)
    try:
        if follow:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                final = resp.geturl()
                data = resp.read(800).decode("utf-8", "replace")
                return resp.status, final, data
        # no-follow: use opener that doesn't handle redirects
        class _NoRedir(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: N802
                return None

        opener = urllib.request.build_opener(_NoRedir)
        try:
            with opener.open(req, timeout=timeout) as resp:
                return resp.status, resp.geturl(), resp.read(400).decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            loc = e.headers.get("Location", "")
            return e.code, loc or e.geturl(), e.read(400).decode("utf-8", "replace")
    except Exception as e:
        return 0, "", f"{type(e).__name__}: {e}"


def _measure_hosted_health() -> dict:
    code, final, body = _http("/health", follow=True)
    ok = code == 200 and '"ok": true' in body.replace(" ", "")
    # tolerate spaced JSON
    ok = code == 200 and ("\"ok\": true" in body or '"ok":true' in body.replace(" ", ""))
    pack = "hosted /health 200 ok"
    measured = f"HTTP {code} body={body[:120]!r}"
    return {
        "pack_says": pack,
        "measured": measured,
        "ok": ok,
        "object": f"curl {HOST}/health",
    }


def _pack_mentions_hosted_login() -> bool:
    text = PACK.read_text()
    return bool(re.search(
        r"private-workspaces|workspace (bearer )?token|/login|login wall|Sign in required",
        text,
        re.I,
    ))


def _measure_hosted_stranger_search() -> dict:
    """Object: unauthenticated /search is behind login. Pack must say so."""
    pack_honest = _pack_mentions_hosted_login()
    pack = ("pack names hosted login / private-workspaces" if pack_honest
            else "pack still implies open stranger /search")
    code, loc, body = _http("/search?q=Directive+2012/28/EU&live=false", follow=False)
    code2, final, body2 = _http("/search?q=Directive+2012/28/EU&live=false", follow=True)
    login_wall = (
        code in (301, 302, 303, 401)
        or "Sign in" in body2
        or "/login" in final
        or "login" in (loc or "").lower()
    )
    measured = (
        f"first={code} loc={loc!r}; follow={code2} final={final}; "
        f"login_wall={login_wall}; pack_honest={pack_honest}"
    )
    ok = login_wall and pack_honest
    return {
        "pack_says": pack,
        "measured": measured,
        "ok": ok,
        "object": f"curl -D- {HOST}/search?q=...&live=false",
    }


def _measure_hosted_visibility_ui() -> dict:
    """Object: /visibility/ui redirects to Sign in. Pack must not sell it as open."""
    pack_honest = _pack_mentions_hosted_login()
    pack = ("pack names hosted login / private-workspaces" if pack_honest
            else "pack/Devpost still sells open /visibility/ui")
    code, loc, _ = _http("/visibility/ui?q=ralph", follow=False)
    code2, final, body2 = _http("/visibility/ui?q=ralph", follow=True)
    login_wall = "Sign in" in body2 or "/login" in final or code == 401
    measured = (
        f"first={code} loc={loc!r}; follow={code2} final={final}; "
        f"login_wall={login_wall}; pack_honest={pack_honest}"
    )
    ok = login_wall and pack_honest
    return {
        "pack_says": pack,
        "measured": measured,
        "ok": ok,
        "object": f"curl -L {HOST}/visibility/ui",
    }


def _measure_public_repo() -> dict:
    pack_text = PACK.read_text()
    # False when the quantified table still says Private until submit.
    pack_private_lie = bool(re.search(
        r"Public repo\s*\|\s*Stranger can clone\s*\|\s*\[[ ]\]\s*\|\s*Private until submit",
        pack_text,
        re.I,
    ))
    pack_says_public = bool(re.search(
        r"Public repo\s*\|\s*.*\|\s*\[x\]\s*\|\s*.*public since 2026-08-22",
        pack_text,
        re.I,
    )) or bool(re.search(r"repo\s+\*\*PUBLIC\*\*|public since 2026-08-22", pack_text, re.I))
    pack = ("pack still says Private until submit" if pack_private_lie
            else ("pack acknowledges public since 2026-08-22" if pack_says_public
                  else "pack public-repo row ambiguous"))
    try:
        req = urllib.request.Request(
            "https://api.github.com/repos/Morkeeth/agent-science",
            headers={"Accept": "application/vnd.github+json", "User-Agent": "agent-science-eval"},
        )
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode())
        is_private = bool(data.get("private"))
        visibility = data.get("visibility")
        measured = f"private={is_private} visibility={visibility}"
        ok = (not is_private) and pack_says_public and (not pack_private_lie)
    except Exception as e:
        measured = f"ERROR {type(e).__name__}: {e}"
        ok = False
    return {
        "pack_says": pack,
        "measured": measured,
        "ok": ok,
        "object": "GET https://api.github.com/repos/Morkeeth/agent-science",
    }


def _claims() -> list[tuple[str, str, Callable[[], dict]]]:
    out: list[tuple[str, str, Callable[[], dict]]] = []
    for filename, key in SUITES:
        out.append((f"suite:{key}", f"SUBMISSION-PACK {key} count", lambda f=filename, k=key: _measure_suite(f, k)))
    out.append(("compound:offline", "offline compound A→B + corpus_hits", _measure_compound))
    if not OFFLINE:
        out.append(("hosted:health", "hosted /health ok", _measure_hosted_health))
        out.append(("hosted:search", "pack honesty about hosted /search login", _measure_hosted_stranger_search))
        out.append(("hosted:visibility", "pack honesty about /visibility/ui login", _measure_hosted_visibility_ui))
        out.append(("github:public", "public-repo claim matches GitHub object", _measure_public_repo))
    return out


def main() -> int:
    rows = []
    base_correct = ship_correct = 0
    b_win = c = 0
    print("Artifact claims @", ROOT)
    print("Commit:", subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT).decode().strip())
    print("Mode:", "offline (suites+compound only)" if OFFLINE else "full (includes hosted+GitHub)")
    if not OFFLINE:
        print("Host:", HOST)
    print()
    print("Baseline arm: trust SUBMISSION-PACK / paste numbers (no object re-run)")
    print("Shipping arm: re-measure each claim at its object")
    print()

    for claim_id, text, measure in _claims():
        result = measure()
        # Baseline: always "agrees with pack" — the naive arm that caused the Qwen retros.
        base_ok = True
        ship_ok = bool(result["ok"])
        if base_ok:
            base_correct += 1
        if ship_ok:
            ship_correct += 1
        if base_ok and not ship_ok:
            b_win += 1
        if ship_ok and not base_ok:
            c += 1
        mark = "OK  " if ship_ok else "FAIL"
        print(f"  {mark} {claim_id:<28} pack={result['pack_says']!r}")
        print(f"       measured={result['measured']}")
        print(f"       object: {result['object']}")
        rows.append({
            "id": claim_id,
            "text": text,
            "baseline": "TRUST_PACK",
            "shipping": "OK" if ship_ok else "FAIL",
            **result,
        })

    n = len(rows)
    print()
    print(f"Baseline:  {base_correct}/{n} = {base_correct/n:.3f}  {format_ci(base_correct, n)}")
    print(f"Shipping:  {ship_correct}/{n} = {ship_correct/n:.3f}  {format_ci(ship_correct, n)}")
    print(f"Delta (shipping - baseline): {ship_correct - base_correct:+d}")
    p, note = mcnemar_exact(b_win, c)
    print(f"McNemar:   p={p:.4f} (b={b_win} c={c} discordant) — {note}")
    if ship_correct < base_correct:
        print("FINDING: shipping exposes pack/doc lies the baseline arm cannot see.")
    elif ship_correct == base_correct:
        print("FINDING: tied — every pack claim held at object.")
    else:
        print("FINDING: shipping beats baseline (unexpected — baseline always trusts pack).")

    # Gate fails the process if any shipping claim fails — that is the point.
    failed = [r for r in rows if r["shipping"] == "FAIL"]
    if failed:
        print()
        print(f"ARTIFACT CLAIMS RED — {len(failed)} claim(s) false at object:")
        for r in failed:
            print(f"  · {r['id']}: pack={r['pack_says']!r} measured={r['measured']}")
        return 1
    print()
    print("ARTIFACT CLAIMS OK — every measured claim matches its object")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
