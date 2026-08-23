#!/usr/bin/env python3
"""Compound exhibit — the ambitious product moment.

Runs Production A then Production B on the same subject against one corpus DB and
prints the receipt a judge / clearance lead / VC can read in ten seconds:

    Parallel calls · first production : N
    Parallel calls · second production: M
    Corpus hits on second             : H
    Fraction of search avoided        : (N-M)/N   if N>0

This is not a cache demo. It is the company sentence made measurable.

Usage:
    python3 scripts/compound_exhibit.py
    python3 scripts/compound_exhibit.py \\
        --a fixtures/scripts/documentary-orphan-works.txt \\
        --b fixtures/scripts/documentary-orphan-works-B.txt \\
        --subject orphan-works
"""
from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import agent_science  # noqa: E402


def _run(path: Path, *, subject: str, db: Path, model: str) -> dict:
    return agent_science.clear_script(
        path.read_text(),
        subject=subject,
        model=model,
        corpus_db=db,
    )


def _receipt(a: dict, b: dict) -> str:
    pa, pb = a["parallel_calls"], b["parallel_calls"]
    saved = pa - pb
    frac = (saved / pa) if pa else 0.0
    lines = [
        "# COMPOUND RECEIPT — Agent Science",
        "",
        f"Subject: `{a['subject']}`",
        "",
        "| | Production A (first) | Production B (second) |",
        "|---|---|---|",
        f"| Claims | {a['claims_extracted']} | {b['claims_extracted']} |",
        f"| SOURCED | {a['sourced']} | {b['sourced']} |",
        f"| UNSOURCED | {a['unsourced']} | {b['unsourced']} |",
        f"| **Parallel calls** | **{pa}** | **{pb}** |",
        f"| Corpus hits | {a['corpus_hits']} | {b['corpus_hits']} |",
        "",
        f"**Search avoided on second production: {saved} of {pa} calls ({frac:.0%}).**",
        "",
        "If Production B's Parallel count is not lower, the compounding claim failed on",
        "these scripts — do not pitch it. Fix keying / overlap, or pick different fixtures.",
        "",
        "## Claims requiring action (Production A)",
    ]
    gaps_a = [r for r in a["rows"] if r["label"] != "SOURCED"]
    if not gaps_a:
        lines.append("_None — unusual for a real script; check the input was not rigged._")
    else:
        for r in gaps_a:
            lines.append(f"- **{r['claim_id']}** {r['label']} — {r['why']}")
    lines += ["", "## Corpus hits on Production B (memory, not re-search)"]
    hits = [r for r in b["rows"] if r.get("corpus_hit")]
    if not hits:
        lines.append("_None — second production did not reuse memory._")
    else:
        for r in hits:
            note = ""
            if r.get("reused_from"):
                note = f' ⚠ reused evidence gathered for different wording: "{r["reused_from"][:100]}"'
            lines.append(f"- **{r['claim_id']}** {r['label']}{note}")
            if r.get("citation_url"):
                lines.append(f"  {r['citation_url']}")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--a", type=Path,
                   default=ROOT / "fixtures/scripts/documentary-orphan-works.txt")
    p.add_argument("--b", type=Path,
                   default=ROOT / "fixtures/scripts/documentary-orphan-works-B.txt")
    p.add_argument("--subject", default="orphan-works")
    p.add_argument("--model", default="gemini-3.5-flash-lite")
    p.add_argument("--db", type=Path, default=None,
                   help="Corpus path (default: fresh temp DB so the exhibit is clean)")
    p.add_argument("--json", action="store_true", help="Also print raw A/B JSON to stderr")
    args = p.parse_args()

    if not args.a.exists() or not args.b.exists():
        print(f"missing script(s): {args.a} / {args.b}", file=sys.stderr)
        return 2

    if args.db:
        db = args.db
        db.parent.mkdir(parents=True, exist_ok=True)
    else:
        tmp = tempfile.NamedTemporaryFile(prefix="compound-", suffix=".db", delete=False)
        db = Path(tmp.name)
        tmp.close()

    print(f"# Running Production A — {args.a.name}", file=sys.stderr)
    a = _run(args.a, subject=args.subject, db=db, model=args.model)
    if not a.get("ok"):
        print(a.get("error", a), file=sys.stderr)
        return 1
    print(f"# Running Production B — {args.b.name}", file=sys.stderr)
    b = _run(args.b, subject=args.subject, db=db, model=args.model)
    if not b.get("ok"):
        print(b.get("error", b), file=sys.stderr)
        return 1

    receipt = _receipt(a, b)
    print(receipt)
    print(f"\n_corpus: {db}_", file=sys.stderr)
    if args.json:
        print(json.dumps({"a": a, "b": b}, indent=1), file=sys.stderr)

    # Non-zero if the ambitious claim did not show up on these fixtures.
    if a["parallel_calls"] > 0 and b["parallel_calls"] >= a["parallel_calls"]:
        print("\nEXHIBIT FAIL: second production did not reduce Parallel calls.",
              file=sys.stderr)
        return 3
    if b["corpus_hits"] < 1:
        print("\nEXHIBIT FAIL: zero corpus hits on Production B.", file=sys.stderr)
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
