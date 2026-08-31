"""Deterministic routing — skip Parallel when the primary URL is known."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from clearance import routing


def t_celex_from_directive_number():
    c = routing.candidates_for(
        text="The Orphan Works Directive is Directive 2012/28/EU.",
        must_contain="2012/28/EU",
    )
    assert c, "expected CELEX route"
    assert "32012L0028" in c[0].url or "32012L0028" in c[0].url.upper()


def t_rights_vocab_code():
    c = routing.candidates_for(
        text="Copyright was never evaluated for this item",
        must_contain="CNE",
    )
    assert any("rightsstatements.org/vocab/CNE" in x.url for x in c)


def t_arxiv_id():
    c = routing.candidates_for(
        text="FaithCoT-Bench is described in arXiv:2503.03750",
        must_contain="2503.03750",
    )
    assert c and "arxiv.org/abs/2503.03750" in c[0].url


def t_empty_for_vague_claim():
    assert not routing.candidates_for(text="something happened in 2019", must_contain="")


if __name__ == "__main__":
    for fn in (t_celex_from_directive_number, t_rights_vocab_code,
               t_arxiv_id, t_empty_for_vague_claim):
        fn()
        print(f"PASS  {fn.__name__}")
    print("\n4/4 passed")
