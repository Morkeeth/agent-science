# BUILD NOW — 2026-08-28

*Read this first. Grounded today against the live URL, this git tree, and Oscar's
last three questions (public skill → multiple repos → "what's going on / next
move"). Supersedes `NEXT-STEPS.md` as the session head. Does not replace
`BUILD-PLAN-STARTUP.md` (company ceiling) or `VISION-2026-08.md` (spine).*

Today is **Friday 28 August 2026**. Agentic Cinema is **12 days out** (9 Sep,
14:00 PT). All Things Agentic closes **31 Aug** — Oscar's attention is contested
for 72 hours. Packaging (video, Devpost, public-repo flip) stays parked until
he un-parks it. Depth does not wait.

---

## 1. What's going on

The engine is ahead of the story the session docs tell. Three identities are
running on **one** constructor (`Verdict`), and the files still argue with each
other about which identity is "the work."

| Identity | The noun | Where it lives | Who it is for |
|---|---|---|---|
| **Companion** | a question | `VISION-2026-08.md`, `ask_registry.py`, `PRD-PUBLIC-SKILL.md` | anyone (or an agent) who is about to assert a fact |
| **Desk** | a script | README, hosted `/`, `POST /clear` | clearance lead / hackathon judge |
| **Vertical** | a filing | `PRD-2026-08.md`, `article53.py` | GPAI counsel, E&O, later |

Oscar already ruled the spine (25 Aug): the companion is the product; A1 is a
customer; the Desk is the same engine pointed at a script. The session queue
(`NEXT-STEPS.md`) was never rewritten after that ruling, so every new agent
still starts at "independence workbench on the Desk."

On top of that, the tree *looks* like several products because `research-corpus/`
has been ingesting Helicon / ZUP / patent / Transcripto claims as **dogfood**
(the engine clearing the fleet's own research). That is not a second Agent
Science. It is the corpus idea working.

**Repos:** there is one live GitHub repo, `Morkeeth/agent-science` (private).
`hack-agent-science` was a local docs sibling, pushed once, **gone from GitHub**
(`404` today). Local folder `~/CODE/cleared` is this same tree under the old
rights name. Two Cloud Run hostnames (`…568004190078.us-central1.run.app` and
`…33kamss2jq-uc.a.run.app`) are the **same service** (identical `/health` body,
project `hack-fleet`) — numbered vs hashed URL, not two products.

---

## 2. What's true, re-checked 2026-08-28

**Live on the hosted URL** (curl, this morning):

```
GET /health → gemini_path: vertex:hack-fleet
              parallel: true
              agent_builder: true
              adk_version: 2.7.1
              engine_default: adk
GET /ask    → 404
```

So the board item "Oscar must run `deploy.sh` so ADK is the hosted default" is
**done and the docs did not notice.** 3/3 partner integrations are on the URL a
judge opens. Receipt: the curl above; local proof remains
`docs/RECEIPT-agent-builder.md`.

**In this tree, shipped since NEXT-STEPS was written (23 Aug):**

| Ship | Commit / object |
|---|---|
| Cross-production refusal log on the live `clear_script` path | `e1f7fac` · `clearance/refusal_log.py` |
| Back-fill seeds reuse (cold-start baseline, 175 rows measured in test) | `98ce040` · `clear_corpus.py --backfill` |
| `verify_corpus` dogfood over the research corpus | `a0ea2e9` |
| Vision reframe: companion + registry, A1 as vertical | `2436584` · `VISION-2026-08.md` |
| `ask_registry.py` — local sqlite ask, sourced or honest miss | `855568d` |
| Public-skill PRD (ideation, this branch) | `7866d94` · `PRD-PUBLIC-SKILL.md` |
| Compounding Desk UI, orphan A/B **43%** search avoided, GCS **corpus** shelf | already on `main` |
| Held-out refusal set + watch-it-go-red suite | `tests/` |

**Still missing (the actual gaps, not the stale board):**

| Gap | Why it matters |
|---|---|
| **No `GET /ask`** | The companion has a CLI on a local db and no URL. Hosted surface is still "paste a documentary." |
| **Refusal log is not GCS-synced** | Corpus compounds across Cloud Run instances; the log (the registry, the moat) does not. `PRD-2026-08.md` §7, still open. |
| **Desk has no independence workbench** | Engine classifies; UI does not show origin groups or a next action. AUDIT: we grade homework. |
| **No skill/plugin package** | Correct — do not ship one until `/ask` returns a row. `PRD-PUBLIC-SKILL.md`. |
| **Repo private** | Blocks marketplace / Remote-Rule install. Parked until submit (`PLAN-30` 1.5). |
| **Wrong-refusal / substring≠statement / circular sourcing** | Open by design. Do not claim them solved. |
| **No dossier PDF, no async jobs, no tenants, no design partner** | Startup H1. Real, later. |

---

## 3. Kill the stale board

Do not restart these. They are done, parked, or the wrong object.

| Stale sentence | Reality 28 Aug |
|---|---|
| "LEFT FOR OSCAR: `bash deploy.sh` so hosted `engine_default: adk`" | Hosted `/health` already returns `"engine_default": "adk"` |
| "GCP + billing is the blocker" | False since 23 Aug; called out in `PITCH.md` |
| `SUBMISSION.md` Agent Builder ⬜ | Flip to ✅; the hosted field is the receipt |
| "Docs: github.com/Morkeeth/hack-agent-science" | 404. One repo. |
| PLAN-30 Phase 1.6 "Firestore — `/tmp` is not compounding" | GCS sqlite corpus shipped. Log is the remaining unsynced store. |
| PLAN-30 Phase 2.1–2.6 as unbuilt | `demo.sh`, dust-bowl second subject, refusal set, independence-as-set **exist**. Unfilmed, not unbuilt. |
| NEXT-STEPS #1 "independence workbench" as the session head **without** the vision ruling | Right Desk slice, wrong front door. Oscar's last questions were the companion and the repo, not Dust Bowl. |
| "Ship a public `SKILL.md` this week" | A prompt. Spends the name. `PRD-PUBLIC-SKILL.md` §4.1. |
| A second public `agent-science-skill` repo | Spec workaround if this repo stays private. Not created. Do not create until `/ask` is live. |

Oscar clicks that **remain** real: rotate keys if they were ever in plaintext env;
public-repo flip at submit; video; Devpost. None of those is the next *build*.

---

## 4. The spine, for the next twelve days

**Agent Science is the sourced-or-refuse companion for search.** A claim
cleared — or proven unprovable — once is free afterward. The Desk is how a
human pastes a script. Article 53 is how a lawyer files. The skill is how an
agent installs the companion. One `Verdict`. Refuse, don't score.

Hackathon (Sep 9) is a **checkpoint that the desk is real**, not a freeze.
A stranger on the URL must see: extract → Parallel → verbatim quote → an
UNSOURCED that is true → compounding on a second paste. That path exists.
Design is still the weak rubric axis (AUDIT): refusals are a wall, not a
work list. Fixing that on `/clear` *and* on `/ask` is the same output schema.

---

## 5. THE NEXT MOVE

**Put the registry on the URL: `GET /ask` + GCS-share `refusal_log.db`.**

This is one slice. It is the only slice that is simultaneously:

- VISION item 1 ("registry becomes the front surface")
- `PRD-2026-08` remaining infrastructure gap (log is local; corpus is not)
- `PRD-PUBLIC-SKILL` Slice 1 (the thing a public skill would call)
- the A→B compounding story for *questions*, not only scripts
- buildable in this repo without Oscar's click (ship waits on his `deploy.sh`
  only to land on the URL; the code path can be proved locally)

### Done when

1. `GET /ask?q=Directive+2012/28` returns JSON: hits with `verdict`, `quote`,
   `url`, `cause`, or an empty list labelled `NOT CLEARED YET` — never a 500,
   never a hedged yes.
2. The same handler is a box on `/` ("Ask the registry") above the script
   paste. A miss does not invite the model to invent; it prints the miss.
3. `refusal_log.py` pulls/pushes via the same GCS helper as `corpus_gcs.py`
   (`REFUSAL_LOG_GCS_URI` or a second object on the existing bucket). A
   control proves a write on instance A is visible to a read on a fresh db
   file (the corpus pattern: `tests/test_backfill_seeds_reuse.py` shape).
4. `deploy.sh` sets the new env var. Oscar's next deploy (whenever) is what
   makes `/ask` live; until then, `python3 ask_registry.py` and a local
   `cloud/service.py` are the proof.
5. No `SKILL.md` installed in `.cursor/skills/` this slice. Packaging after
   the URL returns a row.

### Explicitly not this slice

- Marketplace / plugin.json / public repo
- `clear_claim` as an anonymous public write (that is a Parallel bill)
- Independence workbench UI (next, on the same output schema)
- Dossier PDF / async / tenants
- Filming `demo.sh`

### Size / risk

Medium. The ask function exists (`ask_registry.py`). The GCS helper exists
(`corpus_gcs.py`). The failure mode is shipping `/ask` against an **empty**
hosted log — first reviewer types a question, gets a miss on terms we have
already back-filled locally, files us under unfinished. So: run
`clear_corpus.py --backfill` into the log **before** the first hosted ask,
and GCS-push that file. Empty-registry is an honest miss for *new* questions;
it is a lie for "Directive 2012/28/EU".

---

## 6. Queue after `/ask` lands (do not start all at once)

Oscar cuts. Do not thin preemptively. Re-order only when the previous slice
has a receipt.

| # | Slice | Serves | Done when |
|---|---|---|---|
| **0** | **`GET /ask` + GCS log** | companion, skill, moat | §5 |
| **1** | **Resolution queue** (AUDIT §2) | Desk *and* ask | every UNSOURCED row has one next action; `resolves_with` already on the log schema, currently unprinted on the Desk |
| **2** | **Escalation before refuse** (AUDIT §1) | Desk, the 0-of-10 hole | first search derived-only → second search aimed at a primary; Dust Bowl gains ≥1 PRIMARY without loosening the allowlist |
| **3** | **Independence workbench** | Desk design axis | origin groups visible; unclassified never looks cleared |
| **4** | **Skill packaging** | distribution | `SKILL.md` + plugin talking to **live** `/ask`; still no marketplace until public repo |
| **5** | **Dossier export** | paid artifact | PDF + JSON + run hash from a `/clear` |
| **6** | **Async `/runs`** | production scripts | `run_id` + poll; 5-min script ≠ HTTP timeout |
| **7** | **Design partner** | day-two user | one real script, friction list in `CURSOR-LOG.md` |

Sep 9 floor (does not jump this queue, does not get forgotten):

- Hosted URL stays up (it is)
- `demo.sh` still runs a real extract → search → verbatim → UNSOURCED
- Second paste compounds (corpus GCS already)
- Video / Devpost / public — Oscar, late, un-nagged
- Sealed prediction after he says the exhibit is the one on the URL

H1 after 9 Sep is still `BUILD-PLAN-STARTUP.md` §4–5 (tenants, spend meter,
asset leg). This file only names what changed *under* that ceiling: the
front door is `/ask`, not a thicker paste box.

---

## 7. How the files relate, as of today

| File | Job now |
|---|---|
| **This file** | Current plan + next move |
| `VISION-2026-08.md` | Spine (companion / registry) |
| `PRD-PUBLIC-SKILL.md` | Why a `SKILL.md` without `/ask` is theater |
| `PRD-2026-08.md` | Paying vertical + honest engine gaps |
| `BUILD-PLAN-STARTUP.md` | Company ceiling (H1–H3). Still right. Slice 1–7 *order* is updated here. |
| `PLAN-30.md` | Wedge calendar / what voids Sep 9. Hygiene only. |
| `BUILD-PLAN.md` | Historical (22 Aug admissibility). Do not execute. |
| `NEXT-STEPS.md` | Pointer at this file. Not a second queue. |
| `SUBMISSION.md` | Judge packet. Agent Builder is ✅ on the URL. One repo. |

---

## 8. This session, if we are building rather than talking

1. Wire `GET /ask` in `cloud/service.py` to `ask_registry.ask`.
2. GCS-sync the refusal log the way the corpus already syncs.
3. Add the ask box on `/`.
4. Back-fill, control, commit, push. Hosted land waits on deploy.

That is the move. Everything else is a later slice or a parked Oscar click.
