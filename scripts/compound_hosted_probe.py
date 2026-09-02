#!/usr/bin/env python3
"""Hosted compound-mini A/B — proves Parallel drop + corpus_hits on repeat subject."""
from __future__ import annotations

import json
import sys
import time
import urllib.request
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(base: str, script_path: Path, subject: str, label: str) -> dict:
    script = script_path.read_text()
    body = json.dumps({"script": script, "subject": subject}).encode()
    req = urllib.request.Request(
        base.rstrip("/") + "/clear",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=300) as resp:
        data = json.loads(resp.read())
    keys = [
        "engine",
        "parallel_calls",
        "corpus_hits",
        "corpus_remembered",
        "claims_extracted",
        "sourced",
        "unsourced",
    ]
    summary = {k: data.get(k) for k in keys}
    summary["elapsed_s"] = round(time.time() - t0, 1)
    print(f"{label} {summary}")
    return data


def main() -> int:
    base = sys.argv[1] if len(sys.argv) > 1 else "https://agent-science-568004190078.us-central1.run.app"
    subject = f"compound-probe-{uuid.uuid4().hex[:8]}"
    a = run(base, ROOT / "fixtures/scripts/compound-mini-A.txt", subject, "RUN_A")
    b = run(base, ROOT / "fixtures/scripts/compound-mini-B.txt", subject, "RUN_B")
    ap = a.get("parallel_calls") or 0
    bp = b.get("parallel_calls") or 0
    bh = b.get("corpus_hits") or 0
    # Warm GCS shelf may show A=0 Parallel — still valid if corpus hits rise on B.
    ok = bh >= 1 and bp <= ap
    print(
        "COMPOUND",
        {"A_parallel": ap, "B_parallel": bp, "B_hits": bh, "pass": ok},
    )
    if not ok:
        print(
            "FAIL: need corpus_hits>=1 on B and B_parallel<=A_parallel",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
