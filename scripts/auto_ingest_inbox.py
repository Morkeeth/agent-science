#!/usr/bin/env python3
"""Ingest new research-inbox claims into the truth dictionary.

Fleet research lands in research-inbox/ as [CLAIM]/[URL] markdown. This verifies
each pair against the named source and seeds refusal_log — growing the dictionary
without manual ingest per file.

  python3 scripts/auto_ingest_inbox.py           # ingest all unseeded pairs
  python3 scripts/auto_ingest_inbox.py --dry-run

Hook: run after research skill sessions or from ZUP pipeline.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from clearance import ingest, refusal_log
import clear_corpus

_INBOX = ROOT / "research-inbox"
_URL = re.compile(r"https?://[^\s)\]]+")


def _pairs(path: Path) -> list[tuple[str, str]]:
    text = path.read_text(encoding="utf-8")
    pairs: list[tuple[str, str]] = []
    claim, url = None, None
    for line in text.splitlines():
        u = line.strip()
        if u.upper().startswith("[CLAIM]"):
            claim = u.split("]", 1)[-1].strip()
        elif u.upper().startswith("[URL]"):
            m = _URL.search(u)
            if m and claim:
                pairs.append((claim, m.group(0)))
            claim = None
    return pairs


def _already(con, claim: str) -> bool:
    mc = clear_corpus._must_contain(claim)
    term = mc if len(mc) >= 6 else claim
    row = refusal_log.lookup(con, term=term, assertion=claim)
    return row is not None


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Auto-ingest research-inbox into dictionary")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--production", default="auto-ingest")
    args = p.parse_args(argv)

    if not _INBOX.exists():
        print("No research-inbox/ — nothing to do")
        return 0

    con = refusal_log.connect()
    done, skipped, failed = 0, 0, 0
    for path in sorted(_INBOX.glob("*.md")):
        for claim, url in _pairs(path):
            if _already(con, claim):
                skipped += 1
                continue
            if args.dry_run:
                print(f"would ingest: {claim[:60]}… ← {url[:50]}…")
                done += 1
                continue
            try:
                res = ingest.ingest_claim(claim, url, production=args.production, fetch=True)
                print(f"[{res['label']}] {claim[:70]}")
                done += 1
            except Exception as e:
                print(f"FAIL {claim[:50]}: {e}", file=sys.stderr)
                failed += 1

    print(f"\nIngested {done} · skipped {skipped} (already in dictionary) · failed {failed}")
    print(f"Dictionary size: {refusal_log.stats(con)['n']} claims")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
