---
date: 2026-08-22
horizon: 30 days · Aug 22 → Sep 21
deadline: Agentic Cinema · Sep 9 2026 14:00 PT (day 18)
rule: rank every task by whether it moves THE ONE THING THAT CAN FAIL THE SUBMISSION
---

# 30 DAYS

Days 1–18 win the event. **Days 19–30 are the company** — the part that exists whether
or not we place. Both are in here because the Ideation Law says pitch the vision, not
the sprint.

`⛔` = a missing one makes the entry **inadmissible**, regardless of how good the build is.
`🔴` = blocked on Oscar. `🤖` = mine. `👁` = Cursor's review lane.

---

## PHASE 0 · TONIGHT — close the wound (Aug 22)

| # | Task | Who |
|---|---|---|
| 0.1 | 🔴 **Rotate the Gemini key** (aistudio.google.com — delete + recreate) | Oscar |
| 0.2 | 🔴 **Rotate the Parallel key** (parallel.ai dashboard) | Oscar |
| 0.3 | 🤖 Redeploy with the fixed `deploy.sh` — no Gemini key at all, Parallel via Secret Manager | me, after 0.1/0.2 |
| 0.4 | 🤖 Delete the leaked revisions once rotation is done | me |
| 0.5 | 🤖 Add a control that **fails the build if any deploy surface passes a secret via `--set-env-vars`** | me |

**0.5 is the real fix.** The rewritten script was correct and the old one ran anyway.
A rule that lives in a file gets bypassed; a rule that lives in a test gets caught.

---

## PHASE 1 · ADMISSIBILITY — days 1–5 (Aug 23–27)

Nothing else matters until every ⛔ is green. A perfect build with a missing video is a fail.

| # | Task | Who |
|---|---|---|
| 1.1 | ⛔🤖 **Hosted URL** — redeployed clean, `/healthz` reports the path that actually answers, cold visitor sees a real page not a stack trace | me |
| 1.2 | ⛔👁 Fix `cloud/service.py` health check: it reports `gemini:false` on a working keyless service | Cursor |
| 1.3 | ⛔🤖 **Agent Builder actually called on the default path**, proved with `env -u`, not claimed | me |
| 1.4 | ⛔🤖 **Pre-publication audit widened** — no keys, no transcripts, no cached document containing anything of Oscar's, no `cache/` blob that shouldn't travel | me |
| 1.5 | ⛔🔴 Flip the repo public **at submission, not before** — 7,415 registrants, Devpost only requires public at submit | Oscar |
| 1.6 | 🤖 **Firestore** as the corpus store — for the product reason: a corpus that compounds wants a managed store | me |
| 1.7 | 🤖 Kill `SUBMISSION.md`'s false ✅s — "public repo" (it is private) and "Agent Builder" (never executed) | me |

---

## PHASE 2 · THE THING THAT WINS — days 6–10 (Aug 28 – Sep 1)

⚠️ **All Things Agentic closes Aug 31.** Oscar's attention is contested Aug 26–31.
Anything here that needs him must land before the 26th or after the 31st.

| # | Task | Who |
|---|---|---|
| 2.1 | 🤖 **`demo.sh`** — one command, under 3 minutes of screen time, showing: script in · Gemini extracting · Parallel hitting the open web · a passage verified verbatim · **the UNSOURCED row appearing because it is true** · the source-independence section admitting which sources are derived | me |
| 2.2 | 🤖 **The corpus compounding on camera** — run B on the same subject resolves from memory with fewer Parallel calls. Currently claimed, never filmed | me |
| 2.3 | 🤖 **A second script on a different subject** — proves it is not tuned to orphan works | me |
| 2.4 | 👁 Read `demo.sh` cold: anything a judge would not understand in 3 minutes | Cursor |
| 2.5 | 🤖 **The refusal-correctness held-out set** (`docs/SPEC-…` exists, unbuilt). The suite still cannot fail on a false UNKNOWN | me |
| 2.6 | 🤖 Source-independence beyond a URL heuristic — independence is a property of the source SET | me |

---

## PHASE 3 · FREEZE, FILM, SUBMIT — days 11–18 (Sep 2–9)

| # | Task | Who |
|---|---|---|
| 3.1 | 🤖 Feature freeze Sep 5. After this only defect fixes | me |
| 3.2 | ⛔🔴 **Phase-6 gate: Oscar drives the full path himself**, fresh browser, no credentials. Not delegable | Oscar |
| 3.3 | ⛔👁 **Pre-camera cold pass** — a non-builder drives the exact on-camera surface; **LIVE equals FIXED by hash** | Cursor |
| 3.4 | 🤖 Grep `story-bank.md` before the script is written; rule every hit | me |
| 3.5 | ⛔🔴 **Record the 3-min video** — "functioning as built, not a cinematic trailer" | Oscar |
| 3.6 | ⛔🔴 Devpost form + partner track + public repo + licence + hosted URL + video | Oscar |
| 3.7 | 🤖 Sealed prediction written before results | me |

---

## PHASE 4 · THE COMPANY — days 19–30 (Sep 10–21)

The event ends on day 18. **This is why the build was worth doing.**

| # | Task | Why |
|---|---|---|
| 4.1 | **One real archive or production company runs it on their own material** | The day-two user must not be a judge |
| 4.2 | **The asset leg** — shot-level rights on a real library. Built and parked; it is the second half of the thesis | One engine, two nouns, one buyer with two problems |
| 4.3 | **The gap report as the paid artifact** — "63% of your library is unclearable; here are the 4 contracts that unlock 40%" | The upsell, and the only output anyone pays for today |
| 4.4 | **Independence, properly** — a corroboration graph, not a URL blocklist | The unsolved problem at the centre of the product |
| 4.5 | **Price it.** Per-production, per-library, or per-dossier | A company is described by who it makes rich |
| 4.6 | Write the retro into `hackathon-playbook`; distil the four wrong-object findings | The learnings loop |

---

## THE FOUR THINGS THIS BUILD LEARNED, carried forward

1. **A seam existing is not the service being called.** Hit four times today: eligibility, `CORPUS_DB`, the health check, the independence print.
2. **A gap report with no gaps is evidence the input was rigged.**
3. **Overclaiming is caught by a judge. Underclaiming is caught by us.**
4. **A rule in a file gets bypassed; a rule in a test gets caught.** The safe deploy script existed and the unsafe one ran.
