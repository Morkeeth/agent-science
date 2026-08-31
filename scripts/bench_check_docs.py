#!/usr/bin/env python3
"""Re-derive SUBMISSION-PACK test counts at object — fail if docs are stale.

Run: python3 scripts/bench_check_docs.py
Exit 0 when docs/SUBMISSION-PACK-2026-08-29.md matches live suite counts.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "docs/SUBMISSION-PACK-2026-08-29.md"

SUITES = [
    ("test_watch_it_go_red.py", "watch_it_go_red", 72),
    ("test_adk_default_path.py", "adk_default_path", 5),
    ("test_registry_surface.py", "registry_surface", 16),
    ("test_cross_subject_reuse.py", "cross_subject_reuse", 2),
    ("test_backfill_seeds_reuse.py", "backfill_seeds_reuse", 2),
    ("test_clear_corpus.py", "clear_corpus", 4),
    ("test_search_path.py", "search_path", 5),
    ("test_source_map.py", "source_map", 3),
    ("test_refusal_correctness.py", "refusal_correctness", 6),
    ("test_partner_runtime.py", "partner_runtime", 6),
    ("test_parallel_integration.py", "parallel_integration", 6),
]


def _run_suite(filename: str) -> tuple[int, int]:
    path = ROOT / "tests" / filename
    proc = subprocess.run(
        [sys.executable, str(path)],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )
    out = (proc.stdout or "") + (proc.stderr or "")
    # Patterns: "72 passed, 0 failed" | "5/5 passed" | "all passed" | "2/2 passed"
    m = re.search(r"(\d+)\s+passed,\s+(\d+)\s+failed", out)
    if m:
        return int(m.group(1)), int(m.group(1)) + int(m.group(2))
    m = re.search(r"(\d+)/(\d+)\s+passed", out)
    if m:
        return int(m.group(1)), int(m.group(2))
    if "all passed" in out.lower():
        # refusal_correctness — count PASS lines
        passes = len(re.findall(r"^\s*PASS", out, re.M))
        return passes, passes
    if proc.returncode != 0:
        print(f"FAIL  {filename}: exit {proc.returncode}\n{out[-500:]}")
        return 0, 0
    print(f"WARN  {filename}: could not parse count from:\n{out[-300:]}")
    return 0, 0


def _doc_claims() -> dict[str, int]:
    text = PACK.read_text()
    claims = {}
    for _, key, _ in SUITES:
        m = re.search(rf"\|\s*{re.escape(key)}\s*\|[^|]*\|\s*\*\*(\d+)/(\d+)\*\*", text)
        if m:
            claims[key] = int(m.group(1))
    total = re.search(r"\|\s*\*\*Total\*\*\s*\|\s*\d+ suites\s*\|\s*\*\*(\d+)/(\d+)\*\*", text)
    if total:
        claims["__total__"] = int(total.group(1))
    return claims


def main() -> int:
    if not PACK.exists():
        print(f"MISSING {PACK}")
        return 1

    doc = _doc_claims()
    measured: dict[str, int] = {}
    total_pass = 0
    total_tests = 0
    stale: list[str] = []

    print("bench --check-docs · SUBMISSION-PACK counts at object\n")
    for filename, key, _expected in SUITES:
        passed, total = _run_suite(filename)
        measured[key] = passed
        total_pass += passed
        total_tests += total
        doc_n = doc.get(key)
        ok = doc_n == passed
        mark = "OK" if ok else "STALE"
        print(f"  {mark:5} {key:<22} doc={doc_n} measured={passed}/{total}")
        if not ok:
            stale.append(f"{key}: doc={doc_n} measured={passed}")

    doc_total = doc.get("__total__")
    print(f"  {'OK' if doc_total == total_pass else 'STALE':5} {'total':<22} doc={doc_total} measured={total_pass}/{total_tests}")
    if doc_total != total_pass:
        stale.append(f"total: doc={doc_total} measured={total_pass}")

    print()
    if stale:
        print("STALE COUNTS — update docs/SUBMISSION-PACK-2026-08-29.md:")
        for s in stale:
            print(f"  · {s}")
        return 1
    print(f"ALL {total_pass}/{total_tests} match SUBMISSION-PACK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
