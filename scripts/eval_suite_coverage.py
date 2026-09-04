#!/usr/bin/env python3
"""Suite coverage audit — pack 127/127 vs the full tests/ tree.

Baseline arm: treat the SUBMISSION-PACK total as the whole story (trust-doc).
Shipping arm: re-count every tests/test_*.py PASS line and report coverage.

This exists because a 127/127 headline can read as "all tests green" when half
the tree sits outside the named gate. Numbers are re-derived every run.

Run: python3 scripts/eval_suite_coverage.py
Exit 0 always when measurement succeeds; prints FINDING with coverage ratio.
Exit 1 if any suite file fails (nonzero exit).
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "docs/SUBMISSION-PACK-2026-08-29.md"

GATED = [
    "test_watch_it_go_red.py",
    "test_adk_default_path.py",
    "test_registry_surface.py",
    "test_cross_subject_reuse.py",
    "test_backfill_seeds_reuse.py",
    "test_clear_corpus.py",
    "test_search_path.py",
    "test_source_map.py",
    "test_refusal_correctness.py",
    "test_partner_runtime.py",
    "test_parallel_integration.py",
]


def _pass_count(filename: str) -> tuple[int, int]:
    path = ROOT / "tests" / filename
    proc = subprocess.run(
        [sys.executable, str(path)],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )
    out = (proc.stdout or "") + (proc.stderr or "")
    m = re.search(r"(\d+)\s+passed,\s+(\d+)\s+failed", out)
    if m:
        return int(m.group(1)), proc.returncode
    m = re.search(r"(\d+)/(\d+)\s+passed", out)
    if m:
        return int(m.group(1)), proc.returncode
    passes = len(re.findall(r"^\s*PASS\b", out, re.M))
    return passes, proc.returncode


def _pack_total() -> tuple[int, int]:
    text = PACK.read_text()
    m = re.search(
        r"\|\s*\*\*Total\*\*\s*\|\s*(\d+) suites\s*\|\s*\*\*(\d+)/(\d+)\*\*",
        text,
    )
    if not m:
        raise SystemExit("SUBMISSION-PACK missing Total row")
    return int(m.group(1)), int(m.group(2))


def main() -> int:
    pack_suites, pack_n = _pack_total()
    files = sorted(p.name for p in (ROOT / "tests").glob("test_*.py"))
    gated_set = set(GATED)

    print("SUITE-COVERAGE EVAL — pack gate vs full tests/ tree")
    print("Baseline: trust pack Total as the whole story")
    print("Shipping: re-count every test_*.py PASS line")
    print()

    gated_pass = ungated_pass = 0
    fails: list[str] = []
    print(f"{'file':<40} {'pass':>5}  gate")
    for name in files:
        p, rc = _pass_count(name)
        gated = name in gated_set
        if gated:
            gated_pass += p
        else:
            ungated_pass += p
        if rc != 0:
            fails.append(name)
        print(f"{name:<40} {p:>5}  {'GATED' if gated else 'ungated'}")

    total = gated_pass + ungated_pass
    print()
    print(f"Pack claims:     {pack_suites} suites / {pack_n} tests")
    print(f"Tree files:      {len(files)}")
    print(f"Gated PASS≈:     {gated_pass}")
    print(f"Ungated PASS≈:   {ungated_pass}")
    print(f"Tree PASS≈:      {total}")
    ratio = gated_pass / total if total else 0.0
    print(f"Coverage ratio:  {gated_pass}/{total} = {ratio:.3f}")

    # Baseline predicts coverage=1.0 (pack is everything). Shipping measures ratio.
    baseline_ok = True  # trust-doc always "OK"
    # Gold: is "pack is the whole tree" true? Only if ratio==1 and file counts match.
    claim_whole_tree = ratio >= 0.999 and len(files) == pack_suites
    shipping_ok = claim_whole_tree  # shipping says claim holds only if true
    print()
    print(
        f"Claim 'pack Total is the whole test story': "
        f"gold={claim_whole_tree} baseline_pred=True shipping_pred={shipping_ok}"
    )
    if claim_whole_tree:
        print("FINDING: pack gate covers the full tree.")
    else:
        print(
            f"FINDING: pack gate covers {ratio:.1%} of PASS lines "
            f"({gated_pass}/{total}); {len(files) - pack_suites} files ungated. "
            "Do not read 127/127 as 'all tests'."
        )

    if fails:
        print(f"FAIL suites: {fails}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
