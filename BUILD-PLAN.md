---
date: 2026-08-22
ruling: AGENT SCIENCE (fact clearance) · Parallel track · Oscar, verbatim: "Agent science! thats the goal"
event: Agentic Cinema · deadline 2026-09-09 14:00 PT
status: admissibility is the whole lane · **slice 5 DONE 2026-08-30** · slice 6 prep · Sep 9 deadline
---

# Build plan — from "inadmissible" to "submittable"

## 0 · TREE RULING (mine, reasoning stated, neither tree deleted)

**Consolidate into this tree (`agent-science`), carry the docs across, rename before public.**

The code is the expensive half and it is all here — engine, citation guard, corpus, gap
report, locator/verifier split, both nouns, 31 controls, **and the FACT leg already built
and tested, which IS Agent Science's engine.** `agent-science` holds the portable
half: ORIENT, the 7-slice queue, PHASE-0, the EYES panel, the pre-build fixture. Documents
move in an afternoon; a tested engine does not.

**But the directory name is wrong and a judge sees it.** `cleared` is a rights name on a
facts product. The final name is Oscar's call — `/weekend-name` fires before the repo goes
public, not after. Working name until then; the rename is one `git mv` and costs nothing.

## 1 · MEASURED, NOT ASSUMED — what exists on this machine right now

    gcloud                              NOT INSTALLED
    google.genai / vertexai / aiplatform  not installed
    GOOGLE_API_KEY / GEMINI_API_KEY     unset
    GOOGLE_APPLICATION_CREDENTIALS      unset
    PARALLEL_API_KEY                    unset
    ~/.config/gcloud/…default_credentials.json   absent

**Zero of the three required integrations has a credential.** This is not a design
question, it is two signups.

## 2 · ONLY OSCAR CAN DO THESE — in order, with what each unblocks

| # | His action | Unblocks | Time |
|---|---|---|---|
| **1** | **Gemini API key** — aistudio.google.com → Get API key. No billing needed. | Slice A: the whole `locate()` seam, the largest single piece of work | ~2 min |
| **2** | **Parallel Search API key** — parallel.ai signup | Slice B: the track's own requirement. Without it the entry cannot score on its track at all | ~5 min |
| ~~**3**~~ | ~~**GCP project + billing enabled**~~ **DONE, and had been for a while** (verified 2026-08-23: project `hack-fleet`, `billingEnabled: true`, `aiplatform` + `agentregistry` enabled, ADC on disk). It sat at #1 on the board as an Oscar-only blocker because nobody ran the probe. **Replaced by:** `bash deploy.sh` — one command, ships the billed public revision | ~3 min |

Nothing else on this lane is blocked on a human. #1 and #2 are the cheap ones and unblock
two of the three runtime integrations.

## 3 · THE SLICES — dependency-ordered, each independently verifiable

**A · Gemini behind `locate()`** *(needs key #1)*
One slice, three problems solved. A `GeminiLocator` proposes the passage carrying a claim;
`verify.py` refuses anything not verbatim in the fetched document. **The guard does not
move; the retrieval does.**
- satisfies "Gemini imported and actually called at runtime"
- deletes the hand-scraped chrome list, which was overfitted to two websites
- closes the false-UNKNOWN finding — the defect came from `str.find` hitting a nav label
DONE WHEN: the 5 adversarial-proposer controls still pass with the Gemini locator in
place, and a claim supported only in an awkward position (table cell, second occurrence)
resolves GREEN where `StringLocator` returned UNKNOWN.

**B · Parallel Search in front of `locate()`** *(needs key #2)*
Not a bolt-on for this product: finding the document that *might* carry a claim is
literally step one. Today a `Claim` arrives with `source_url` already filled in by hand.
Parallel is what fills it.
DONE WHEN: a claim with `source_url=None` returns candidate documents, each fetched and
run through the existing verifier; unfound claims still print UNSOURCED with the probe named.

**C · Agent Builder deployment** *(built 2026-08-23; the code path is done and proved
locally — `docs/RECEIPT-agent-builder.md`. Only `deploy.sh` is left, and it is Oscar's click.)*
The orchestration: extract claims → search → fetch → locate → verify → gap report.
DONE WHEN: a hosted URL a stranger can paste a script into.

**D · The exhibit + submission** — hosted URL, public repo, OSI licence, ≤3-min video.
All four are mandatory; a missing one is inadmissible regardless of the build.

## 4 · CURSOR'S LANE — review, not product code

Git is the mailbox, one writer on product code at a time. Cursor takes `FOR-CURSOR.md`,
logs to `CURSOR-LOG.md`, and gets the adversarial half:
- attack the verifier with proposers I did not think of
- audit every control for the class we swept today: does it bind to the live object, or
  carry its own copy of what it grades
- read `PITCH.md` cold and mark every claim whose evidence it cannot find in the repo

## 5 · WHAT DOES NOT CHANGE

The citation guard, the corpus, the gap report, the UNKNOWN cause taxonomy and the 31
controls are the product and carry over untouched. **No fork-dependent work was started,
so the ruling costs nothing.** The asset leg stays on disk, unbuilt, as the expansion path.
