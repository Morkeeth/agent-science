#!/usr/bin/env python3
"""Freeze the refusal-correctness holdout: hash set.json into a manifest.

    python3 scripts/freeze_holdout.py [--check]

`--check` verifies and exits non-zero on drift. No argument rewrites the manifest —
a deliberate act, reviewed in the diff, that would invalidate every eval number on n=6.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from clearance import holdout as H  # noqa: E402


def main(argv: list[str]) -> int:
    if "--check" in argv:
        v = H.verify()
        print(json.dumps(v, indent=1))
        if not v["ok"]:
            print("DRIFT — the holdout labels may have been tuned post-hoc.")
            return 1
        print(f"holdout intact: {v['n_items']} items, labelled {v['labelled_at']}, "
              f"frozen {v['frozen_at']}")
        return 0

    if not H.SET_PATH.is_file():
        print(f"MISSING {H.SET_PATH}")
        return 1
    data = json.loads(H.SET_PATH.read_text())
    doc = {
        "what": "the refusal-correctness holdout labelled before any engine tuning pass",
        "frozen_at": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "labelled_at": data.get("labelled_at"),
        "labelled_by": data.get("labelled_by"),
        "n_items": len(data.get("items", [])),
        "set": {
            "file": "set.json",
            "sha256": H.sha256(H.SET_PATH),
            "bytes": H.SET_PATH.stat().st_size,
        },
    }
    H.MANIFEST.write_text(json.dumps(doc, indent=1) + "\n")
    print(f"froze {doc['n_items']} items -> {H.MANIFEST.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
