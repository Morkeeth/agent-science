"""ADVERSARIAL HELD-OUT PROBE for `cited_provision_differs` — labels written first.

Run: python3 scripts/probe_citation_heldout.py     (needs the document cache or network)

WHY IT EXISTS. The lane that shipped the check closed saying its evidence was n=2, one of
them the motivating case, because `research-corpus/` contains no provision-bearing claims
at all. This is the population that did not exist: claims that cite an Article, against a
real regulation, labelled before any run. It is NOT the gold set — `fixtures/refusal-
correctness/set.json` stays the only reportable accuracy for the guard as a whole. This
measures ONE mechanism's cost and recall on rows that can exercise it.
SET A, n=11, labelled 2026-08-31 by the wave-4 adversarial pass, BEFORE any run:
  8 TRUE (anchor verbatim under the article the claim names — must stay SOURCED)
+ 3 FALSE near-misses (anchor verbatim under a DIFFERENT article — should be REFUSED).
SET A is reported UNCHANGED and separately, because SHIPS 9/11 vs BASE 7/11 is already
published on the front surface and in the FINDING. Growing a set is not a licence to
restate its old score.

SET B, n=12, added 2026-08-31 wave 5, labelled the same way and for a stated reason: SET A
priced the shape the gate CLOSES at n=3 and the shapes it CANNOT SEE at n=1, so the
boundary sentence rested on a single row. Every SET B label is derived from the fetched
document, not from memory: each case carries the article heading and the sentence the
anchor actually sits under (`why`), read out of the 590,271-character EUR-Lex text with
`scripts/`-external tooling before any arm was run. That discipline exists because the
withdrawn F4 case below was mislabelled by a human, not missed by the engine.

CATEGORIES, because one aggregate score hides the only thing this probe measures:
  true          correct citation. A refusal here is a FALSE REFUSAL and the cost that matters.
  false-number  the rival provision is named BY NUMBER in the carrier clause. THE SHAPE
                THE GATE CLOSES. Recall here is what "cited_provision_differs" means.
  false-words   the rival provision's subject is named in WORDS ("providers of
                general-purpose AI models"), so there is no numeral to conflict with.
                KNOWN HOLE. Every row here is expected to be missed until the mechanism
                changes; they are here to price the hole, not to be passed.
  false-annex   the provision is an Annex, and `semantic.provisions("Annex III") -> []`.
                KNOWN PARSER HOLE, same status.
  false-excl    NEW, found by building this set: the carrier clause names the claim's own
                article BY NUMBER **in order to exclude it** ("other than those laid down
                in Articles 5"). The gate sees the same numeral on both sides, finds no
                rival, and clears a claim the clause explicitly denies.
"""
import sys
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[1]))
from clearance import semantic as S, instruments
from clearance.facts import Claim, judge_claim

URL = "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32024R1689"

