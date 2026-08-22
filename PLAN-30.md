---
date: 2026-08-22
horizon: 30 days · Aug 22 → Sep 21
deadline: Agentic Cinema · Sep 9 2026 14:00 PT (day 18) — checkpoint, not "done"
rule: over-build the product; Oscar cuts scope. Never assess as near-ship. Video/Devpost late.
oscar: 2026-08-22 — "you can fix me 30 more days of building… over build and ill stop you"
---

# 30 DAYS

**Default stance: over-build.** Prefer depth (corpus, refusal, independence, second subject,
asset leg) over packaging urgency. Sep 9 is a **checkpoint**. Days 19–30 are the company
whether or not we place. Oscar stops over-scope — do not self-thin into a demo.

`🔴` = blocked on Oscar. `🤖` = build. `👁` = Cursor review.
`⛔` = **a missing one makes the entry inadmissible, however good the build is.**

**Over-build is the stance; `⛔` is the floor, and the two do not conflict.** Packaging is
not next work and should not crowd out depth — but the marks stay visible, because the
recorded failure here is not over-scoping, it is a finished build that was inadmissible
for a knowable reason nobody was looking at. A live demo and a clean repo are still a
fail without the video. Build deep; never lose sight of what voids the entry.

---

## PHASE 0 · CLOSE THE WOUND (Aug 22–23)

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

## PHASE 1 · FOUNDATION — days 1–5 (Aug 23–27)

Product foundation, not packaging panic. Hosted URL exists; **clean deploy + real store** do not.

| # | Task | Who |
|---|---|---|
| 1.1 | 🤖 **Hosted URL redeployed clean** — `/health` reports the path that answers; cold visitor gets a page not a stack | me |
| 1.2 | 👁 Health check — `gemini_path` (done in tree @ `a1817b6`; must be live after redeploy) | Cursor |
| 1.3 | 🤖 **Agent Builder on the default path**, proved with `env -u`, not claimed | me |
| 1.4 | 🤖 **Pre-publication audit** — no keys/transcripts/`cache/` blobs that shouldn't travel | me |
| 1.5 | 🔴 Public repo **only at submit** — not now | Oscar / late |
| 1.6 | 🤖 **Firestore** (or managed) corpus — `/tmp` is not compounding | me |
| 1.7 | 🤖 Kill false ✅s in `SUBMISSION.md` — public repo / Agent Builder claims | me |

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

## PHASE 3 · CHECKPOINT (Sep 2–9) — only when Phases 1–2 are real

**Do not start this phase early. Do not nag Oscar about video.**
If Phase 2 is thin, keep building — submission packaging waits.

| # | Task | Who |
|---|---|---|
| 3.1 | 🤖 Soft freeze only when compounding + demo path + refusal set exist | me |
| 3.2 | 🔴 Oscar drives the full path himself, fresh browser — when *he* says ready | Oscar |
| 3.3 | 👁 Pre-camera cold pass — only after 3.2 | Cursor |
| 3.4 | 🤖 Grep story-bank before any script; rule every hit | me |
| 3.5 | 🔴 Video — **Oscar's call, late, not a build-lane prompt** | Oscar |
| 3.6 | 🔴 Devpost + public repo — late | Oscar |
| 3.7 | 🤖 Sealed prediction after the exhibit exists | me |

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
