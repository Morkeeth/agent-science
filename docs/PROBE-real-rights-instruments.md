---
date: 2026-08-22
project: CLEARED
probe: does a REAL, publicly-fetchable, asset-level rights instrument exist?
answer: YES — at scale, on real film-archive material
status: kill condition DOES NOT FIRE
---

# PROBE — the kill condition tested against the object

## The gate being tested
`github.com/Morkeeth/agent-science/ORIENT.md`, verbatim:
> *"If the only way to demo a RED rights verdict is an **invented contract**, the demo is wrong.
> Fabricated evidence inside an evidence-not-claims pitch is the crack a judge pushes on."*

Correct, and fatal to CLEARED **if** no real instrument exists. It does exist.

## THE ARTIFACT — one real asset, one real instrument, both fetchable now

| | |
|---|---|
| Asset | **"The Film Archive in Berlin"** |
| Holder | Deutsche Welle (Germany), via EUscreenXL |
| Asset URL | https://www.europeana.eu/item/2051904/data_euscreenXL_1252769 |
| Record ID | `/2051904/data_euscreenXL_1252769` |
| **Rights instrument** | `http://rightsstatements.org/vocab/InC/1.0/` |

The instrument's own terms, fetched from `rightsstatements.org` (HTTP 200):
> *"This Item is protected by copyright and/or related rights. You are free to use this Item in any
> way that is permitted by the copyright and related rights legislation that applies to your use.
> **For other uses you need to obtain permission from the rights-holder(s).**"*

**→ Query: "shots we can license for AI training in the EU."
→ Verdict: RED. Reason: In Copyright, no permission granted for this use, rights-holder Deutsche
Welle must be approached. Cited to a live URL. Nothing invented.**

## IT IS NOT ONE ITEM — it is a machine-readable vocabulary at archive scale
Europeana API, query `film archive`, 50 real items. Six distinct real instruments returned:

| Instrument | n | Verdict for "license for AI training / commercial" |
|---|---|---|
| `rightsstatements.org/vocab/InC/1.0/` | 36 | **RED** — in copyright, permission required |
| `creativecommons.org/publicdomain/mark/1.0/` | 6 | **GREEN** |
| `creativecommons.org/licenses/by-nd/4.0/` | 4 | **RED** — no derivatives |
| `rightsstatements.org/vocab/InC-EDU/1.0/` | 2 | **RED** — educational use only |
| `creativecommons.org/licenses/by-nc/4.0/` | 1 | **RED** — non-commercial |
| `creativecommons.org/licenses/by-nc-sa/4.0/` | 1 | **RED** — non-commercial |

Corpus size behind it: **2,094,079** items on `film`. `rightsstatements.org` is the standard
vocabulary used by Europeana and DPLA — 12 statements, versioned, dereferenceable, each with terms.

## What this changes
- The RED verdict runs on **real instruments with citable URLs**. The kill condition does not fire.
- **The gap report writes itself from real data:** 36/50 = **72% of a real European film-archive
  sample is In Copyright, i.e. unclearable as-is.** That is CLEARED's step-6 upsell, measured, not
  asserted.
- What is still NOT public: the underlying **contracts** (term, territory, expiry, music beds).
  So CLEARED's honest v1 shape = **real public instruments as the spine**, plus contract ingest as
  the enterprise path, and the product prints UNKNOWN where no instrument exists — never a guess.

## Reproduce
```bash
curl -s "https://api.europeana.eu/record/v2/search.json?wskey=api2demo&query=film+archive&rows=50&profile=rich" \
  | python3 -c "import json,sys,collections;print(collections.Counter(r for i in json.load(sys.stdin)['items'] for r in (i.get('rights') or ['<none>'])))"
```
`api2demo` is Europeana's public demo key — fine for a probe, get a real key for the build.
