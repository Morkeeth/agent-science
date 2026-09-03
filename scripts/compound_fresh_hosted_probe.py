#!/usr/bin/env python3
"""Hosted compound A/B with UUID-embedded claims — forces Parallel on Run A.

Warm GCS shelf can zero out compound-mini Parallel counts. This probe embeds a
unique token in every claim so Run A must call Parallel at least once, then Run B
reuses the overlapping claim (corpus_hits >= 1) with fewer or equal Parallel calls.

Usage: python3 scripts/compound_fresh_hosted_probe.py [BASE_URL]
"""
from __future__ import annotations

import json
import sys
import time
import urllib.request
import uuid


def run(base: str, script: str, subject: str, label: str) -> dict:
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
    base = (
        sys.argv[1]
        if len(sys.argv) > 1
        else "https://agent-science-568004190078.us-central1.run.app"
    )
    token = uuid.uuid4().hex[:12]
    subject = f"compound-fresh-{token}"
    script_a = f"""NARRATOR (V.O.)
In {token[:4]} the Archive of Zephyr-{token} passed Regulation Z-{token.upper()} for orphan media.
The Collective-{token} estimated that fifty-one percent of pre-contact works lack authorship."""
    script_b = f"""NARRATOR (V.O.)
In {token[:4]} the Archive of Zephyr-{token} passed Regulation Z-{token.upper()} for orphan media.
The Phobos Library-{token} opened digitisation in 2851 with forty-two staff members."""

    a = run(base, script_a, subject, "RUN_A")
    b = run(base, script_b, subject, "RUN_B")
    ap = a.get("parallel_calls") or 0
    bp = b.get("parallel_calls") or 0
    bh = b.get("corpus_hits") or 0
    # Run A must exercise Parallel; Run B must compound.
    ok = ap >= 1 and bh >= 1 and bp <= ap
    print(
        "COMPOUND",
        {
            "subject": subject,
            "A_parallel": ap,
            "B_parallel": bp,
            "B_hits": bh,
            "pass": ok,
        },
    )
    if not ok:
        print(
            "FAIL: need A_parallel>=1, corpus_hits>=1 on B, B_parallel<=A_parallel",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
