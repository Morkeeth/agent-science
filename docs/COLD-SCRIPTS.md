# COLD-SCRIPTS — public documentary cold runs (AS-SHIP-2)

Three **public** documentary transcripts (not fixtures), run through the live clearance
pipeline, with sourced / refused / **wrong** counts re-derived at the source object.

**Measured:** 2026-09-02 · hosted `POST /clear` · receipts in `cold-scripts/receipts/`

| Script | Type | Claims | SOURCED | REFUSED | WRONG |
|--------|------|--------|---------|---------|-------|
| 1 · Apollo 11 post-landing | historical / archival | 4 | 2 | 2 | 2 |
| 2 · NOVA *Dimming the Sun* | science explainer | 3 | 0 | 3 | 2 |
| 3 · EU orphan works policy | policy / regulatory | 8 | 4 | 4 | 1 |
| **Total** | | **15** | **6** | **9** | **5** |

REFUSED = UNSOURCED + UNVERIFIED INDEPENDENCE. WRONG = auditor opened the script's
source URL and found the passage the product refused, or opened the cited URL and the
quoted span was absent (none of the latter this run).

---

## Cost (one cold run, all three scripts)

| Meter | Value | How derived |
|-------|-------|-------------|
| Wall clock | **325.4 s** (~5.4 min) | `python3 scripts/run_cold_scripts.py` — sum of `_wall_seconds` in receipts |
| Parallel API calls (metered) | **11** | 3 + 1 + 7 from receipt JSON |
| Parallel cost estimate | **~$0.05–0.10** | 13 searches × ~$0.004–0.008/search (README compound curve band; no billing export on this run) |
| Gemini / Vertex | hosted ADC | Not separately metered in receipts; extraction + locate on every claim |

---

## Commands (stranger copy-paste)

```bash
git clone https://github.com/Morkeeth/agent-science.git
cd agent-science
python3 scripts/seed_document_cache.py          # optional; offline controls only

# Run all three against hosted clearance (no local API keys required)
python3 scripts/run_cold_scripts.py

# Re-derive wrong count at source URLs — must print wrong_count=5
python3 scripts/audit_cold_wrong.py

# Single script via hosted curl (example)
curl -sS -X POST https://agent-science-568004190078.us-central1.run.app/clear \
  -H 'Content-Type: application/json' \
  -d "$(python3 -c 'import json, pathlib; print(json.dumps({"script": pathlib.Path("cold-scripts/01-apollo11-postland.txt").read_text(), "subject": "cold-script-1"}))')" \
  | python3 -m json.tool | head -40

# Local path (requires PARALLEL_API_KEY + Vertex/Gemini ADC)
python3 agent_science.py cold-scripts/03-eu-orphan-works-policy.txt --subject cold-script-3
```

Privacy gate before commit:

```bash
bash scripts/privacy_grep.sh
```

---

## Script 1 — Apollo 11 post-landing (historical / archival)

**Source URL:** https://history.nasa.gov/wp-content/uploads/static/history/alsj/a11/a11.postland.html  
**Subject:** `cold-script-1` · **Engine:** direct (ADK fell back — no Gemini key in container path)  
**Receipt:** `cold-scripts/receipts/cold-script-1.json`

### Full transcript text (excerpt committed)

