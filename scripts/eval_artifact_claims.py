#!/usr/bin/env python3
"""PRIOR LOSS gate — every artifact claim measured at HEAD (not carried).

Baseline arm (NAIVE): trust the document's printed ratios — always "pass".
Shipping arm: re-derive each bound claim at its object and fail on drift.

Also flags soft claims (e.g. "265+ claims") that name a number without a
command that can reproduce it — those are the failure mode from the Qwen loss
retros ("fitted to whatever had most recently been measured").

Run: python3 scripts/eval_artifact_claims.py
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "docs/SUBMISSION-PACK-2026-08-29.md"
MANIFEST = ROOT / "research-corpus/MANIFEST.json"

# Bound claims: (label, how to measure, pattern in pack OR absolute expected)
SUITE_FILES = [
    ("watch_it_go_red", "tests/test_watch_it_go_red.py"),
    ("adk_default_path", "tests/test_adk_default_path.py"),
    ("registry_surface", "tests/test_registry_surface.py"),
    ("cross_subject_reuse", "tests/test_cross_subject_reuse.py"),
    ("backfill_seeds_reuse", "tests/test_backfill_seeds_reuse.py"),
    ("clear_corpus", "tests/test_clear_corpus.py"),
    ("search_path", "tests/test_search_path.py"),
    ("source_map", "tests/test_source_map.py"),
    ("refusal_correctness", "tests/test_refusal_correctness.py"),
    ("partner_runtime", "tests/test_partner_runtime.py"),
    ("parallel_integration", "tests/test_parallel_integration.py"),
]


def _run_suite(rel: str) -> tuple[int, int]:
    proc = subprocess.run(
        [sys.executable, str(ROOT / rel)],
        capture_output=True, text=True, cwd=str(ROOT),
    )
    out = (proc.stdout or "") + (proc.stderr or "")
    m = re.search(r"(\d+)\s+passed,\s+(\d+)\s+failed", out)
    if m:
        return int(m.group(1)), int(m.group(1)) + int(m.group(2))
    m = re.search(r"(\d+)/(\d+)\s+passed", out)
    if m:
        return int(m.group(1)), int(m.group(2))
    if "all passed" in out.lower():
        passes = len(re.findall(r"^\s*PASS", out, re.M))
        return passes, passes
    return 0, 0


def _pack_ratio(key: str) -> tuple[int, int] | None:
    text = PACK.read_text()
    m = re.search(rf"\|\s*{re.escape(key)}\s*\|[^|]*\|\s*\*\*(\d+)/(\d+)\*\*", text)
    if not m:
        return None
    return int(m.group(1)), int(m.group(2))


def _soft_claims(text: str) -> list[str]:
    """Numbers that look like live inventory without a command tether."""
    soft = []
    for m in re.finditer(r"\*\*(\d+)\+?\s*claims\*\*", text, re.I):
        soft.append(m.group(0))
    for m in re.finditer(r"on disk[^\n]{0,40}(\d+)\+?\s*claims", text, re.I):
        soft.append(m.group(0)[:80])
    # "265+ claims" style without bold
    for m in re.finditer(r"(?<!\d)(\d{2,4})\+\s*claims", text, re.I):
        soft.append(m.group(0))
    return soft


def _freeze_check() -> dict:
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts/freeze_population.py"), "--check"],
        capture_output=True, text=True, cwd=str(ROOT),
    )
    # first JSON object in stdout
    try:
        start = proc.stdout.index("{")
        end = proc.stdout.rindex("}") + 1
        return json.loads(proc.stdout[start:end])
    except Exception:
        return {"ok": False, "error": proc.stdout[-400:] + proc.stderr[-400:]}


def main() -> int:
    print("ARTIFACT CLAIMS AT HEAD — baseline trusts docs; shipping re-derives\n")
    pack_text = PACK.read_text() if PACK.exists() else ""
    soft = _soft_claims(pack_text)

    # --- Baseline arm: trust printed pack ratios (no execution) ---
    baseline_ok = True
    for key, _ in SUITE_FILES:
        ratio = _pack_ratio(key)
        if ratio is None:
            baseline_ok = False
            print(f"NAIVE  {key:<22} MISSING in pack")
        else:
            print(f"NAIVE  {key:<22} trusts doc {ratio[0]}/{ratio[1]} (not run)")
    print(f"NAIVE  soft_claims          trusts {len(soft)} soft number(s) unread")
    print(f"NAIVE  overall              {'PASS' if baseline_ok else 'FAIL'} "
          "(baseline never opens the object)\n")

    # --- Shipping arm: run at object ---
    stale = []
    total_pass = total_n = 0
    for key, rel in SUITE_FILES:
        got_p, got_n = _run_suite(rel)
        doc = _pack_ratio(key)
        total_pass += got_p
        total_n += got_n
        doc_s = f"{doc[0]}/{doc[1]}" if doc else "—"
        ok = doc == (got_p, got_n)
        mark = "OK" if ok else "STALE"
        print(f"SHIP   {key:<22} doc={doc_s} measured={got_p}/{got_n} {mark}")
        if not ok:
            stale.append(key)

    freeze = _freeze_check()
    man = json.loads(MANIFEST.read_text()) if MANIFEST.exists() else {}
    freeze_ok = bool(freeze.get("ok")) and freeze.get("claims") == man.get("claims")
    print(
        f"SHIP   research_corpus       manifest={man.get('claims')} "
        f"freeze_check={freeze.get('claims')} "
        f"{'OK' if freeze_ok else 'STALE'}"
    )
    if not freeze_ok:
        stale.append("research_corpus")

    soft_ok = len(soft) == 0
    print(f"SHIP   soft_unbound_numbers  count={len(soft)} "
          f"{'OK' if soft_ok else 'FLAG'}")
    for s in soft:
        print(f"         · {s}")
    if not soft_ok:
        stale.append("soft_unbound_numbers")

    print()
    print(
        f"Baseline arm: PASS (trusted docs without execution) — "
        f"this is the two-hour version that ships stale ratios."
    )
    if stale:
        print(f"Shipping arm: FAIL — drift at: {', '.join(stale)}")
        print("GATE FAIL — fix pack / remove soft numbers / re-freeze before claiming.")
        return 1

    print(
        f"Shipping arm: PASS — {total_pass}/{total_n} suite tests + "
        f"{man.get('claims')} frozen corpus claims match objects."
    )
    print("GATE OK — artifact claims at HEAD match measured objects; no soft +claims.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
