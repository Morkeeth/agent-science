#!/usr/bin/env python3
"""Fail when docs claim hosted engine_default while live /health lacks it.

Catches the 2026-09-11 failure mode: STATUS/PITCH/receipts said
`engine_default: adk` while Cloud Run returned only ok/service/mode/revision.

Usage:
  python3 scripts/check_hosted_partner_claims.py
  python3 scripts/check_hosted_partner_claims.py --base URL
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASE = "https://agent-science-568004190078.us-central1.run.app"

# Docs that historically asserted live partner health. Soft claims ("until deploy")
# and FINDING/BLOCKED files are excluded.
CLAIM_FILES = [
    "docs/STATUS.md",
    "docs/PITCH-TOMORROW.md",
    "docs/SUBMISSION-PACK-2026-08-29.md",
]

# A claim is "live affirmative" if it asserts engine_default on hosted without
# an adjacent RED/STRIPPED/until-deploy hedge on the same line.
AFFIRM = re.compile(r"engine_default:\s*adk|`engine_default`:\s*`?adk`?", re.I)
HEDGE = re.compile(
    r"STRIPPED|RED|until\s+Oscar|until\s+deploy|00028|FINDING-hosted-partner|"
    r"prove_partners_local|local prove|local desk|deploy\.sh|\[ \]",
    re.I,
)


def fetch_health(base: str) -> dict:
    url = base.rstrip("/") + "/health"
    req = urllib.request.Request(url, headers={"User-Agent": "agent-science-partner-claim-check"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode())


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default=DEFAULT_BASE)
    args = ap.parse_args()

    try:
        health = fetch_health(args.base)
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
        print(f"FAIL: could not fetch {args.base}/health: {e}")
        return 1

    print("live /health:", json.dumps(health, indent=2))
    has_partners = all(
        k in health
        for k in ("gemini", "parallel", "agent_builder", "engine_default", "gemini_path")
    )

    stale: list[str] = []
    for rel in CLAIM_FILES:
        path = ROOT / rel
        if not path.exists():
            continue
        for i, line in enumerate(path.read_text().splitlines(), 1):
            if AFFIRM.search(line) and not HEDGE.search(line):
                if not has_partners:
                    stale.append(f"{rel}:{i}: {line.strip()}")

    if not has_partners:
        print(
            "\nLIVE HEALTH MISSING PARTNER FIELDS — "
            "see docs/FINDING-hosted-partner-proof-dark-2026-09-11.md"
        )
        if stale:
            print("STALE AFFIRMATIVE DOC CLAIMS (no hedge on same line):")
            for s in stale:
                print("  ·", s)
            return 1
        print("No unhedged affirmative doc claims — docs honest about the outage.")
        return 0

    print("live partner fields present")
    if health.get("engine_default") == "adk":
        print("engine_default: adk — OK")
    else:
        print(f"engine_default: {health.get('engine_default')!r} (named, not silent)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