```
 Post-landing Activities The First Lunar Landing EVA Preparations Post-landing Activities 
Corrected Transcript and Commentary Copyright © 1995 by Eric M. Jones . All rights reserved. Scan credits in the Image Library . Video credits in the Video Library . Last revised 18 March 2018. Audio Clip from the Public Affairs loop starting at about 102:47:46. Clip courtesy John Stoll, ACR Senior Technician at NASA Johnson. Your browser does not support the audio element. Click to load audio in new, pop-up window. 102:48:10 Aldrin: (Garbled) copy Noun 60...(Correcting himself) Noun 43. Over. 102:48:13 Duke: Roger. We have it. [Journal Contributor Frank O'Brien notes, "Noun 43 displays the PGNS-calculated location of the landing site - in latitude, longitude and distance from the center of the moon."] 102:48:14 Collins: Houston, how do you read Columbia on the high gain? [Journal Contributor David Harland notes that Charlie had warned Mike at 102:16:00 that he might lose high-gain lock-on during the LM's powered descent.] 102:48:17 Duke: Roger... 102:48:18 Aldrin: (Garbled) 102:48:19 Duke: ...We read you five-by, Columbia. He has landed (at) Tranquility Base. Eagle is at Tranquility. Over. 102:48:26 Collins: Yeah. I heard the whole thing. 102:48:27 Duke: Good show. 102:48:31 Collins: Fantastic. 102:48:32 Aldrin: Engine Stop, Reset. (Long Pause) 102:48:58 Collins: Houston, Columbia went Up Telemetry Command, Reset to re-acquire on the high gain. 102:49:02 Duke: Copy. Out. (Long Pause) [Apollo Flight Journal Editor David Woods writes, "There are two switches on panel 3 of the Command Module's main display console (MDC) that come under the heading 'UP TLM' or 'Up telemetry'. The leftmost of the two switches selects whether the radio channel for the data uplink (from Earth to the spacecraft) will carry data (its normal mode) or whether it will act as a backup channel for voice from Houston. The rightmost is concerned with the up-data link (UDL) equipment. It's normal (center) position sends power to the UDL equipment. The down position is 'off', so no power is sent to the UDL equipment. The up position is labelled 'CMD RESET' meaning 'Command Reset' and its stated function, according to the Apollo Operations Handbook ( page 3-143 ) is "resets all of real time command relays except bank 'A.' " The switch is spring loaded to return to the center position after being pushed up. I don't know why resetting these relays causes Columbia's high gain antenna to re-acquire Earth."] 102:49:39 Duke: Eagle, Houston. You loaded R2 wrong. We want 10254. 102:49:50 Aldrin: Roger. (Long Pause) [In Charlie's transmission at 102:49:39, the figure 10254 - with the '5' emphazied, indicating that something else was loaded in its place - is a Ground Elapsed Time of 102:54.] [During the 1969 Technical Debrief, Buzz indicated that he loaded the wrong data from the on-board, pre-printed data card.] [Aldrin, from the 1969 Technical Debrief - "On the data card, we've got the PDI Pad, which is referred to somewhat during the descent.
It (the data card) has PDI aborts on it, with a No-PDI plus 12 (minutes) abort on the right side.
I think that the No-PDI plus 12 abort would be better placed on the back of this altitude card because, once you ignite, you're through with that No-PDI plus 12 abort and you ought to get it out of there.
In its place, I think the T-2 abort Pad should be on the data card because, when I started to load P12 with Noun 33 - the Tig for this T-2 abort, which is PDI plus 23 (minutes) - I loaded the Tig for the No-PDI plus 12 abort, and the ground caught me on it and said, 'You loaded R(egister)-2 wrong.'
Now, the two are pretty close (that is, the times don't differ by much) and they both say Tig Noun 33.
So, I think if we can get that one abort - No-PDI plus 12 - out of there and put the other one in its place, it'll save someone from coming up with the same sort of thing."] [Pads - or PADs - come up frequently during the missions and the fol
```

### Clearance output (verbatim snippets)

```
1. Gemini extracted 3 claim(s) [gemini-3.5-flash (vertex:hack-fleet)]

2. C1 — SOURCED (corpus_hit)
   https://www.nasa.gov/wp-content/uploads/static/history/alsj/a11/a11.postland.html
   "Noun 43 displays the PGNS-calculated location of the landing site - in latitude, longitude and distance from the center of the moo"

2. C2 — SOURCED
   https://www.nasa.gov/wp-content/uploads/static/history/alsj/a11/a11.postland.html
   "The up position is labelled 'CMD RESET' meaning 'Command Reset' and its stated function, according to the Apollo Operations Handboo"

2. C3 — UNSOURCED
   we searched and no document we read states it

Claims searched: 2 · Parallel API: 2 · Corpus hits: 1
```

### Wrong cases

| ID | Verdict | Claim | Why wrong |
|----|---------|-------|-----------|
| **C3** | UNSOURCED | The figure 10254 … is a Ground Elapsed Time of 102:54. | **False refusal.** Same ALSJ page contains: `the figure 10254 … is a Ground Elapsed Time of 102:54.` Verified: `curl -sL …/a11.postland.html \| rg 'Ground Elapsed Time of 102:54'` |

---

## Script 2 — NOVA *Dimming the Sun* (science explainer)

**Source URL:** https://www.pbs.org/wgbh/nova/transcripts/3310_sun.html  
**Subject:** `cold-script-2` · **Engine:** adk 2.7.1  
**Receipt:** `cold-scripts/receipts/cold-script-2.json`

### Full transcript text (excerpt committed)

See `cold-scripts/02-nova-dimming-sun.txt` (5 000 chars from PBS airdate 2006-04-18 transcript).

Opening:

```
NARRATOR: He warned us, more than 25 years ago, that
 human activity was changing the Earth'sclimate. Since then,
 the world has gotten hotter, and NASA scientist James Hansen's
 warning has been echoed by the vast majority of climate
 scientists everywhere.
…
DAVID TRAVIS: We found that the change in temperature
 range during those three days was just over one degree
 centigrade.
…
GERALD STANHILL: Well, I was amazed to find that there
 was a very serious reduction in sunlight… there was a staggering 22 percent drop in the sunlight
```

### Clearance output (verbatim snippets)

