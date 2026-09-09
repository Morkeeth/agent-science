#!/usr/bin/env python3
"""Qwen eval gate — every artifact claim measured at the object.

PRIOR LOSS checklist row: "Every artifact claim measured at the submitted commit."

Two arms, identical claim IDs, symmetrical scorer (ok bool only):

  Baseline  — trust SUBMISSION-PACK as written (the naive two-hour habit: if the
              doc asserts it, treat it as true). Never opens the object.
  Shipping  — re-derive each claim at its object (suite run, curl, fixture read,
              gh visibility, offline compound).

A claim the pack prints as true that fails at the object is a shipping miss and a
baseline false-GREEN — the embarrassment this gate exists to catch.

Run: python3 scripts/eval_artifact_claims.py
Exit 0 always prints the table; exit 3 when shipping finds any false pack claim.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from eval_stats import format_ci, mcnemar_exact  # noqa: E402

PACK = ROOT / "docs/SUBMISSION-PACK-2026-08-29.md"
HOST = os.environ.get(
    "AGENT_SCIENCE_HOST",
    "https://agent-science-568004190078.us-central1.run.app",
)


@dataclass
class Claim:
    id: str
    text: str
    # What the pack currently asserts (baseline trusts this).
    pack_ok: bool
    # Callable returning (ok: bool, evidence: str) measured at object.
    measure: callable


def _run(cmd: list[str], *, timeout: int = 120) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd, capture_output=True, text=True, cwd=str(ROOT), timeout=timeout
    )


def _suite_count(filename: str) -> tuple[int, int]:
    proc = _run([sys.executable, str(ROOT / "tests" / filename)])
    out = (proc.stdout or "") + (proc.stderr or "")
    m = re.search(r"(\d+)\s+passed,\s+(\d+)\s+failed", out)
    if m:
        return int(m.group(1)), int(m.group(1)) + int(m.group(2))
    m = re.search(r"(\d+)/(\d+)\s+passed", out)
    if m:
        return int(m.group(1)), int(m.group(2))
    passes = len(re.findall(r"^\s*PASS", out, re.M))
    if passes:
        return passes, passes
    return 0, 0


def _pack_claims_n(key: str) -> int | None:
    text = PACK.read_text()
    m = re.search(rf"\|\s*{re.escape(key)}\s*\|[^|]*\|\s*\*\*(\d+)/(\d+)\*\*", text)
    return int(m.group(1)) if m else None


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: D401
        return None


def _http(path: str, *, timeout: int = 20) -> tuple[int, str]:
    """GET without following redirects — 303 to sign-in must stay visible."""
    req = urllib.request.Request(HOST + path, method="GET")
    opener = urllib.request.build_opener(_NoRedirect)
    try:
        with opener.open(req, timeout=timeout) as resp:
            body = resp.read(800).decode("utf-8", errors="replace")
            return resp.status, body
    except urllib.error.HTTPError as e:
        body = e.read(800).decode("utf-8", errors="replace") if e.fp else ""
        loc = e.headers.get("Location", "") if e.headers else ""
        if loc:
            body = f"Location: {loc}\n{body}"
        return int(e.code), body
    except Exception as e:
        return 0, f"{type(e).__name__}: {e}"


def _measure_suite(filename: str, key: str, expected: int):
    def measure():
        passed, total = _suite_count(filename)
        doc_n = _pack_claims_n(key)
        ok = passed == expected and (doc_n is None or doc_n == passed)
        return ok, f"measured={passed}/{total} pack={doc_n} expected={expected}"

    return measure


def _measure_compound():
    def measure():
        proc = _run([sys.executable, str(ROOT / "scripts/compound_exhibit_receipt.py")])
        text = (ROOT / "docs/COMPOUND-EXHIBIT-2026-08-29.md").read_text()
        m = re.search(
            r"\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*([+-]?\d+)\s*\|\s*(\d+)\s*\|", text
        )
        if not m:
            return False, "compound receipt missing quantified row"
        pa, pb, _delta, hits = map(int, m.groups())
        ok = pa > 0 and pb < pa and hits >= 1 and proc.returncode == 0
        return ok, f"A={pa} B={pb} corpus_hits={hits} exit={proc.returncode}"

    return measure


def _measure_repo_public():
    def measure():
        # Prefer gh; fall back to public API JSON (no auth needed for public repos).
        proc = _run(["gh", "api", "repos/Morkeeth/agent-science",
                     "--jq", ".private"])
        if proc.returncode == 0 and proc.stdout.strip() in {"true", "false"}:
            private = proc.stdout.strip() == "true"
            # Pack historically said private-until-submit; object is public since 2026-08-22.
            pack = PACK.read_text()
            pack_says_private = bool(re.search(
                r"Private until submit|flip repo to public", pack, re.I))
            # Shipping ok when reality is public AND pack does not claim private.
            ok = (not private) and (not pack_says_private)
            return ok, f"private={private} pack_claims_private={pack_says_private}"
        code, body = _http_raw("https://api.github.com/repos/Morkeeth/agent-science")
        try:
            data = json.loads(body)
            private = bool(data.get("private"))
        except Exception:
            return False, f"github api http={code} body={body[:120]}"
        pack_says_private = bool(re.search(
            r"Private until submit|flip repo to public", PACK.read_text(), re.I))
        ok = (not private) and (not pack_says_private)
        return ok, f"private={private} pack_claims_private={pack_says_private}"

    return measure


def _http_raw(url: str, timeout: int = 20) -> tuple[int, str]:
    req = urllib.request.Request(url, method="GET",
                                 headers={"Accept": "application/vnd.github+json",
                                          "User-Agent": "agent-science-artifact-eval"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read(4000).decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        return int(e.code), e.read(4000).decode("utf-8", errors="replace") if e.fp else ""
    except Exception as e:
        return 0, f"{type(e).__name__}: {e}"


def _measure_hosted_health():
    def measure():
        code, body = _http("/health")
        try:
            data = json.loads(body)
        except Exception:
            return False, f"http={code} non-json={body[:80]!r}"
        ok = code == 200 and data.get("ok") is True
        return ok, f"http={code} mode={data.get('mode')!r} rev={data.get('revision')!r}"

    return measure


def _measure_hosted_public_search():
    """Unauthenticated /search must not look like a live JSON desk."""

    def measure():
        code, body = _http("/search?q=2012/28/EU&live=false")
        # Success = JSON SOURCED without sign-in. 303/HTML login is a miss.
        sourced = False
        try:
            data = json.loads(body)
            sourced = data.get("label") == "SOURCED"
        except Exception:
            sourced = False
        ok = code == 200 and sourced
        return ok, f"http={code} sourced={sourced} body={body[:60]!r}"

    return measure


def _measure_hosted_visibility_panel():
    """Old judge WOW: /visibility/ui must be the search panel, not the public stub."""

    def measure():
        # Follow redirects to the canonical origin so we score the page judges land on.
        code, body = _http_follow("/visibility/ui?q=ralph+loop+agentic")
        panel = (
            ("transparency" in body.lower() and "verdict" in body.lower())
            or ("angle" in body.lower() and "SOURCED" in body)
            or ("pane" in body.lower() and "verdict" in body.lower())
        )
        # Public-entry stub explicitly says older /visibility links are local-only.
        stub = "local routes" in body.lower() or "public entry" in body.lower()
        ok = code == 200 and panel and not stub
        return ok, f"http={code} panel={panel} stub={stub} body={body[:70]!r}"

    return measure


def _measure_judge_demo():
    def measure():
        code, body = _http_follow("/judge/demo")
        ok = (
            code == 200
            and "PEP 8" in body
            and ("public" in body.lower() or "read-only" in body.lower())
        )
        return ok, f"http={code} pep8={'PEP 8' in body} body={body[:70]!r}"

    return measure


def _http_follow(path: str, *, timeout: int = 20) -> tuple[int, str]:
    req = urllib.request.Request(HOST + path, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read(120_000).decode("utf-8", errors="replace")
            return resp.status, body
    except urllib.error.HTTPError as e:
        body = e.read(120_000).decode("utf-8", errors="replace") if e.fp else ""
        return int(e.code), body
    except Exception as e:
        return 0, f"{type(e).__name__}: {e}"


def _measure_free_lookup():
    def measure():
        _run([sys.executable, str(ROOT / "scripts/seed_document_cache.py")], timeout=180)
        proc = _run([sys.executable, "-m", "clearance", "lookup", "2012/28/EU"])
        out = (proc.stdout or "") + (proc.stderr or "")
        ok = "[SOURCED]" in out and "0 Parallel" in out
        return ok, out.splitlines()[0] if out.strip() else f"exit={proc.returncode}"

    return measure


def _measure_gap_561():
    def measure():
        text = (ROOT / "fixtures/gap-report-600.md").read_text()
        m = re.search(r"561 of 600 \(94%\)", text)
        # Re-derive denominator from the fixture header, not a carried prompt number.
        items = re.search(r"\*\*Items judged:\*\*\s*(\d+)", text)
        n = int(items.group(1)) if items else -1
        ok = bool(m) and n == 600
        return ok, f"items={n} has_561_line={bool(m)}"

    return measure


def _measure_shift_247():
    def measure():
        text = (ROOT / "fixtures/shift-ai-training-vs-noncommercial.md").read_text()
        m = re.search(r"247 of 600 items \(41%\)", text)
        ok = bool(m)
        return ok, f"has_247_line={bool(m)}"

    return measure


def _claims() -> list[Claim]:
    # pack_ok: what a baseline reader who trusts the pack would score today.
    # After pack refresh, hosted-public-search pack_ok becomes False (honest).
    pack = PACK.read_text()
    paste = (ROOT / "submission/DEVPOST-PASTE.md").read_text()
    combined = pack + "\n" + paste
    pack_claims_private = bool(re.search(
        r"Private until submit|flip repo to public", pack, re.I))
    # Treat Devpost "Try it" hosted visibility/desk links as asserting a public desk.
    pack_claims_public_desk = bool(re.search(
        r"/visibility/ui\?q=|/truths/ui|hosted.*SOURCED|/search\?q=",
        combined, re.I)) and not bool(re.search(
        r"private-workspaces|withdrawn|local routes, not anonymous|"
        r"do not film|/judge/demo",
        combined, re.I))

    return [
        Claim("AC1", "watch_it_go_red 72/72", True,
              _measure_suite("test_watch_it_go_red.py", "watch_it_go_red", 72)),
        Claim("AC2", "registry_surface 16/16", True,
              _measure_suite("test_registry_surface.py", "registry_surface", 16)),
        Claim("AC3", "partner_runtime matches pack", True,
              _measure_suite("test_partner_runtime.py", "partner_runtime", 7)),
        Claim("AC4", "offline compound A→B corpus_hits≥1", True, _measure_compound()),
        Claim("AC5", "repo public and pack does not claim private",
              not pack_claims_private, _measure_repo_public()),
        Claim("AC6", "hosted /health ok", True, _measure_hosted_health()),
        Claim("AC7", "hosted public /search SOURCED without auth",
              pack_claims_public_desk, _measure_hosted_public_search()),
        Claim("AC8", "local free lookup 2012/28/EU SOURCED", True, _measure_free_lookup()),
        Claim("AC9", "gap-report fixture still states 561/600", True, _measure_gap_561()),
        Claim("AC10", "shift fixture still states 247/600", True, _measure_shift_247()),
        Claim("AC11", "hosted /visibility/ui is the judge search panel",
              pack_claims_public_desk, _measure_hosted_visibility_panel()),
        Claim("AC12", "hosted /judge/demo public read-only case", True,
              _measure_judge_demo()),
    ]


def main() -> int:
    claims = _claims()
    n = len(claims)
    print("ARTIFACT-CLAIM EVAL — every claim at its object")
    print("Baseline arm: trust SUBMISSION-PACK wording (no object open)")
    print("Shipping arm: re-derive at suite / curl / fixture / compound\n")
    print(f"{'id':<5} {'baseline':<8} {'shipping':<8} {'b_ok':<5} {'s_ok':<5} evidence")
    b_ok = s_ok = 0
    discordant_b = discordant_c = 0
    rows = []
    for c in claims:
        # Baseline: pack assertion is the score.
        baseline = c.pack_ok
        shipping, evidence = c.measure()
        b_ok += int(baseline)
        s_ok += int(shipping)
        if baseline and not shipping:
            discordant_c += 1  # shipping catches a pack false-GREEN
        if shipping and not baseline:
            discordant_b += 1
        print(f"{c.id:<5} {str(baseline):<8} {str(shipping):<8} "
              f"{str(baseline):<5} {str(shipping):<5} {evidence}")
        rows.append((c, baseline, shipping, evidence))

    print()
    print(f"Baseline:  {format_ci(b_ok, n)}")
    print(f"Shipping:  {format_ci(s_ok, n)}")
    print(f"Delta (shipping - baseline): {s_ok - b_ok:+d}")
    p, note = mcnemar_exact(discordant_b, discordant_c)
    print(f"McNemar:   p={p:.4f} ({note})")
    false_green = [c.id for c, b, s, _ in rows if b and not s]
    if false_green:
        print(f"FINDING: baseline false-GREEN on {', '.join(false_green)} — "
              "pack asserted true; object disagrees.")
    elif s_ok > b_ok:
        print("FINDING: shipping recovers claims the pack no longer asserts.")
    else:
        print("FINDING: arms agree on this set.")

    # Gate fails only when shipping finds a pack false claim still marked pack_ok.
    return 3 if false_green else 0


if __name__ == "__main__":
    raise SystemExit(main())
