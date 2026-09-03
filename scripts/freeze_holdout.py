#!/usr/bin/env python3
"""Re-pin holdout MANIFEST after intentional label or fixture changes.

Run ONLY after human review — not during tuning passes.

Usage: python3 scripts/freeze_holdout.py
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOLDOUT = ROOT / "fixtures/refusal-correctness"
MANIFEST = HOLDOUT / "MANIFEST.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    files = ["set.json"] + sorted(
        str(p.relative_to(HOLDOUT)).replace("\\", "/")
        for p in (HOLDOUT / "docs").glob("*")
        if p.is_file()
    )
    manifest = {
        "frozen_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "labelled_before_tuning": False,
        "note": "Re-frozen after intentional holdout change — update hack.md LOG.",
        "files": {rel: _sha256(HOLDOUT / rel) for rel in files},
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {MANIFEST} ({len(files)} files)")


if __name__ == "__main__":
    main()
