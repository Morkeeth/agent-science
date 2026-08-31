#!/usr/bin/env python3
"""Freeze the measurement population: hash every COMMITTED corpus file into a manifest.

    python3 scripts/freeze_population.py [--check]

The file list comes from `git ls-files`, not from the directory, so the manifest can only
ever pin content that a clean checkout also has. That is the whole point: "REGISTRY 314
claims" did not reproduce from a clean checkout because two of the 314 rows came from
untracked files the product itself had written into the population it measures.

`--check` verifies and exits non-zero on drift, printing the diff. No argument rewrites
the manifest — a deliberate act, reviewed in the diff, that moves every published number.
"""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from clearance import population as P  # noqa: E402
import clear_corpus as C  # noqa: E402


def tracked_md() -> list[str]:
    out = subprocess.run(["git", "-C", str(ROOT), "ls-files", "research-corpus/*.md"],
                         capture_output=True, text=True, check=True).stdout
    return sorted(Path(line).name for line in out.split() if line.endswith(".md"))


def main(argv: list[str]) -> int:
    if "--check" in argv:
        v = P.verify()
        print(json.dumps(v, indent=1))
        if not v["ok"]:
            print("DRIFT — the population that produces the published number has moved.")
            return 1
        print(f"frozen population intact: {v['n_files']} files, {v['claims']} claims, "
              f"frozen {v['frozen_at']}")
        return 0

    names = tracked_md()
    missing = [n for n in names if not (P.FROZEN / n).is_file()]
    if missing:
        print(f"tracked but not on disk: {missing}")
        return 1
    files = [{"file": n, "sha256": P.sha256(P.FROZEN / n),
              "bytes": (P.FROZEN / n).stat().st_size} for n in names]
    # Count the claims the parser actually finds, over exactly these files, so the
    # manifest carries the denominator itself and a drifted count is visible in the diff.
    claims = len(C.parse_corpus(str(P.FROZEN)))
    doc = {
        "what": "the frozen measurement population every published Agent Science number "
                "is computed over",
        "frozen_at": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "source": "git ls-files research-corpus/*.md — committed content only",
        "written_by": "nothing; clearance.ingest writes to research-inbox/",
        "n_files": len(files), "claims": claims, "files": files,
    }
    P.MANIFEST.write_text(json.dumps(doc, indent=1) + "\n")
    print(f"froze {len(files)} files, {claims} claims -> "
          f"{P.MANIFEST.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
