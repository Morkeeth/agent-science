#!/usr/bin/env python3
"""Baseline arm: stripped private-workspaces /health vs shipping partner health.

Measures stranger-visible partner proofs without auth. The naive arm is exactly
what hosted revision agent-science-00028-hed returned on 2026-09-11 before the
fix — a nearer proxy that made partner verify look green in docs while the
object itself lost Gemini/Parallel/ADK fields.

Run: python3 scripts/eval_partner_health_baseline.py
"""
from __future__ import annotations

import json
import os
import sys
import urllib.request
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from cloud import partners  # noqa: E402

HOSTED = os.environ.get(
    "AGENT_SCIENCE_URL",
    "https://agent-science-568004190078.us-central1.run.app",
)


def fetch(url: str) -> tuple[int, dict | str]:
    req = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            body = resp.read().decode()
            try:
                return resp.status, json.loads(body)
            except json.JSONDecodeError:
                return resp.status, body
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        try:
            return e.code, json.loads(body)
        except Exception:
            return e.code, body


def main() -> int:
    naive = {
        "ok": True,
        "service": "agent-science",
        "mode": "private-workspaces",
        "revision": "agent-science-00028-hed",
    }
    with patch.dict(
        os.environ,
        {
            "AGENT_BUILDER": "1",
            "GCP_PROJECT": "hack-fleet",
            "PARALLEL_API_KEY": "pk-live-abc",
            "K_REVISION": "local-shipping",
        },
        clear=False,
    ):
        with patch("cloud.agent.adk_available", return_value=True):
            with patch("cloud.agent.adk_version", return_value="2.7.1"):
                with patch("clearance.search.sdk_available", return_value=True):
                    with patch("clearance.search.sdk_version", return_value="1.3.2"):
                        shipping_health = partners.health(mode="private-workspaces")
                        shipping_manifest = partners.manifest(
                            gemini_path="vertex:hack-fleet", adk_default=True
                        )

    naive_score = partners.partner_proof_score(naive, None)
    ship_score = partners.partner_proof_score(shipping_health, shipping_manifest)

    print("=== Partner health baseline ===")
    print("naive_arm (stripped hosted 00028 shape):", naive_score)
    print("shipping_arm (code path):", ship_score)
    print(
        "delta:",
        ship_score["score"] - naive_score["score"],
        f"({naive_score['score']}/{naive_score['denominator']} → "
        f"{ship_score['score']}/{ship_score['denominator']})",
    )

    live_code, live_health = fetch(f"{HOSTED}/health")
    live_p_code, live_partners = fetch(f"{HOSTED}/partners")
    live_score = None
    if isinstance(live_health, dict):
        live_score = partners.partner_proof_score(
            live_health, live_partners if isinstance(live_partners, dict) else None
        )
    print("live_hosted /health HTTP", live_code, "→", live_health if not isinstance(live_health, str) else live_health[:120])
    print("live_hosted /partners HTTP", live_p_code)
    print("live_hosted score:", live_score)

    assert ship_score["score"] == ship_score["denominator"], ship_score
    assert ship_score["score"] > naive_score["score"], (naive_score, ship_score)

    if live_score and live_score["score"] < ship_score["score"]:
        print(
            "FINDING: live hosted still on naive/stripped arm — "
            "Oscar deploy required for /health+/partners fix"
        )
        print("BLOCKED_DEPLOY=1")
        return 0  # measured finding, not a code failure

    print("PASS shipping beats naive; live matches shipping" if live_score else "PASS shipping beats naive")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
