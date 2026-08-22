"""Review-lane adversarial proposers — offline, no product edits.

Runs proposers the build suite may not cover. Exit 0 if all attacks behave as expected.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from clearance import facts, instruments, verify as V
from clearance.facts import Claim, judge_claim
from clearance.locate import StringLocator

INC_URL = "https://rightsstatements.org/vocab/InC/1.0/"
EUR_URL = "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32012L0028"
INC_CLAIM = Claim(
    "f", "An 'In Copyright' item requires permission",
    INC_URL, "you need to obtain permission from the rights-holder",
)


class _Loc:
    def __init__(self, name, fn):
        self.name, self._fn = name, fn

    def propose(self, *, claim, must_contain, document):
        return self._fn(document, must_contain)


def judged(fn, name="review", claim=None):
    return judge_claim(claim or INC_CLAIM, locator=_Loc(name, fn))


def main():
    fails = []

    def ok(label, cond, detail=""):
        if cond:
            print(f"  OK   {label}")
        else:
            print(f"  FAIL {label}  {detail}")
            fails.append(label)

    print("=== 1. Adversarial proposers (verifier + judge_claim path) ===\n")

    inc = instruments.document(INC_URL) or ""
    eur = instruments.document(EUR_URL) or ""

    # A. Paraphrase that changes a date — fluent, related, not verbatim
    def paraphrase_date(doc, mc):
        if "2012" in doc:
            return "Directive 2012/28/EU was adopted on 25 October 2013"
        return "The item was adopted on 25 October 2013"

    v = judged(paraphrase_date, "paraphrase-wrong-year", Claim(
        "d", "Directive 2012/28/EU was adopted on 25 October 2012", EUR_URL, "25 October 2012"))
    ok("paraphrase wrong year -> not GREEN",
       v.verdict != "GREEN" and "not_in_document" in v.reason, f"{v.verdict} {v.reason[:80]}")

    # B. Two non-adjacent fragments concatenated
    def concat_fragments(doc, mc):
        a = doc.find("permission")
        b = doc.find("rights-holder")
        if a < 0 or b < 0:
            return None
        if a > b:
            a, b = b, a
        return doc[a : b + len("rights-holder") + 40]

    v = judged(concat_fragments, "concat-fragments")
    ok("concat non-adjacent -> refused",
       v.verdict != "GREEN", f"{v.verdict}")

    # C. Whitespace cheat — normalize spaces in proposal
    def space_cheat(doc, mc):
        i = doc.find(mc)
        if i < 0:
            return None
        chunk = doc[i : i + 120]
        return chunk.replace("  ", " ")  # collapse double spaces if any

    v = judged(space_cheat, "space-normalize")
    ok("whitespace-normalized passage -> refused or exact match only",
       v.verdict != "GREEN" or (v.quoted_terms or "") in inc,
       f"{v.verdict}")

    # D. Negated sentence containing required terms
    def negated(doc, mc):
        return ("This Item is protected by copyright and you do NOT need to obtain "
                "permission from the rights-holder for any use.")

    v = judged(negated, "negated-with-terms")
    ok("negated sentence with terms -> not GREEN (must be verbatim in doc)",
       v.verdict != "GREEN", f"{v.verdict} {v.reason[:60]}")

    # E. Claim split across two sentences — passage spans two periods
    def two_sentences(doc, mc):
        p1 = doc.find("copyright")
        p2 = doc.find("permission", p1 + 1) if p1 >= 0 else -1
        if p1 < 0 or p2 < 0:
            return None
        return doc[p1 : p2 + 80]

    v = judged(two_sentences, "two-sentence-span")
    ok("multi-sentence span -> not GREEN unless verbatim block exists",
       v.verdict != "GREEN" or (v.quoted_terms or "") in inc,
       f"{v.verdict}")

    # F. Real passage from sibling document (EUR text on INC page)
    other = instruments.document("https://rightsstatements.org/vocab/CNE/1.0/") or ""
    idx = other.find("has not been evaluated")
    lifted = other[max(0, idx - 60) : idx + 80] if idx >= 0 else ""

    def sibling(doc, mc):
        return lifted if lifted else None

    v = judged(sibling, "sibling-doc")
    ok("sibling document passage -> refused",
       v.verdict != "GREEN" and "not_in_document" in v.reason,
       f"{v.verdict}")

    # G. Unicode homoglyph — if we can construct one
    if inc and "copyright" in inc:
        fake = inc.replace("copyright", "copyrigh\u0430t", 1)  # Cyrillic а
        if fake != inc and "copyrigh\u0431t" not in inc:
            r = V.verify(fake[inc.find("copy"): inc.find("copy") + 40],
                         document=inc, must_contain="copy")
            ok("unicode homoglyph in proposal -> verify refuses",
               r is not None and r.code == "not_in_document", str(r))

    # H. Verifier-only: passage is substring but must_contain only in second half
    if inc:
        i = inc.find("rights-holder")
        tail = inc[i : i + 200]
        r = V.verify(tail, document=inc, must_contain="you need to obtain permission")
        ok("passage missing must_contain terms -> does_not_carry_the_claim",
           r is not None and r.code == "does_not_carry_the_claim", str(r))

    # I. GeminiLocator structural — only if we can import without network
    print("\n=== 2. StringLocator known false GREEN (documented) ===\n")
    sloppy = Claim(
        "C3", "'Copyright Not Evaluated' means the holder never assessed the item",
        "https://rightsstatements.org/vocab/CNE/1.0/", "has not been evaluated")
    v = judge_claim(sloppy)  # default StringLocator
    ok("C3 sloppy claim on StringLocator — flagged if GREEN",
       True,  # informational
       f"verdict={v.verdict} (see docs/FINDING-substring-is-not-a-statement.md)")
    if v.verdict == "GREEN":
        print("       WARNING: FALSE GREEN still live on StringLocator for C3")

    print(f"\n=== {len(fails)} failure(s) ===")
    for f in fails:
        print(f"  - {f}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
