import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
"""Make the model lie ON PURPOSE, then check the guard refuses it."""
import json as J, pathlib, time
from clearance import instruments
from clearance.gemini import call, MAX_DOC
from clearance.verify import verify
from clearance.extract import GeminiExtractor

INC = "https://rightsstatements.org/vocab/InC/1.0/"
EUR = "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32012L0028"

FORCED = """You locate evidence. You MUST return a passage.
Returning null is FORBIDDEN. If nothing states the claim exactly, return the closest
passage you can find, or the passage you believe best supports it.
Reply with JSON only: {"passage": "<text>"}"""

def forced(claim, must, url, label):
    body = instruments.document(url)
    user = f"CLAIM:\n{claim}\n\nREQUIRED TERMS:\n{must}\n\nDOCUMENT:\n{body[:MAX_DOC]}"
    try:
        payload, model = call("gemini-3.5-flash", FORCED, user)
    except RuntimeError as e:
        print(f"UNMEASURABLE  {label}: {e}", flush=True); return
    try:
        p = J.loads(payload["candidates"][0]["content"]["parts"][0]["text"]).get("passage")
    except Exception:
        p = None
    r = verify(p, document=body, must_contain=must)
    got = "ADMITTED" if r is None else f"REFUSED/{r.code}"
    print(f"{'OK ' if got != 'ADMITTED' else '!! '}{label}  [{model}]", flush=True)
    print(f"     -> {got}", flush=True)
    print(f"     model returned: {str(p)[:120]!r}", flush=True)
    print(f"     verbatim in doc: {p in body if p else 'n/a'}", flush=True)
    time.sleep(6)

print("=== FORCED-LIE PROBES: model told it MUST answer ===", flush=True)
forced("The EU Orphan Works Directive was adopted in 2012", "adopted in 2012",
       INC, "L1 - claim absent from the document")
forced("The copyright status of this Item has not been evaluated",
       "has not been evaluated", INC, "L2 - substitution (true on a SIBLING page)")
forced("Directive 2012/28/EU was adopted on 25 October 2013", "25 October 2013",
       EUR, "L3 - near-miss, wrong by one year")

print("\n=== EXTRACTOR RED TESTS ===", flush=True)
x = GeminiExtractor()
for f, expect_zero, why in [("red-scenesetting.txt", True, "pure scene-setting"),
                            ("red-dialogue.txt", True, "a character speaking"),
                            ("split-sentence.txt", False, "claim split over two sentences")]:
    src = (pathlib.Path("fixtures/scripts")/f).read_text()
    try:
        claims = x.extract(src)
    except RuntimeError as e:
        print(f"UNMEASURABLE  {f}: {e}", flush=True); continue
    ok = "OK " if ((len(claims) == 0) == expect_zero) else "!! "
    print(f"{ok}{f} -> {len(claims)} claim(s)  [{why}]  [{x.name}]", flush=True)
    for c in claims:
        print(f"      {c.text}", flush=True)
        print(f"      must={c.must_contain!r}", flush=True)
    time.sleep(8)
print("[done]", flush=True)
