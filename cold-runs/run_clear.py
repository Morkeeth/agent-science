#!/usr/bin/env python3
"""Run POST /clear on a script file; record wall time and save JSON receipt."""
from __future__ import annotations

import json
import sys
import time
import urllib.request
from pathlib import Path

HOST = "https://agent-science-568004190078.us-central1.run.app"


def run(script_path: Path, subject: str, out_path: Path) -> dict:
    script = script_path.read_text()
    body = json.dumps({"script": script, "subject": subject}).encode()
    req = urllib.request.Request(
        f"{HOST}/clear",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    t0 = time.monotonic()
    with urllib.request.urlopen(req, timeout=600) as resp:
        raw = resp.read().decode()
    elapsed = time.monotonic() - t0
    data = json.loads(raw)
    receipt = {
        "script_path": str(script_path),
        "subject": subject,
        "wall_seconds": round(elapsed, 2),
        "parallel_api_calls": data.get("parallel_api_calls"),
        "parallel_calls": data.get("parallel_calls"),
        "claims_extracted": data.get("claims_extracted"),
        "sourced": data.get("sourced"),
        "unsourced": data.get("unsourced"),
        "corpus_hits": data.get("corpus_hits"),
        "log_hits": data.get("log_hits"),
        "ok": data.get("ok"),
        "result": data,
    }
    out_path.write_text(json.dumps(receipt, indent=2))
    print(json.dumps({k: receipt[k] for k in receipt if k != "result"}, indent=2))
    return receipt


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("usage: run_clear.py <script.txt> <subject> <out.json>")
        sys.exit(2)
    run(Path(sys.argv[1]), sys.argv[2], Path(sys.argv[3]))
