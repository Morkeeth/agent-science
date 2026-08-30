#!/usr/bin/env python3
"""Boot the vision: fleet websearches → verified registry rows.

Every file in research-corpus/ is a saved websearch. This seeds offline caches and
backfills the refusal log so ask_registry and /registry have truths before first live run.

    python3 scripts/boot_registry.py

Stranger path (no keys):
    git clone …/agent-science && cd agent-science && python3 scripts/boot_registry.py
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main() -> int:
    py = sys.executable
    steps = [
        ([py, str(ROOT / "scripts/seed_document_cache.py")], "document + search cache"),
        ([py, str(ROOT / "clear_corpus.py"), "research-corpus", "--backfill"],
         "research-corpus → refusal_log registry"),
    ]
    for cmd, label in steps:
        print(f"\n→ {label}")
        r = subprocess.run(cmd, cwd=ROOT)
        if r.returncode != 0:
            print(f"FAILED: {label}", file=sys.stderr)
            return r.returncode

    from clearance import refusal_log
    con = refusal_log.connect()
    st = refusal_log.stats(con)
    print(f"\nRegistry ready: {st['n']} claims · {st['cleared']} sourced · "
          f"{st['refused']} refused · {st['productions']} productions")
    print("  python3 ask_registry.py --browse")
    print("  python3 ask_registry.py --serve   # local :8091")
    print("  curl -s localhost:8080/registry   # after cloud/service.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
