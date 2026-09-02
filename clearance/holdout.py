"""The refusal-correctness holdout — frozen before any tuning pass.

`fixtures/refusal-correctness/set.json` was labelled 2026-08-22, before engine runs on
these items. The manifest pins that file by hash so a post-hoc label edit cannot move
the denominator without a deliberate, reviewed act.

    holdout_set()   -> parsed set dict, AFTER verifying the file still matches the manifest.
    verify()        -> diff dict without raising.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOLDOUT_DIR = ROOT / "fixtures/refusal-correctness"
SET_PATH = HOLDOUT_DIR / "set.json"
MANIFEST = HOLDOUT_DIR / "MANIFEST.json"


class HoldoutError(RuntimeError):
    """The holdout set is not the one the manifest pins."""


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def manifest() -> dict:
    if not MANIFEST.is_file():
        raise HoldoutError(
            f"no holdout manifest at {MANIFEST.relative_to(ROOT)} — run "
            f"`python3 scripts/freeze_holdout.py` and commit it")
    return json.loads(MANIFEST.read_text())


def verify() -> dict:
    """Compare set.json on disk against the frozen manifest. Never raises."""
    m = manifest()
    pinned = m["set"]["sha256"]
    if not SET_PATH.is_file():
        return {"ok": False, "frozen_at": m.get("frozen_at"), "n_items": m.get("n_items"),
                "changed": ["set.json missing"], "missing": [], "extra": []}
    actual = sha256(SET_PATH)
    changed = [] if actual == pinned else ["set.json"]
    return {"ok": not changed, "frozen_at": m["frozen_at"], "labelled_at": m["labelled_at"],
            "n_items": m["n_items"], "missing": [], "extra": [], "changed": changed}


def holdout_set() -> dict:
    """The labelled holdout — or a loud failure if it drifted."""
    v = verify()
    if not v["ok"]:
        raise HoldoutError(
            "the refusal-correctness holdout no longer matches its manifest — "
            "labels may have been tuned post-hoc:\n"
            f"  changed: {v['changed'] or 'none'}\n"
            "Deliberate? re-run scripts/freeze_holdout.py and commit the manifest.")
    return json.loads(SET_PATH.read_text())
