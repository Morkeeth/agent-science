#!/usr/bin/env python3
"""Popular queries for devs — what to cache, alias, or ingest next."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from clearance.stack_cli import cmd_popular
import argparse


def main() -> int:
    args = argparse.Namespace(limit=15, json="--json" in sys.argv)
    if "--limit" in sys.argv:
        i = sys.argv.index("--limit")
        args.limit = int(sys.argv[i + 1])
    return cmd_popular(args)


if __name__ == "__main__":
    raise SystemExit(main())
