"""The measurement population — frozen, hashed, and separate from where the product writes.

WHY THIS FILE EXISTS. Until 2026-08-31 the eval replayed `research-corpus/` and
`clearance/ingest.py` WROTE dated claim files into `research-corpus/`. The published
denominator therefore moved every time anyone used the product: the night of 08-30 read
n=313, then n=314 an hour later because a parallel lane had ingested a claim, and from a
clean checkout the same command reads 312 because two of those files were never
committed. A number whose population is a live write target is not a measurement.

Oscar's standing law: **bind tests live, pin baselines — a live baseline silently becomes
the treatment.** So:

    research-corpus/   FROZEN. Committed, hashed in MANIFEST.json, replayed by the evals.
                       Nothing in the product writes here. Growing it is a deliberate,
                       reviewed act: add the files, re-run scripts/freeze_population.py,
                       commit the new manifest, and every published number moves ON PURPOSE.
    research-inbox/    LIVE. Where `clearance.ingest` writes. Audit trail for claims the
                       product ingests at runtime. Never enters a published denominator.

The manifest is generated from `git ls-files`, so it can only ever freeze committed
content — which is the property the reproducibility defect was about.

    frozen_dir()          -> absolute path, AFTER verifying the directory still matches
                             the manifest. Raises PopulationError, loudly, otherwise.
    verify()              -> the full diff (missing / extra / changed) without raising.

FAILS LOUD, NEVER EMPTY. `clear_corpus.parse_corpus` returns [] for a directory that is
not there, and "research-corpus" as a bare relative string resolves against the caller's
cwd — so a run from the wrong directory would have measured a population of zero and
printed a confident 0/0. Both are closed here: the path is resolved from the repo root
and an empty or mismatched population is an exception, not a number.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

#: The frozen measurement population. Read by the evals. Written by nobody.
FROZEN = ROOT / "research-corpus"
#: The live sink. Written by `clearance.ingest`. Read by no published number.
INBOX = ROOT / "research-inbox"
MANIFEST = FROZEN / "MANIFEST.json"


class PopulationError(RuntimeError):
    """The measurement population is not the one the manifest pins."""


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _members(directory: Path) -> dict[str, Path]:
    if not directory.is_dir():
        return {}
    return {p.name: p for p in sorted(directory.glob("*.md"))}


def manifest() -> dict:
    if not MANIFEST.is_file():
        raise PopulationError(
            f"no frozen manifest at {MANIFEST.relative_to(ROOT)} — run "
            f"`python3 scripts/freeze_population.py` and commit it")
    return json.loads(MANIFEST.read_text())


def verify() -> dict:
    """Compare the directory on disk against the frozen manifest. Never raises."""
    m = manifest()
    pinned = {f["file"]: f["sha256"] for f in m["files"]}
    present = _members(FROZEN)
    missing = sorted(set(pinned) - set(present))
    extra = sorted(set(present) - set(pinned))
    changed = sorted(n for n in set(pinned) & set(present)
                     if sha256(present[n]) != pinned[n])
    return {"ok": not (missing or extra or changed), "frozen_at": m["frozen_at"],
            "n_files": len(pinned), "claims": m["claims"],
            "missing": missing, "extra": extra, "changed": changed}


def frozen_dir() -> str:
    """The population every published number is computed over — or a loud failure.

    Returns an absolute path so no caller's cwd can silently substitute another
    directory (or no directory, which `parse_corpus` would have reported as zero claims).
    """
    v = verify()
    if not v["ok"]:
        raise PopulationError(
            "the frozen measurement population no longer matches its manifest — "
            "a published denominator would move:\n"
            f"  missing: {v['missing'] or 'none'}\n"
            f"  extra  : {v['extra'] or 'none'}  "
            "(ingest writes to research-inbox/, never here)\n"
            f"  changed: {v['changed'] or 'none'}\n"
            "Deliberate? re-run scripts/freeze_population.py and commit the manifest.")
    if not v["n_files"]:
        raise PopulationError("the frozen population is empty")
    return str(FROZEN)
