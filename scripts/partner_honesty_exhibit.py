#!/usr/bin/env python3
"""Partner honesty exhibit — shipping compound vs naive on hosted URL.

Requires WORKSPACE_TOKEN for private-workspaces /clear. Without it, exits 2
BLOCKED (not green). Classifies sealed STRICT_DROP vs soft flat.

Usage: python3 scripts/partner_honesty_exhibit.py [BASE_URL]
"""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tests.test_partner_honesty_classify import classify  # noqa: E402

DEFAULT_BASE = "https://agent-science-568004190078.us-central1.run.app"


def _get(url: str, timeout: float = 60) -> dict:
    with urllib.request.urlopen(url, timeout=timeout) as resp:
        return json.loads(resp.read())


def _clear(base: str, script: str, subject: str, token: str, label: str) -> dict:
    body = json.dumps({"script": script, "subject": subject}).encode()
    req = urllib.request.Request(
        base.rstrip("/") + "/clear",
        data=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        },
        method="POST",
    )
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=300) as resp:
        data = json.loads(resp.read())
    keys = [
        "engine", "adk_version", "adk_tool_calls", "model_routing",
        "parallel_calls", "parallel_api_calls", "search_cache_hits",
        "corpus_hits", "log_hits", "claims_extracted", "sourced", "unsourced",
    ]
    summary = {k: data.get(k) for k in keys}
    summary["parallel_calls"] = summary.get("parallel_calls") or 0
    summary["corpus_hits"] = summary.get("corpus_hits") or 0
    summary["elapsed_s"] = round(time.time() - t0, 1)
    print(f"{label} {summary}")
    return summary


def main() -> int:
    base = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_BASE
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    token = os.environ.get("WORKSPACE_TOKEN") or os.environ.get("AGENT_SCIENCE_WORKSPACE_TOKEN") or ""
    print(f"=== Partner honesty exhibit === stamp={stamp}")
    print(f"URL: {base}")

    health = _get(base.rstrip("/") + "/health")
    print("health keys:", sorted(health.keys()))
    if health.get("gemini") is None:
        print("FINDING: hosted /health stripped of partner fields — deploy in-tree fix first.")

    if not token:
        print("BLOCKED: no WORKSPACE_TOKEN — hosted /clear is workspace-auth.")
        print("Offline classify still runs:")
        # Re-derive classify control at object (no network).
        import subprocess
        rc = subprocess.call([sys.executable, str(ROOT / "tests/test_partner_honesty_classify.py")])
        return 2 if rc == 0 else rc

    subject = f"honesty-{uuid.uuid4().hex[:10]}"
    claim = f"In honesty-{subject[-6:]} the Archive of Zephyr passed Regulation Z for orphan media."
    try:
        a = _clear(base, claim, subject, token, "A")
        b = _clear(base, claim + " The regulation named orphan works.", subject, token, "B")
    except urllib.error.HTTPError as e:
        print(f"BLOCKED: POST /clear HTTP {e.code}")
        return 2
    except Exception as e:
        print(f"FAIL: {type(e).__name__}: {e}")
        return 1

    ap = int(a.get("parallel_calls") or 0)
    bp = int(b.get("parallel_calls") or 0)
    bh = int(b.get("corpus_hits") or 0)
    cls = classify(ap, bp, bh)
    print(f"CLASS={cls} A_parallel={ap} B_parallel={bp} B_corpus_hits={bh}")
    print(f"engine A={a.get('engine')} B={b.get('engine')}")
    if cls == "SOFT_PASS_FLAT":
        print("FINDING_RED: soft pass ≠ sealed STRICT_DROP — do not film as Parallel drop")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