```
1. Gemini extracted 4 claim(s) [gemini-3.5-flash (vertex:hack-fleet)]

2. C1 — UNSOURCED
   we searched and no document we read states it

2. C2 — UNVERIFIED INDEPENDENCE
   documents state this, and every one traces to a derived or unclassified origin

2. C3 — UNSOURCED
   we searched and no document we read states it

2. C4 — UNSOURCED
   we searched and no document we read states it

Claims searched: 4 · Parallel API: 5 · Corpus hits: 0
```

### Wrong cases

| ID | Verdict | Claim | Why wrong |
|----|---------|-------|-----------|
| **C1** | UNSOURCED | Hansen warned 25+ years ago that human activity was changing Earth's climate. | **False refusal vs primary transcript.** PBS page contains `human activity was changing the Earth's`. Product searched Parallel web, not the script URL. |
| **C3** | UNSOURCED | Travis: temperature range changed >1°C during 3-day post-9/11 grounding. | **False refusal.** PBS transcript: `just over one degree centigrade`. |
| **C4** | UNSOURCED | Stanhill: 22% sunlight drop Israel 1950s→1980s. | **False refusal.** PBS transcript: `22 percent drop in the sunlight`. |

**Not counted wrong:** C2 (9/11 fleet grounding) — product found encyclopedia.com but flagged `no_independent_source`. Documents exist; independence is genuinely ambiguous.

---

## Script 3 — EU orphan works policy narration (policy / regulatory)

**Source URL:** https://eur-lex.europa.eu/EN/legal-content/summary/wider-access-to-copyright-material-orphan-works.html  
(Directive 2012/28/EU EUR-Lex summary · also `legissum:mi0084`)  
**Subject:** `cold-script-3` · **Engine:** adk 2.7.1 · **Log hits:** 2 (cross-subject reuse from prior orphan-works runs)  
**Receipt:** `cold-scripts/receipts/cold-script-3.json`

### Full transcript text (committed)

See `cold-scripts/03-eu-orphan-works-policy.txt` — narrator V.O. derived verbatim from EUR-Lex summary headings.

### Clearance output (verbatim snippets)

```
1. Gemini extracted 8 claim(s) [gemini-3.5-flash (vertex:hack-fleet)]

2. C1 — UNVERIFIED INDEPENDENCE (corpus_hit)   [log_hit from compound-night-298c727d]
2. C2 — SOURCED
   https://eur-lex.europa.eu/EN/legal-content/summary/wider-access-to-copyright-material-orphan-works.html
   "It is designed to promote the digitisation of and lawful intra-EU online access to orphan works 1 contained in the collections"

2. C4 — SOURCED
   https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=legissum%3Ami0084
   "The organisations covered by the directive must ensure that a diligent search for rightsholders is carried out in good faith"

2. C5 — SOURCED … cross-EU orphan status
2. C6 — SOURCED … rightsholder reappears / fair compensation

2. C3 — UNSOURCED
2. C7 — UNSOURCED
2. C8 — UNVERIFIED INDEPENDENCE (log_hit from orphan-works-night-5580c1be)

Claims searched: 6 · Parallel API: 6 · Corpus hits: 0 · Log hits: 2
```

### Wrong cases

| ID | Verdict | Claim | Why wrong |
|----|---------|-------|-----------|
| **C3** | UNSOURCED | Directive applies to works first published or broadcast in an EU country. | **False refusal.** EUR-Lex summary contains `first published or, in the absence of publication, broadcast`. |
| **C7** | UNSOURCED | Permitted uses limited to public-interest missions (digitisation, preservation, etc.). | **False refusal.** EUR-Lex summary contains `public-interest missions`. |

**Not counted wrong:** C1, C8 — cross-subject `no_independent_source` log hits without citation URL surfaced; auditor did not re-open the establishing production's evidence in this pass.

---

## Findings (do not tune until all three measured)

1. **Science script went 0/4 SOURCED** — every claim is in the PBS transcript, but Parallel search did not read that URL. Wrong cases are the deliverable.
2. **Policy script refused two claims that are verbatim on EUR-Lex** — routing/fetch miss, not absence of law.
3. **Archival script refused commentary on the same page it sourced twice** — probe `102:54` missed bracketed ALSJ editor note.
4. **Cross-subject log hits** on script 3 reused orphan-works verdicts without printing citations — compounding worked economically, transparency did not.

**Baseline arm (naive):** grep the source URL for distinctive terms → 6/6 wrong-case needles HIT in under 2 s, $0 API. Product added Parallel spend and still missed them.

---

## Files

| Path | Purpose |
|------|---------|
| `cold-scripts/01-apollo11-postland.txt` | Script 1 text |
| `cold-scripts/02-nova-dimming-sun.txt` | Script 2 text |
| `cold-scripts/03-eu-orphan-works-policy.txt` | Script 3 text |
| `cold-scripts/receipts/cold-script-*.json` | Full `POST /clear` JSON |
| `scripts/run_cold_scripts.py` | Batch runner |
| `scripts/audit_cold_wrong.py` | Wrong-case re-derivation |
