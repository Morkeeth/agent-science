"""ADVERSARIAL HELD-OUT PROBE for `cited_provision_differs` — labels written first.

Run: python3 scripts/probe_citation_heldout.py     (needs the document cache or network)

WHY IT EXISTS. The lane that shipped the check closed saying its evidence was n=2, one of
them the motivating case, because `research-corpus/` contains no provision-bearing claims
at all. This is the population that did not exist: claims that cite an Article, against a
real regulation, labelled before any run. It is NOT the gold set — `fixtures/refusal-
correctness/set.json` stays the only reportable accuracy for the guard as a whole. This
measures ONE mechanism's cost and recall on rows that can exercise it.
8 TRUE (anchor verbatim under the article the claim names — must stay SOURCED)
+ 3 FALSE near-misses (anchor verbatim under a DIFFERENT article — should be REFUSED).
"""
import sys
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[1]))
from clearance import semantic as S, instruments
from clearance.facts import Claim, judge_claim

URL = "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32024R1689"

CASES = [
 # id, expect, claim, must_contain
 ("T1","SOURCED",'Article 5 lists prohibited practices: "The following AI practices shall be prohibited"',
  "The following AI practices shall be prohibited"),
 ("T2","SOURCED",'Article 50 requires that "AI systems intended to interact directly with natural persons" be designed so people are informed',
  "AI systems intended to interact directly with natural persons"),
 ("T3","SOURCED",'Article 16 requires providers to "ensure that their high-risk AI systems are compliant with the requirements set out in Section 2"',
  "ensure that their high-risk AI systems are compliant with the requirements set out in Section 2"),
 ("T4","SOURCED",'Article 101 allows the Commission to impose on GPAI model providers "fines not exceeding 3 % of their annual total worldwide turnover"',
  "fines not exceeding 3 % of their annual total worldwide turnover"),
 ("T5","SOURCED",'Article 26 requires that "Deployers of high-risk AI systems shall take appropriate technical and organisational measures"',
  "Deployers of high-risk AI systems shall take appropriate technical and organisational measures"),
 ("T6","SOURCED",'Article 72 requires that "Providers shall establish and document a post-market monitoring system"',
  "Providers shall establish and document a post-market monitoring system"),
 ("T7","SOURCED",'Article 53 requires GPAI providers to "draw up and keep up-to-date the technical documentation of the model"',
  "draw up and keep up-to-date the technical documentation of the model"),
 ("T8","SOURCED",'Article 22 requires providers in third countries to "appoint an authorised representative"',
  "appoint an authorised representative"),
 # FALSE near-misses: the anchor is verbatim but belongs to a DIFFERENT provision
 ("F1","REFUSED",'Article 53 breaches are subject to "administrative fines of up to EUR 35 000 000"',
  "administrative fines of up to EUR 35 000 000"),
 ("F2","REFUSED",'Article 26 breaches are subject to "administrative fines of up to EUR 35 000 000"',
  "administrative fines of up to EUR 35 000 000"),
 ("F3","REFUSED",'Article 5 breaches attract "fines not exceeding 3 % of their annual total worldwide turnover"',
  "fines not exceeding 3 % of their annual total worldwide turnover"),
]

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
        for cid, expect, claim, mc in CASES:
            v = judge_claim(Claim(cid, claim, URL, mc), fetch=True)
            out[cid] = (v.verdict, v.refusal_code or "", (v.quoted_terms or "")[:110])
        return out
    finally:
        S.DEFAULT_CHECKS = saved

assert instruments.document(URL, fetch=True), "no document"
base = run(("polarity",))
ship = run(("polarity","citation"))
print(f"{'id':4} {'label':9} {'BASE':8} {'SHIPS':8} {'agrees?':8} code")
bad=[]
for cid, expect, claim, mc in CASES:
    b, sv = base[cid], ship[cid]
    got = "SOURCED" if sv[0]=="GREEN" else "REFUSED"
    ok = got==expect
    if not ok: bad.append((cid,expect,got,sv))
    print(f"{cid:4} {expect:9} {b[0]:8} {sv[0]:8} {'OK' if ok else 'WRONG':8} {sv[1]}")
print()
for cid,expect,got,sv in bad:
    print(f"  MISS {cid}: labelled {expect}, engine says {got}  code={sv[1]}")
    print(f"       span: {sv[2]}")
print(f"\nSHIPS correct {len(CASES)-len(bad)}/{len(CASES)}   "
      f"BASE correct {sum((('SOURCED' if base[c][0]=='GREEN' else 'REFUSED')==e) for c,e,_,_ in CASES)}/{len(CASES)}")
