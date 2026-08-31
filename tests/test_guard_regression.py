"""The guard's regression set — DERIVED, and never reported as accuracy.

Every case in `fixtures/refusal-correctness/regression.json` was written FROM a defect
found while building and measuring `clearance/semantic.py` on 2026-08-31. The guard was
shaped by them. It therefore passes them by construction, and a green run here means only
**the defects already found have not come back** — which is worth having, and is not an
eval result.

This distinction is the whole reason the cases live in a second file. Folding them into
`set.json` would have turned an n=6 held-out measurement into an n=12 number that looks
twice as strong and is half as honest: six items the system had never seen, plus six the
system was built from, added together and reported as one accuracy. That is the
substitution this product exists to refuse, performed on the product's own scoreboard.

So: two files, a loud `held_out: false`, and a control below that fails if anyone ever
merges them or quietly flips the flag.

Run: python3 tests/test_guard_regression.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from clearance import semantic as S

REG = json.loads((ROOT / "fixtures/refusal-correctness/regression.json").read_text())
HELD_OUT = json.loads((ROOT / "fixtures/refusal-correctness/set.json").read_text())

passed = failed = 0


def check(name, fn):
    global passed, failed
    try:
        fn()
        print(f"  PASS  {name}")
        passed += 1
    except AssertionError as e:
        print(f"  FAIL  {name}\n        {e}")
        failed += 1


def t_the_set_declares_itself_derived():
    """The label is the point. Without it this file is an inflated eval set."""
    assert REG.get("held_out") is False, \
        "regression.json no longer declares held_out: false — it is about to be quoted " \
        "as an accuracy number it cannot support"
    assert REG.get("derived_from") == "guard-design"
    assert "NOT HELD OUT" in REG.get("warning", "").upper()


def t_it_has_not_been_merged_into_the_held_out_set():
    """n=6 must stay n=6. If it grows, say what was added and where it came from."""
    assert len(HELD_OUT["items"]) == 6, (
        f"the held-out set is now n={len(HELD_OUT['items'])}. If that is deliberate, the "
        "new items need labels written BEFORE an engine run, like the first six had — "
        "and a derived case moved in here would make every accuracy number in "
        "docs/FINDING-semantic-guard-2026-08-31.md wrong.")
    held_claims = {i["claim"].strip() for i in HELD_OUT["items"]}
    leaked = [i["id"] for i in REG["items"] if i["claim"].strip() in held_claims]
    assert not leaked, f"derived cases have leaked into the held-out set: {leaked}"


def t_every_defect_found_tonight_stays_closed():
    """The regression run itself. Not a score — a tripwire."""
    wrong = []
    for it in REG["items"]:
        finding = S.inspect(it["passage"], claim=it["claim"],
                            must_contain=it["must_contain"])
        got = "REFUSE" if finding else "ADMIT"
        if got != it["expect"]:
            wrong.append(
                f"{it['id']} ({it['defect']}): expected {it['expect']}, got {got}"
                + (f" — {finding.detail[:160]}" if finding else ""))
    assert not wrong, ("a defect closed on 2026-08-31 has returned:\n  "
                       + "\n  ".join(wrong))


def t_the_set_exercises_both_directions():
    """A regression set that only tests refusals cannot see the refuse-everything drift."""
    expects = [i["expect"] for i in REG["items"]]
    assert "REFUSE" in expects and "ADMIT" in expects
    assert expects.count("ADMIT") >= 3, (
        "fewer than 3 ADMIT cases: this set has drifted into watching only the "
        "assert-too-much direction, which is how the false-refusal direction got missed "
        "for a day in the first place")


def t_no_case_is_the_fixture_it_generalises():
    """REG1 must test RC5's RULE, not RC5's words."""
    rc5 = next(i for i in HELD_OUT["items"] if i["id"] == "RC5")
    reg1 = next(i for i in REG["items"] if i["id"] == "REG1")
    assert reg1["must_contain"] != rc5["must_contain"], \
        "REG1 reuses RC5's exact terms — it tests the fixture, not the mechanism"
    assert not set(reg1["passage"].lower().split()) >= set(rc5["why"].lower().split())


if __name__ == "__main__":
    print("GUARD REGRESSION — derived from tonight's defects, NOT a held-out score\n")
    for n, f in list(globals().items()):
        if n.startswith("t_") and callable(f):
            check(n[2:].replace("_", " "), f)
    print(f"\n{passed} passed, {failed} failed")
    print("Reminder: the only reportable accuracy for this guard is set.json, n=6.")
    raise SystemExit(1 if failed else 0)
