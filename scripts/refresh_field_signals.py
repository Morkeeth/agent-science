#!/usr/bin/env python3
"""Refresh GitHub star / push signals into truth-dictionary/field-signals.json.

Stars are an ADOPTION signal for the truth layer (what people use), not a verdict.
Requires `gh` authenticated. Does not call Parallel or Gemini.
"""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "truth-dictionary" / "field-signals.json"

REPOS = [
    ("Significant-Gravitas/AutoGPT", "agent loop adoption"),
    ("anthropics/claude-code", "dominant coding-agent surface"),
    ("hesreallyhim/awesome-claude-code", "curated what-people-use index"),
    ("Aider-AI/aider", "pair-programming agent"),
    ("cursor/cursor", "editor+agent product signal"),
    ("frankbria/ralph-claude-code", "Ralph loop used in building"),
    ("mikeyobrien/ralph-orchestrator", "Ralph orchestration active"),
]


def _gh_repo(slug: str) -> dict:
    raw = subprocess.check_output(
        ["gh", "api", f"repos/{slug}",
         "--jq", "{full_name,stargazers_count,pushed_at,html_url}"],
        text=True,
    )
    return json.loads(raw)


def main() -> int:
    github = []
    for slug, why in REPOS:
        try:
            d = _gh_repo(slug)
        except subprocess.CalledProcessError as e:
            print(f"FAIL {slug}: {e}", file=sys.stderr)
            return 1
        github.append({
            "repo": d["full_name"],
            "stars": d["stargazers_count"],
            "pushed_at": d["pushed_at"],
            "url": d["html_url"],
            "why": why,
        })
        print(f"  {d['stargazers_count']:>7} ★  {d['full_name']}")

    prev = json.loads(OUT.read_text()) if OUT.exists() else {}
    out = {
        "read_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "note": prev.get("note") or (
            "Adoption / use signals. Stars are not proof. "
            "Refresh: python3 scripts/refresh_field_signals.py"
        ),
        "github": github,
        "blogs_and_docs": prev.get("blogs_and_docs", []),
    }
    OUT.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
