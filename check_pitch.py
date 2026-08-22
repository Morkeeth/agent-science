"""Run CLEARED's OWN pitch claims through the fact leg.

If the product cannot survive being pointed at its own marketing, it should not be
pointed at anyone else's script.
"""
from clearance.facts import Claim, judge_claim

CLAIMS = [
    Claim("C1", "The EU Orphan Works Directive is Directive 2012/28/EU",
          "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32012L0028",
          "2012/28/EU"),
    Claim("C2", "An 'In Copyright' item requires permission from the rights-holder",
          "https://rightsstatements.org/vocab/InC/1.0/",
          "you need to obtain permission from the rights-holder"),
    Claim("C3", "'Copyright Not Evaluated' means the holder never assessed the item",
          "https://rightsstatements.org/vocab/CNE/1.0/",
          "has not been evaluated"),
    Claim("C4", "The Orphan Works Directive permits commercial use by cultural institutions",
          "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32012L0028",
          "commercial use is permitted"),
    Claim("C5", "94% of film archives are unclearable for AI training",
          None, "94% of film archives"),
]

if __name__ == "__main__":
    import sys
    fetch = "--fetch" in sys.argv
    for c in CLAIMS:
        v = judge_claim(c, fetch=fetch)
        print(f"{v.verdict:<8} {c.claim_id}  {c.text[:64]}")
        print(f"         cause={v.cause}  {v.reason}")
        if v.citation_url:
            print(f"         cite : {v.citation_url}")
            print(f'         quote: "{(v.quoted_terms or "")[:150]}…"')
        print()
