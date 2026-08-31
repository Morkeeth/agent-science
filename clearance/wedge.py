"""THE WEDGE — the one refusal a stranger has to meet in the first ten seconds.

It is not a story about the product. It is a defect that was live in this engine at
04:40 on 2026-08-31, found by running it, and closed the same hour.

    claim    Article 50 transparency breaches are subject to
             "administrative fines of up to EUR 35 000 000"
    verdict  GREEN
    span     "Non-compliance with the prohibition of the AI practices referred to in
              Article 5 shall be subject to administrative fines of up to EUR
              35 000 000 or, if the offender is an undertaking, up to 7 % of its
              total worldwide annual turnover ..."

Every property a grounded answer is supposed to have, this span has. It is verbatim. It
is in the document the claim cites. It carries 73 % of the claim's content terms. It is
the operative sentence of a real penalties provision, not page furniture. A citation
checker returns it with a URL and a green tick.

It is about **Article 5**. The claim is about **Article 50**. Article 50 is reached by
Article 99(4)(g) and its tier is EUR 15 000 000 / 3 %. The two numbers on the page are
both real; the sentence joining them is false, and the difference is EUR 20 000 000.

WHY NOTHING IN THE ENGINE COULD SEE IT. A provision citation is two tokens that mean
one thing, and every similarity path in the guard splits them and then drops the number:
`content()` filters tokens of length 1, so the "5" in "Article 5" does not survive
tokenisation at all. What is left is `article`, and `article` matches `article`. The
check was not too weak. It was reading the wrong object.

WHAT THIS MODULE IS. Inputs, provenance, and a labelled reading — the claim, the source,
the anchor, what the answer should be, and `Case.note`, a hand-written reading of the
instrument. It holds NO ENGINE OUTPUT: no verdict the engine returned, no span it
selected, no coverage it measured. Those are produced by `scripts/wedge_receipt.py`
running the shipping engine against the fetched document, and the surface renders that
receipt. `Case.note` is the boundary, and `PROVENANCE` names it on the page. Writing the outcome down here and
rendering it as though the engine had said it is the exact failure this product sells
against, and it would be committed inside the exhibit that sells it.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

# Regulation (EU) 2024/1689 (the AI Act), consolidated text, EUR-Lex. Chosen because the
# claim under it is one an intelligent person actually makes: the 35M/7% tier is the
# headline number in every summary of this instrument, and attaching it to the wrong
# article is the single most common error written about it. The error is in this repo's
# own research corpus (research-corpus/2026-08-24-verification-stack-positioning.md
# attaches "fines to EUR 35M or 7%" to the high-risk obligations of Articles 8-17, 26,
# 27 and 73, which are Article 99(4) provisions at EUR 15M / 3%).
URL = "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32024R1689"
INSTRUMENT = "Regulation (EU) 2024/1689 — the EU AI Act"

RECEIPT = Path(__file__).resolve().parent.parent / "fixtures/wedge/receipt.json"
COMMAND = "python3 scripts/wedge_receipt.py"


@dataclass(frozen=True)
class Case:
    case_id: str
    claim: str
    must_contain: str
    expect: str          # SOURCED | REFUSED — the labelled answer, written before the run
    note: str


# BOTH DIRECTIONS. A gate that only ever refuses is not a gate, it is a switch, and the
# second case is what stops this exhibit from being one: the same desk, the same article,
# the same anchor shape, and it clears — because that claim is true.
CASES = (
    Case("WEDGE-1",
         'Article 50 transparency breaches are subject to "administrative fines of up '
         'to EUR 35 000 000"',
         "administrative fines of up to EUR 35 000 000",
         "REFUSED",
         "False. 35M/7% is the Article 5 tier. The span that carries the anchor is "
         "Article 99(3), which is about Article 5 and never mentions Article 50."),
    Case("WEDGE-2",
         'Article 50 transparency breaches are subject to "administrative fines of up '
         'to EUR 15 000 000"',
         "administrative fines of up to EUR 15 000 000",
         "SOURCED",
         "True. Article 99(4) sets EUR 15 000 000 / 3 % and reaches Article 50 at "
         "point (g). The same mechanism must let this one through."),
)

# "NOTHING ON THIS PAGE IS WRITTEN BY HAND" WAS FALSE, ON THE ONE PAGE THAT MAY NOT
# PRINT A FALSE SENTENCE. Every verdict, span, refusal code and coverage figure IS
# engine output — but `Case.note` renders beside each reading and makes a substantive
# assertion about the instrument ("Article 99(4) sets EUR 15 000 000 / 3 % and reaches
# Article 50 at point (g)"), and so does the sentence `_wedge_html` appends after it.
# Both are true. The sentence claiming neither existed was not, and an absolute claim
# about provenance is the one a reader checks. Corrected 2026-08-31 by an adversarial
# pass; pinned by `t_the_provenance_line_does_not_overclaim`.
PROVENANCE = (
    f"Produced by `{COMMAND}` running the shipping engine (clearance.facts.judge_claim) "
    f"against {INSTRUMENT}, fetched live from EUR-Lex. Every verdict, span, refusal code "
    "and coverage figure below is the engine's output, read from that receipt: this page "
    "cannot print a verdict the engine did not produce. The reading of the instrument in "
    "the note beside each row is written by hand, and it is the only thing here that is. "
    "BASE is the engine with the citation check off, which is exactly the engine that "
    "shipped at 04:00 on 2026-08-31."
)

# What a keyword-grounded answer would have done with WEDGE-1, stated as a property of
# the span rather than as an insult to a competitor: it is verbatim, it is in the cited
# document, and it carries most of the claim's content terms. Those are the three tests
# a retrieval-with-citations product applies, and this span passes all three.
KEYWORD_GROUNDER_PASSES = (
    "verbatim in the fetched document",
    "contains the claim's distinctive anchor",
    "carries most of the claim's content terms",
)


def receipt() -> dict | None:
    """The engine's own output, or None. NEVER a fallback to a written-down answer."""
    import json
    if not RECEIPT.exists():
        return None
    try:
        return json.loads(RECEIPT.read_text())
    except (ValueError, OSError):
        return None
