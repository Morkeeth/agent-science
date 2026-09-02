"""Holdout freeze gate — labels cannot drift without a manifest commit."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from clearance import holdout as H  # noqa: E402


def test_the_holdout_matches_its_manifest():
    v = H.verify()
    assert v["ok"], (
        f"holdout drift: changed={v['changed']} — "
        "re-run scripts/freeze_holdout.py only if labels were deliberately revised"
    )
    assert v["n_items"] == 6
    assert v["labelled_at"] == "2026-08-22T21:30:00Z"


def test_eval_scripts_load_labels_through_the_holdout_gate():
    data = H.holdout_set()
    assert len(data["items"]) == 6
    assert data["labelled_at"] == "2026-08-22T21:30:00Z"
    # Every item must carry a human rationale — post-hoc tuning usually drops these.
    for item in data["items"]:
        assert item.get("why"), f"{item['id']} missing why"


def test_changing_a_label_moves_the_hash():
    """Watched RED shape: editing expected without re-freezing must fail verify()."""
    original = H.SET_PATH.read_text()
    try:
        data = json.loads(original)
        data["items"][0]["expected"] = "NOT_SUPPORTED"
        H.SET_PATH.write_text(json.dumps(data, indent=2))
        assert not H.verify()["ok"], "a label edit must fail the holdout gate"
    finally:
        H.SET_PATH.write_text(original)
        assert H.verify()["ok"], "restore left holdout dirty"


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items())
           if k.startswith("test_") and callable(v)]
    bad = 0
    for fn in fns:
        try:
            fn()
            print(f"PASS  {fn.__name__}")
        except AssertionError as e:
            bad += 1
            print(f"FAIL  {fn.__name__}: {e}")
    print(f"\n{len(fns) - bad}/{len(fns)} passed")
    sys.exit(1 if bad else 0)
