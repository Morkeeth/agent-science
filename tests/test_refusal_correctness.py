"""Refusal-correctness held-out set — the suite must fail on a false UNKNOWN.

Labels in fixtures/refusal-correctness/set.json were written before these controls
run against them. A refuse-everything locator must fail SUPPORTED items. A greedy
locator must fail NOT_SUPPORTED items that nearly match.

The load-bearing control is `t_shipping_locator_binds_both_poles_on_held_out_set`:
it runs the ACTUAL product locator (`DEFAULT`) over the set and fails on a false
UNKNOWN (a supported claim abstained on — the finding's own RC1 seed) as well as a
false GREEN, and cannot be satisfied by a stuck all-GREEN or all-UNKNOWN locator.
This mirrors the answerable/unanswerable split used by grounded-refusal benchmarks
(RefusalBench, AbstentionBench), which score over-abstention, not only hallucination.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from clearance import instruments, verify as V
from clearance.facts import Claim, judge_claim
from clearance.locate import DEFAULT
from clearance.verdict import GREEN, UNKNOWN

SET = json.loads((ROOT / "fixtures/refusal-correctness/set.json").read_text())


class _Loc:
    def __init__(self, name, fn):
        self.name, self._fn = name, fn

    def propose(self, *, claim, must_contain, document):
        return self._fn(document, must_contain)


def _doc(rel: str) -> str:
    return (ROOT / rel).read_text()


def _with_doc(url: str, body: str, claim: Claim, locator, **kw):
    saved = instruments.document

    def fake(u, fetch=False):
        if u == url:
            return body
        return saved(u, fetch=fetch)

    instruments.document = fake
    try:
        return judge_claim(claim, locator=locator, **kw)
    finally:
        instruments.document = saved


def t_refusal_set_labels_predate_the_run():
    assert SET["labelled_at"] and SET["labelled_by"]
    assert len(SET["items"]) >= 6


def t_accepted_passages_are_verbatim_in_their_documents():
    """The set is subject to its own product — labels cite a real span."""
    for it in SET["items"]:
        doc = _doc(it["document"])
        if it["expected"] == "SUPPORTED":
            p = it["accepted_passage"]
            assert p and p in doc, f"{it['id']}: accepted_passage not in document"
            assert it["must_contain"] in p
            assert V.verify(p, document=doc, must_contain=it["must_contain"]) is None, \
                f"{it['id']}: labelled passage fails the verifier"
        else:
            assert it["accepted_passage"] is None


def t_oracle_resolves_every_supported_item():
    """False UNKNOWN pole: labelled-SUPPORTED must be greenable somehow."""
    misses = []
    for it in SET["items"]:
        if it["expected"] != "SUPPORTED":
            continue
        passage = it["accepted_passage"]
        url = f"fixture://{it['id']}"
        loc = _Loc("labelled-oracle", lambda doc, mc, p=passage: p)
        v = _with_doc(url, _doc(it["document"]),
                      Claim(it["id"], it["claim"], url, it["must_contain"]), loc)
        if v.verdict != GREEN:
            misses.append(f"{it['id']}: {v.verdict}/{v.cause}")
    assert not misses, "false UNKNOWN on labelled-SUPPORTED:\n  " + "\n  ".join(misses)


def t_refuse_everything_fails_supported_pole_on_held_out_set():
    null = _Loc("always-null", lambda doc, mc: None)
    supported = [it for it in SET["items"] if it["expected"] == "SUPPORTED"]
    greens = 0
    for it in supported:
        url = f"fixture://null-{it['id']}"
        v = _with_doc(url, _doc(it["document"]),
                      Claim(it["id"], it["claim"], url, it["must_contain"]), null)
        if v.verdict == GREEN:
            greens += 1
    assert greens == 0
    # Oracle on same items is all GREEN — prove the suite can tell them apart.
    oracle_ok = 0
    for it in supported:
        p = it["accepted_passage"]
        url = f"fixture://ora-{it['id']}"
        v = _with_doc(url, _doc(it["document"]),
                      Claim(it["id"], it["claim"], url, it["must_contain"]),
                      _Loc("oracle", lambda doc, mc, pp=p: pp))
        if v.verdict == GREEN:
            oracle_ok += 1
    assert oracle_ok == len(supported)
    assert oracle_ok > greens


def t_near_miss_and_wrong_doc_must_stay_unknown():
    """Assert-too-much pole on the held-out set."""
    bad = []
    for it in SET["items"]:
        if it["expected"] != "NOT_SUPPORTED":
            continue
        # Skip items the engine provably CANNOT catch (substring-is-not-a-statement):
        # a greedy stand-in on those tests behaviour the system never promised, and this
        # loop used to "pass" RC5 only because the greedy slice happened to start
        # mid-word. The shipping-locator pole test below pins RC5 as the documented gap.
        if it.get("engine_limit"):   # none remain since 2026-08-31; kept for the next one
            continue

        def greedy(doc, mc):
            if "2020" in mc:
                return ("Member States shall bring into force the laws necessary "
                        "to comply with this Directive by 29 October 2020.")
            i = doc.find(mc)
            if i >= 0:
                return doc[max(0, i - 40): i + len(mc) + 80]
            return None

        url = f"fixture://bad-{it['id']}"
        v = _with_doc(url, _doc(it["document"]),
                      Claim(it["id"], it["claim"], url, it["must_contain"]),
                      _Loc("greedy", greedy))
        if v.verdict == GREEN:
            bad.append(f"{it['id']}: false GREEN — {v.quoted_terms!r}")
    assert not bad, "false GREEN on labelled-NOT_SUPPORTED:\n  " + "\n  ".join(bad)


def t_shipping_locator_binds_both_poles_on_held_out_set():
    """The whole point of the finding, on the ACTUAL product locator.

    Runs the shipping StringLocator (`DEFAULT`) over every item and binds both
    directions, so the suite fails when the product itself drifts — not only when a
    hand-made oracle or greedy stand-in does:

      * a catchable SUPPORTED item that abstains  -> FALSE UNKNOWN  -> RED here
      * a catchable NOT_SUPPORTED item that greens -> FALSE GREEN   -> RED here

    `engine_limit` items are exempted from the gold expectation and pinned separately
    below, because the system provably cannot read meaning (FINDING-substring-is-not-
    a-statement); pretending it can would be the very over-fitting this repo refuses.
    """
    results = {}
    for it in SET["items"]:
        url = f"fixture://ship-{it['id']}"
        v = _with_doc(url, _doc(it["document"]),
                      Claim(it["id"], it["claim"], url, it["must_contain"]), DEFAULT)
        results[it["id"]] = (v.verdict, v.cause)

    false_unknown, false_green = [], []
    for it in SET["items"]:
        if it.get("engine_limit"):
            continue
        verdict = results[it["id"]][0]
        if it["expected"] == "SUPPORTED" and verdict != GREEN:
            # RC1 lives here: the nav occurrence of "29 October 2014" precedes the real
            # sentence. A first-occurrence-only locator abstains — the exact defect the
            # finding was written about. This line turns that from "drift visible" into
            # "suite fails."
            false_unknown.append(f"{it['id']}: {results[it['id']]}")
        if it["expected"] == "NOT_SUPPORTED" and verdict == GREEN:
            false_green.append(f"{it['id']}: {results[it['id']]}")
    assert not false_unknown, \
        "FALSE UNKNOWN — shipping locator abstained on a supported claim:\n  " \
        + "\n  ".join(false_unknown)
    assert not false_green, \
        "FALSE GREEN — shipping locator cleared an unsupported claim:\n  " \
        + "\n  ".join(false_green)

    # Neither pole is satisfiable by a stuck locator: SUPPORTED greens and
    # NOT_SUPPORTED abstains on the SAME engine in the SAME run.
    catchable = [it for it in SET["items"] if not it.get("engine_limit")]
    greens = sum(results[it["id"]][0] == GREEN for it in catchable
                 if it["expected"] == "SUPPORTED")
    unknowns = sum(results[it["id"]][0] == UNKNOWN for it in catchable
                   if it["expected"] == "NOT_SUPPORTED")
    assert greens > 0 and unknowns > 0, \
        "an all-GREEN or all-UNKNOWN locator would be caught by one of these poles"

    # RC5 WAS the documented, uncloseable gap — pinned as a defect from 2026-08-22 so a
    # locator that closed it would fail here with an instruction rather than have the win
    # pass unnoticed. It fired on 2026-08-31 and the instruction was carried out: RC5 is
    # enforced above like any other NOT_SUPPORTED item, and `engine_limit` is gone.
    #
    # What replaces it is the harder control. A closed gap is easy to un-close by
    # accident, and the flag that makes the old engine recoverable is exactly the lever
    # that would do it. So: assert the set carries NO engine limits, and assert that
    # turning the guard off REPRODUCES the false GREEN. If someone flips the default and
    # the hole quietly returns, the second half of this fails and names it.
    assert not [it for it in SET["items"] if it.get("engine_limit")], (
        "an engine_limit is back in the set — a claim the product cannot judge is being "
        "carried as a fixture note again; say which, and why it cannot be closed")

    rc5 = next(it for it in SET["items"] if it["id"] == "RC5")
    url = "fixture://guardoff-RC5"
    off = _with_doc(url, _doc(rc5["document"]),
                    Claim("RC5", rc5["claim"], url, rc5["must_contain"]), DEFAULT,
                    semantic=False)
    assert off.verdict == GREEN, (
        "with CLEARANCE_SEMANTIC_GUARD off, RC5 must reproduce the documented false "
        f"GREEN — got {off.verdict}. Either the flag no longer recovers the old engine, "
        "or something else changed and the guard is not the thing closing RC5.")
    assert results["RC5"][0] == UNKNOWN, \
        "the shipping default no longer refuses RC5 — the closed gap has reopened"


if __name__ == "__main__":
    failed = 0
    for name, fn in list(globals().items()):
        if name.startswith("t_") and callable(fn):
            try:
                fn()
                print(f"  PASS  {name}")
            except Exception as e:
                failed += 1
                print(f"  FAIL  {name}: {e}")
    print(f"\n{failed} failed" if failed else "\nall passed")
    raise SystemExit(failed)
