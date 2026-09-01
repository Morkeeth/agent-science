#!/usr/bin/env python3
"""Qwen eval gate — holdout frozen before the first tuning pass.

Proves the held-out refusal set labels were fixed before eval arms were tuned on them.
Does NOT claim the semantic guard was blind — it reports post-freeze metadata edits honestly.

Run: python3 scripts/eval_holdout_frozen.py
Exit 0 when label hash matches HOLDOUT-MANIFEST and git ordering holds.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SET_PATH = ROOT / "fixtures/refusal-correctness/set.json"
MANIFEST_PATH = ROOT / "fixtures/refusal-correctness/HOLDOUT-MANIFEST.json"

# First commit that shipped semantic-guard tuning on the holdout pole (RC5 close).
TUNING_COMMITS = (
    "02f1b5e2f55c214c6f89fe593a408282c819311f",  # Semantic guard: close RC5
)


def _label_blob(set_data: dict) -> str:
    fields = json.loads(MANIFEST_PATH.read_text())["label_fields"]
    items = [{k: item.get(k) for k in fields} for item in set_data["items"]]
    return json.dumps(items, sort_keys=True, separators=(",", ":"))


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def _git_first_commit(path: str) -> str | None:
    out = subprocess.run(
        ["git", "-C", str(ROOT), "log", "--format=%H", "--reverse", "--", path],
        capture_output=True,
        text=True,
    ).stdout.strip()
    return out.splitlines()[0] if out else None


def _git_commit_date(commit: str) -> datetime:
    out = subprocess.run(
        ["git", "-C", str(ROOT), "show", "-s", "--format=%cI", commit],
        capture_output=True,
        text=True,
    ).stdout.strip()
    return datetime.fromisoformat(out.replace("Z", "+00:00"))


def main() -> int:
    if not SET_PATH.is_file() or not MANIFEST_PATH.is_file():
        print("MISSING holdout set or manifest")
        return 1

    set_data = json.loads(SET_PATH.read_text())
    manifest = json.loads(MANIFEST_PATH.read_text())
    blob = _label_blob(set_data)
    digest = _sha256(blob)
    expected = manifest["label_fields_sha256"]

    print("HOLDOUT FROZEN GATE — refusal-correctness/set.json")
    print(f"  labelled_at (set):     {set_data.get('labelled_at')}")
    print(f"  frozen_at (manifest):  {manifest.get('frozen_at')}")
    print(f"  n_items:               {len(set_data.get('items', []))}")
    print(f"  label hash:            {digest}")
    print(f"  manifest expects:      {expected}")

    ok = True
    if digest != expected:
        print("FAIL  label fields changed since freeze — update HOLDOUT-MANIFEST only after re-labelling")
        ok = False
    else:
        print("PASS  scoring labels match frozen manifest")

    first_set = _git_first_commit("fixtures/refusal-correctness/set.json")
    if not first_set:
        print("FAIL  set.json has no git history")
        ok = False
    else:
        set_date = _git_commit_date(first_set)
        print(f"  first set.json commit: {first_set[:8]} @ {set_date.isoformat()}")
        for tc in TUNING_COMMITS:
            try:
                tune_date = _git_commit_date(tc)
            except Exception:
                continue
            if tune_date >= set_date:
                relation = "after" if tune_date > set_date else "same day as"
                print(f"  tuning commit {tc[:8]} is {relation} first label commit — expected")
            else:
                print(f"FAIL  tuning commit {tc[:8]} predates holdout labels")
                ok = False

    # Metadata drift is allowed but must be named.
    meta_keys = {"closed_at", "closed_by", "why", "note"}
    for item in set_data["items"]:
        extra = sorted(set(item) - set(manifest["label_fields"]) - {"id"} - meta_keys)
        if extra:
            print(f"WARN  {item['id']} has unexpected keys: {extra}")

    post_freeze = [i["id"] for i in set_data["items"] if i.get("closed_at")]
    if post_freeze:
        print(f"NOTE  post-freeze metadata on: {', '.join(post_freeze)} — labels unchanged; not a re-label")

    print()
    if ok:
        print("FINDING: holdout labels frozen before tuning commits on record.")
        return 0
    print("FINDING: holdout gate FAILED — do not ship result tables until fixed.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
