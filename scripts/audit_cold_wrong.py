#!/usr/bin/env python3
"""Re-derive wrong-case audit at the source object (AS-SHIP-2).

Wrong = verdict disagrees with a human opening the cited URL (SOURCED rows)
or the script's own source URL (UNSOURCED rows where primary text exists).

Run: python3 scripts/audit_cold_wrong.py
"""
from __future__ import annotations

import json
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECEIPTS = ROOT / "cold-scripts" / "receipts"

SOURCE_URL = {
    "cold-script-1": "https://history.nasa.gov/wp-content/uploads/static/history/alsj/a11/a11.postland.html",
    "cold-script-2": "https://www.pbs.org/wgbh/nova/transcripts/3310_sun.html",
    "cold-script-3": "https://eur-lex.europa.eu/EN/legal-content/summary/wider-access-to-copyright-material-orphan-works.html",
}

# Needles chosen from extracted claim text — not from product output.
AUDIT = {
    "cold-script-1": [
        ("C1", "SOURCED", "Noun 43 displays the PGNS-calculated location of the landing site"),
        ("C2", "UNSOURCED", "UP TLM"),
        ("C3", "SOURCED", "resets all of real time command relays except bank"),
        ("C4", "UNSOURCED", "Technical Debrief"),
    ],
    "cold-script-2": [
        ("C1", "UNSOURCED", "entire United States aircraft fleet was grounded"),
        ("C2", "UNSOURCED", "David Travis"),
        ("C3", "UNSOURCED", "Gerry Stanhill"),
    ],
    "cold-script-3": [
        ("C2", "SOURCED", "promote the digitisation of and lawful intra-EU online access to orphan works"),
        ("C3", "UNSOURCED", "first published or, in the absence of publication, broadcast"),
        ("C7", "UNSOURCED", "public-interest missions"),
    ],
}


def _fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    return urllib.request.urlopen(req, timeout=60).read().decode("utf-8", "replace")


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", s).lower()


def main() -> int:
    wrong = []
    for subject, checks in AUDIT.items():
        url = SOURCE_URL[subject]
        page = _norm(_fetch(url))
        receipt = json.loads((RECEIPTS / f"{subject}.json").read_text())
        by_id = {r["claim_id"]: r for r in receipt["rows"]}
        for cid, expected_label, needle in checks:
            row = by_id.get(cid)
            if row is None:
                print(f"  SKIP {subject} {cid}: not in receipt")
                continue
            hit = _norm(needle) in page
            actual = row["label"]
            if expected_label == "SOURCED" and actual != "SOURCED":
                wrong.append((subject, cid, "false_refusal", needle[:60]))
            elif expected_label == "UNSOURCED" and hit and actual in ("UNSOURCED", "UNVERIFIED INDEPENDENCE"):
                wrong.append((subject, cid, "false_refusal_at_primary", needle[:60]))
            elif expected_label == "SOURCED" and actual == "SOURCED":
                cite = row.get("citation_url") or url
                cite_page = _norm(_fetch(cite)) if cite != url else page
                quote = (row.get("quoted_terms") or "")[:40]
                if quote and _norm(quote[:30]) not in cite_page:
                    wrong.append((subject, cid, "false_positive", quote))
    print(f"wrong_count={len(wrong)}")
    for w in wrong:
        print(f"  {w[0]} {w[1]} {w[2]}: {w[3]}")
    return 0 if wrong else 0  # informational; wrong cases are the deliverable


if __name__ == "__main__":
    raise SystemExit(main())
