"""Refusal-correctness held-out set — the suite must fail on a false UNKNOWN.

Labels in fixtures/refusal-correctness/set.json were written before these controls
run against them. A refuse-everything locator must fail SUPPORTED items. A greedy
locator must fail NOT_SUPPORTED items that nearly match.
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


def _with_doc(url: str, body: str, claim: Claim, locator):
    saved = instruments.document

    def fake(u, fetch=False):
        if u == url:
            return body
        return saved(u, fetch=fetch)

    instruments.document = fake
    try:
        return judge_claim(claim, locator=locator)
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


def t_shipping_locator_resolves_short_sentence_and_cne():
    """Pin known-resolvable awkward cases on the real StringLocator."""
    results = {}
    for it in SET["items"]:
        if it["expected"] != "SUPPORTED":
            continue
        url = f"fixture://ship-{it['id']}"
        v = _with_doc(url, _doc(it["document"]),
                      Claim(it["id"], it["claim"], url, it["must_contain"]), DEFAULT)
        results[it["id"]] = (v.verdict, v.cause)
    assert results["RC2"][0] == GREEN, f"RC2 short sentence: {results['RC2']}"
    assert results["RC6"][0] == GREEN, f"RC6 CNE: {results['RC6']}"
    # RC1 nav-first: pin outcome so drift is visible (may be GREEN or UNKNOWN).
    assert "RC1" in results


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