CASES = [
 # id, expect, claim, must_contain, category, why (the document evidence for the label)
 # ---------------------------------------------------------------- SET A (wave 4, n=11)
 ("T1","SOURCED",'Article 5 lists prohibited practices: "The following AI practices shall be prohibited"',
  "The following AI practices shall be prohibited", "true", "Article 5 Prohibited AI practices"),
 ("T2","SOURCED",'Article 50 requires that "AI systems intended to interact directly with natural persons" be designed so people are informed',
  "AI systems intended to interact directly with natural persons", "true", "Article 50 Transparency obligations"),
 ("T3","SOURCED",'Article 16 requires providers to "ensure that their high-risk AI systems are compliant with the requirements set out in Section 2"',
  "ensure that their high-risk AI systems are compliant with the requirements set out in Section 2", "true", "Article 16 Obligations of providers"),
 ("T4","SOURCED",'Article 101 allows the Commission to impose on GPAI model providers "fines not exceeding 3 % of their annual total worldwide turnover"',
  "fines not exceeding 3 % of their annual total worldwide turnover", "true", "Article 101 Fines for providers of general-purpose AI models"),
 ("T5","SOURCED",'Article 26 requires that "Deployers of high-risk AI systems shall take appropriate technical and organisational measures"',
  "Deployers of high-risk AI systems shall take appropriate technical and organisational measures", "true", "Article 26 Obligations of deployers"),
 ("T6","SOURCED",'Article 72 requires that "Providers shall establish and document a post-market monitoring system"',
  "Providers shall establish and document a post-market monitoring system", "true", "Article 72 Post-market monitoring"),
 ("T7","SOURCED",'Article 53 requires GPAI providers to "draw up and keep up-to-date the technical documentation of the model"',
  "draw up and keep up-to-date the technical documentation of the model", "true", "Article 53 Obligations for providers of GPAI models"),
 ("T8","SOURCED",'Article 22 requires providers in third countries to "appoint an authorised representative"',
  "appoint an authorised representative", "true", "Article 22 Authorised representatives"),
 ("F1","REFUSED",'Article 53 breaches are subject to "administrative fines of up to EUR 35 000 000"',
  "administrative fines of up to EUR 35 000 000", "false-number",
  "the anchor sits in Article 99(3), whose clause names Article 5 by number"),
 ("F2","REFUSED",'Article 26 breaches are subject to "administrative fines of up to EUR 35 000 000"',
  "administrative fines of up to EUR 35 000 000", "false-number",
  "the anchor sits in Article 99(3), whose clause names Article 5 by number"),
 ("F3","REFUSED",'Article 5 breaches attract "fines not exceeding 3 % of their annual total worldwide turnover"',
  "fines not exceeding 3 % of their annual total worldwide turnover", "false-words",
  "the anchor sits in Article 101(1), which names its subject as 'providers of "
  "general-purpose AI models' and carries no numeral"),
 # ------------------------------------------------- SET B (wave 5, n=12, same discipline)
 ("T9","SOURCED",'Article 4 requires providers and deployers to ensure "a sufficient level of AI literacy" of their staff',
  "a sufficient level of AI literacy", "true",
  "'Article 4 AI literacy Providers and deployers of AI systems shall take measures to "
  "ensure, to their best extent, a sufficient level of AI literacy of their staff'"),
 ("T10","SOURCED",'Article 12 requires that high-risk AI systems "technically allow for the automatic recording of events"',
  "technically allow for the automatic recording of events", "true",
  "'Article 12 Record-keeping 1. High-risk AI systems shall technically allow for the "
  "automatic recording of events (logs)'. An EARLIER occurrence sits in a recital with no "
  "article at all, so this row also exercises span selection, not only citation."),
 ("T11","SOURCED",'Article 14 requires high-risk AI systems to be designed so that "they can be effectively overseen by natural persons"',
  "they can be effectively overseen by natural persons", "true",
  "'Article 14 Human oversight 1. High-risk AI systems shall be designed and developed in "
  "such a way ... that they can be effectively overseen by natural persons'"),
 ("T12","SOURCED",'Article 5 breaches are "subject to administrative fines of up to EUR 35 000 000"',
  "shall be subject to administrative fines of up to EUR 35 000 000", "true",
  "Article 99(3): 'Non-compliance with the prohibition of the AI practices referred to in "
  "Article 5 shall be subject to administrative fines of up to EUR 35 000 000'. The "
  "sub-paragraph the claim needs, cited correctly — the true twin of WEDGE-1."),
 ("T13","SOURCED",'Article 88 gives the Commission "exclusive powers to supervise and enforce Chapter V"',
  "The Commission shall have exclusive powers to supervise and enforce Chapter V", "true",
  "'Article 88 Enforcement of the obligations of providers of general-purpose AI models "
  "1. The Commission shall have exclusive powers to supervise and enforce Chapter V'"),
 ("F5","REFUSED",'Article 31 breaches are subject to "administrative fines of up to EUR 35 000 000"',
  "administrative fines of up to EUR 35 000 000", "false-number",
  "Article 31 is a 99(4) provision at EUR 15M / 3 %; the anchor sits in 99(3), which "
  "names Article 5 by number"),
 ("F6","REFUSED",'Article 22 breaches are subject to "administrative fines of up to EUR 35 000 000"',
  "administrative fines of up to EUR 35 000 000", "false-number",
  "Article 22 is named at 99(4)(b) at EUR 15M / 3 %; the anchor sits in 99(3), which "
  "names Article 5 by number"),
 ("F7","REFUSED",'Article 99 sets fines for GPAI model providers "not exceeding 3 % of their annual total worldwide turnover"',
  "fines not exceeding 3 % of their annual total worldwide turnover", "false-words",
  "the anchor sits in Article 101(1), not Article 99, and 101(1) names its subject in "
  "words — a second row for the hole F3 found alone"),
 ("F8","REFUSED",'Article 16 breaches attract "fines not exceeding 3 % of their annual total worldwide turnover"',
  "fines not exceeding 3 % of their annual total worldwide turnover", "false-words",
  "Article 16 is a 99(4)(a) provision at EUR 15M / 3 %; the anchor sits in Article 101(1), "
  "about GPAI models, whose subject is named in words"),
 ("F9","REFUSED",'Article 5 breaches are subject to "administrative fines of up to EUR 15 000 000"',
  "administrative fines of up to EUR 15 000 000", "false-excl",
  "Article 99(4) reads 'other than those laid down in Articles 5' — it names Article 5 by "
  "number IN ORDER TO EXCLUDE IT. The gate sees the same numeral on both sides and finds "
  "no rival. Article 5 is the 35M / 7 % tier at 99(3)."),
 ("F10","REFUSED",'Annex I lists "AI systems intended to be used for the recruitment or selection of natural persons" as high-risk',
  "AI systems intended to be used for the recruitment or selection of natural persons", "false-annex",
  "the anchor is Annex III point 4(a) ('Employment, workers' management and access to "
  "self-employment'), not Annex I. semantic.provisions('Annex III') -> [], so neither "
  "side of the comparison has a provision to conflict."),
 ("T14","SOURCED",'Annex III lists "AI systems intended to be used for the recruitment or selection of natural persons" as high-risk',
  "AI systems intended to be used for the recruitment or selection of natural persons", "true",
  "the same anchor, cited to its real home — the control that stops F10 being scored as a "
  "win for a mechanism that simply refuses every annex claim"),
]

