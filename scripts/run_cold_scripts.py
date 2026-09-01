#!/usr/bin/env python3
"""Run cold-scripts through hosted POST /clear; save JSON receipts."""
from __future__ import annotations

import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

HOST = "https://agent-science-568004190078.us-central1.run.app"
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "cold-scripts" / "receipts"


def run_one(path: Path, subject: str) -> dict:
    script = path.read_text()
    payload = json.dumps({"script": script, "subject": subject}).encode()
    req = urllib.request.Request(
        f"{HOST}/clear",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=600) as resp:
        body = resp.read().decode()
    elapsed = time.time() - t0
    data = json.loads(body)
    data["_wall_seconds"] = round(elapsed, 1)
    data["_script_file"] = path.name
    return data


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    scripts = [
        ("cold-script-1", ROOT / "cold-scripts" / "01-apollo11-postland.txt"),
        ("cold-script-2", ROOT / "cold-scripts" / "02-nova-dimming-sun.txt"),
        ("cold-script-3", ROOT / "cold-scripts" / "03-eu-orphan-works-policy.txt"),
    ]
    for subject, path in scripts:
        print(f"=== {subject} ({path.name}) ===", flush=True)
        try:
            data = run_one(path, subject)
        except urllib.error.HTTPError as e:
            data = {"ok": False, "error": e.read().decode(), "subject": subject}
        out = OUT / f"{subject}.json"
        out.write_text(json.dumps(data, indent=2))
        if data.get("ok"):
            print(
                f"  sourced={data.get('sourced')} unsourced={data.get('unsourced')} "
                f"parallel={data.get('parallel_api_calls')} "
                f"wall={data.get('_wall_seconds')}s -> {out.name}",
                flush=True,
            )
        else:
            print(f"  FAILED: {data.get('error', data)[:200]}", flush=True)
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
