#!/usr/bin/env python3
"""Live partner probe — optional keys; always writes a receipt markdown file."""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from clearance import search as parallel
from cloud import agent as adk_agent
from cloud import partners


def main() -> int:
    stamp = datetime.now(timezone.utc).isoformat()
    out_path = ROOT / "docs" / f"RECEIPT-partner-probe-{stamp[:10]}.md"

    proj = os.environ.get("GCP_PROJECT") or os.environ.get("GOOGLE_CLOUD_PROJECT") or "none"
    manifest = partners.manifest(
        gemini_path=f"vertex:{proj}",
        adk_default=os.environ.get("AGENT_BUILDER", "1") not in ("0", "false", "False"),
    )

    key_path = Path.home() / ".config" / "keys" / "parallel.key"
    probe: dict = {
        "at": stamp,
        "parallel": {
            **parallel.integration_info(),
            "key_present": bool(os.environ.get("PARALLEL_API_KEY") or key_path.exists()),
            "live_probe": None,
        },
        "adk": {
            "importable": adk_agent.adk_available(),
            "version": adk_agent.adk_version(),
        },
    }

    if probe["parallel"]["key_present"]:
        try:
            parallel.reset_calls()
            hits = parallel.find_sources(
                "Find primary source for EU Orphan Works Directive 2012/28/EU",
                ["Directive 2012/28/EU", "orphan works directive"],
                live=True,
                max_results=3,
                term="probe-orphan-works",
            )
            probe["parallel"]["live_probe"] = {
                "ok": bool(hits),
                "n_candidates": len(hits or []),
                "search_id": parallel.last_search_id(),
                "calls": parallel.calls(),
                "transport": parallel.integration_info()["transport"],
                "urls": [h.url for h in (hits or [])[:3]],
            }
        except Exception as e:
            probe["parallel"]["live_probe"] = {
                "ok": False,
                "error": type(e).__name__,
                "detail": str(e)[:240],
            }

    lines = [
        "# Partner probe receipt",
        "",
        f"**At:** {stamp}",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2),
        "```",
        "",
        "## Live Parallel",
        "",
        "```json",
        json.dumps(probe["parallel"], indent=2),
        "```",
        "",
        "## ADK",
        "",
        "```json",
        json.dumps(probe["adk"], indent=2),
        "```",
    ]
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"wrote": str(out_path), "parallel_live": probe["parallel"].get("live_probe")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