#: the population already published as SHIPS 9/11 vs BASE 7/11. Reported unchanged.
SET_A = {"T1","T2","T3","T4","T5","T6","T7","T8","F1","F2","F3"}

# THE HEADER'S OWN ARITHMETIC, CHECKED AGAINST THE ROWS (added 2026-08-31, adversarial
# pass). The docstring above said "SET B, n=11" while the list below carried twelve rows
# — T9-T14 and F5-F10 — so the file that grew the set to 23 could not add its own halves
# to 23. A prose count beside the data it describes is the defect this whole repo exists
# to catch; here it is checked rather than typed.
_SET_B = {c[0] for c in CASES} - SET_A
_DECLARED = {int(n) for n in __import__("re").findall(
    r"SET B, n=(\d+),", __doc__ or "")} | {int(n) for n in __import__("re").findall(
    r"SET A, n=(\d+),", __doc__ or "")}
assert {c[0] for c in CASES} >= SET_A, "SET_A names a row the case list does not have"
assert len(SET_A) == 11 and len(_SET_B) == 12 and len(CASES) == 23, (
    f"the sets no longer add up: SET A {len(SET_A)} + SET B {len(_SET_B)} "
    f"!= {len(CASES)} rows")
assert _DECLARED == {11, 12}, (
    f"the docstring declares set sizes {sorted(_DECLARED)}; the rows are "
    f"SET A {len(SET_A)}, SET B {len(_SET_B)}")

# A FOURTH FALSE CASE WAS WRITTEN AND WITHDRAWN, AND THE LABEL WAS MINE, NOT THE ENGINE'S.
#   F4  "Annex IV sets out the 'technical documentation referred to in Article 11(1)'
#        for GPAI models"           labelled REFUSED, engine says SOURCED
# The engine is right and the label was wrong: the span it returned IS Annex IV. It was
# written to demonstrate the roman-numeral blind spot and does not, because nothing in
# it conflicts. The blind spot is real and is demonstrated at the parser instead:
#   >>> semantic.provisions("Annex III")  ->  []
# Scoring a probe against a label I got wrong would be this repo's own founding defect,
# committed inside the probe built to find it.

def run(arm_checks):
    saved = S.DEFAULT_CHECKS
    S.DEFAULT_CHECKS = arm_checks
    try:
        out = {}
        for cid, expect, claim, mc, cat, why in CASES:
            v = judge_claim(Claim(cid, claim, URL, mc), fetch=True)
            out[cid] = (v.verdict, v.refusal_code or "", (v.quoted_terms or "")[:110])
        return out
    finally:
        S.DEFAULT_CHECKS = saved


assert instruments.document(URL, fetch=True), "no document"
base = run(("polarity",))
ship = run(("polarity", "citation"))

CAT_ENGLISH = {
    "true": "correct citation — a refusal here is a FALSE REFUSAL",
    "false-number": "rival named BY NUMBER — THE SHAPE THE GATE CLOSES",
    "false-words": "rival's subject named in WORDS — known hole",
    "false-annex": "provision is an Annex — known parser hole",
    "false-excl": "carrier names the claim's own article to EXCLUDE it — found by this set",
}

got = {c: ("SOURCED" if ship[c][0] == "GREEN" else "REFUSED") for c in ship}
got_b = {c: ("SOURCED" if base[c][0] == "GREEN" else "REFUSED") for c in base}

print(f"{'id':5} {'set':4} {'label':9} {'BASE':8} {'SHIPS':8} {'agrees?':8} {'category':13} code")
bad = []
for cid, expect, claim, mc, cat, why in CASES:
    ok = got[cid] == expect
    if not ok:
        bad.append((cid, expect, got[cid], ship[cid], cat, why))
    st = "A" if cid in SET_A else "B"
    print(f"{cid:5} {st:4} {expect:9} {base[cid][0]:8} {ship[cid][0]:8} "
          f"{'OK' if ok else 'WRONG':8} {cat:13} {ship[cid][1]}")

print("\nMISSES, each with the label's evidence in the document:")
for cid, expect, g, sv, cat, why in bad:
    print(f"  {cid}: labelled {expect}, engine says {g}   [{cat}]")
    print(f"     why the label: {why}")
    print(f"     span returned: {sv[2]}")

def score(ids):
    ids = [c for c in ids if c in got]
    s_ok = sum(got[c] == e for c, e, *_ in CASES if c in ids)
    b_ok = sum(got_b[c] == e for c, e, *_ in CASES if c in ids)
    return s_ok, b_ok, len(ids)

print("\n" + "=" * 78)
sa, ba, na = score(SET_A)
print(f"SET A (published wave 4, unchanged)   SHIPS {sa}/{na}   BASE {ba}/{na}")
sf, bf, nf = score([c for c, *_ in CASES])
print(f"FULL SET (A + B, labelled first)      SHIPS {sf}/{nf}   BASE {bf}/{nf}")

print("\nBY CATEGORY — one aggregate hides the only thing this measures:")
for cat, english in CAT_ENGLISH.items():
    ids = [c for c, e, cl, m, k, w in CASES if k == cat]
    if not ids:
        continue
    s_ok, b_ok, n = score(ids)
    print(f"  {cat:13} {s_ok}/{n} SHIPS · {b_ok}/{n} BASE   {english}")

# THE COST IS MARGINAL, NOT ABSOLUTE, AND THE FIRST VERSION OF THIS BLOCK GOT IT WRONG.
# It printed `nt - s_true` = 2, which counts every TRUE row SHIPS refuses — including T3,
# which BASE refuses too (`not_a_statement`, a locator failure that predates this check).
# The surface said 1 and the command the surface tells a reader to run said 2: a sentence
# contradicted by its own cited source, on the pair of sentences this product sells.
# The cost OF THIS CHECK is the rows it takes from BASE: correct under BASE, wrong under
# SHIPS. Both numbers are printed, because a reader reconciling them should not have to
# derive the difference.
print("\nTHE SENTENCE THIS PROBE LICENSES, and no stronger one:")
n_num = [c for c, e, cl, m, k, w in CASES if k == "false-number"]
s_num, b_num, _ = score(n_num)
n_true = [c for c, e, cl, m, k, w in CASES if k == "true"]
s_true, b_true, nt = score(n_true)
introduced = [c for c, e, cl, m, k, w in CASES
              if k == "true" and got_b[c] == e and got[c] != e]
both = [c for c, e, cl, m, k, w in CASES
        if k == "true" and got_b[c] != e and got[c] != e]
print(f"  It refuses THIS SHAPE of the error — a carrier clause naming a rival provision")
print(f"  by number: {s_num}/{len(n_num)} closed, against {b_num}/{len(n_num)} without the check,")
print(f"  at a cost of {len(introduced)} false refusal(s) INTRODUCED on {nt} correctly")
print(f"  cited claims {sorted(introduced)} — the rows BASE gets right and SHIPS gets wrong.")
print(f"  A further {len(both)} true row(s) {sorted(both)} are refused by BOTH arms and are")
print(f"  NOT this check's cost: {nt - s_true} of {nt} refused under SHIPS in total.")
print(f"  It does not see a rival named in words, an Annex, or an exclusion clause.")
