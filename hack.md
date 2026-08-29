# hack.md — Agentic Cinema constitution + 7 slices

**Repo:** Morkeeth/agent-science · **Event:** Agentic Cinema · Sep 9 2026  
**Spine:** Agent Science = the websearch companion — a registry of verified truths.  
**Constitution:** verbatim span or REFUSE — never paraphrase. No public repo. No rename. No `--set-env-vars` secrets. Slice 1 deploy/keys: Oscar only.

---

## ⛔ PRIOR LOSS — read before the next result table

**Corrected 2026-08-29. The earlier version of this section said Mount Helicon lost because its
evaluation had "no alternative arm." That is retracted — it was falsified at n=40 and it was wrong
about our own submission.**

Mount Helicon lost Track 1 of the Qwen Cloud Global AI Hackathon to **Quên**
(`github.com/phamthanhhang208/quen`). The entry exists and was submitted:
`devpost.com/software/glaze-lo72xn` — the slug carries the project's old codename `glaze`. Measured
at our submitted tag `submission/devpost-2026-07-21` (commit `0eef89f`) against their `HEAD`: they
won with **~11–14k Python LOC** *(two counters disagree; unreconciled)*, **17 test files, 50 commits
and a top-level `eval/`**; we lost with **29,588 LOC, 41 test files, 310 commits and no top-level
`eval/`**. Their README is *shorter* than ours. **We were not under-measured** — the submission
carried 1,104 lines of benchmark code, two named benchmarks, and a rival-model arm reported with
numbers at README line 206 (`qwen3.6-plus 0.962 ties claude-sonnet-5 0.962, beats gpt-5 0.808`).

**WHY WE LOST IS UNKNOWN.** Four confident diagnoses were written in two days and all four were
wrong: (1) *the tagline* — from 24 scraped taglines, no repo opened; the winner's tagline is the
same shape, and our real Devpost tagline is benefit-shaped. (2) *no eval dir / 63× their size* —
measured the wrong repo (`mountain-of-helicon`, never submitted) and counted `.venv` as our code.
(3) *no alternative arm* — falsified at n=40, blind-coded, pre-registered: **7 of 20 winners ship
none**, and non-winner `clearcrew` has one of the most rigorous benchmarks in the field and still
lost. (4) *never submitted* — wrong; the gallery search failed on the old codename. **Each was
fitted to whatever had most recently been measured, and none was checked against the object it made
a claim about.** What survives from (3) is a tendency only: 65% of winners vs 25% of non-winners,
Fisher p=0.025, post-hoc and correlational — not an explanation.

**Untested candidates that remain live:** category fit against the track brief · demo/video
visibility (the live Devpost page shows **no video**, and the frozen tag's `DEVPOST-FINAL.md` still
reads *"PASTE PUBLIC VIDEO URL HERE"*) · the rubric's actual weights (**30/30/25/15, with no
eval-rigor line at all**) · field size (724 slugs, 23 badges) · judging noise. **The one thing that
would settle it is judge feedback from the organisers — an outward act only Oscar can request.**

**Gate before this event's result table ships** — this checklist now stands on its own merits as
submission craft, supported by a real tendency, **not** as the explanation of that loss:

- [ ] **Alternative arm named and run** — what a competent person does *without* this project, on identical inputs, identical budget, identical prompt.
- [ ] **Ablation** — our one signature mechanism switched off; its delta is the only number that credits our idea.
- [ ] **External anchor** — one dataset or benchmark we did not build and cannot tune, or an explicit README line saying there is none.
- [ ] **Holdout frozen before the first tuning pass.**
- [ ] **Baseline steelmanned** — run it, read its raw rows, confirm it can actually score before believing our margin.
- [ ] **Statistic matched to n** — n<100 → CIs + a paired test, never a bare point.
- [ ] **Scorer symmetrical** — nothing only our system can emit; judge from delivered output for every arm.
- [ ] **Cost from billing**, with the price card's date stated.
- [ ] **Offline path with no API key.**
- [ ] **"Honesty & limitations" section carrying our worst number.**
- [ ] **Answer the track brief in the track's own words on the first screen** — that is what the rubric weights, not eval rigor.
- [ ] **Video verified attached and public on the live entry page, from a logged-out browser** — not in a checklist file, on the page.
- [ ] **Every artifact claim measured at the submitted commit.** Four retros of that loss failed this row.

Full record: `~/CODE/fleet-ops/retros/QWEN-LOSS-RETRO-2026-08-30.md` (corrected) ·
`QWEN-FIELD-TEST-2026-08-30.md` (the n=40 falsification) · playbook lesson 97.

---

## The seven slices

| # | Slice | Owner | Done when |
|---|--------|-------|-----------|
| **1** | **Deploy the desk** | Oscar | Hosted URL a stranger can paste a script into; keys via Secret Manager; `deploy.sh` only |
| **2** | **The registry has a face** | build | Query in → SOURCED span, UNSOURCED, or UNKNOWN with named refusal; every query browsable |
| **3** | **Backfill + compound exhibit** | build | Cross-production log seeded from fleet corpus; orphan-works A/B shows Parallel drop |
| **4** | **A second subject** | build | Full chain on a corpus unrelated to orphan works; receipt with failures honest |
| **5** | **Agent Builder as default** | build | ADK on default `/clear` path; receipt with `engine: adk` — **claims only, no deploy** |
| **6** | **Design partner loop** | Oscar + build | One real clearance lead runs their script; friction list in CURSOR-LOG |
| **7** | **Submission pack** | Oscar | Public repo, OSI licence, ≤3-min video, Devpost — all four mandatory |

---

## NOW — 2026-08-29 (slices 2 + 3 + 4 run)

**Baseline:** `refusal_log.py` 264 lines · registry backfilled: **173 rows** (29 SOURCED + 144 proven-unprovable refusals seeded from `research-corpus/`).

### Slice 2 — registry surface
- [x] `clearance/refusal_log.py` — `queries` table, `search_registry()`, `browse_queries()`, `surface_label()`
- [x] `ask_registry.py` — CLI + `--browse` + `--serve` local UI on :8091 (CSS template bug fixed)
- [x] Every query logged as a browsable row; refusal carries named `cause` + `why`
- [x] `tests/test_registry_surface.py` — 5 controls green
- [ ] Hosted `/registry` on Cloud Run (blocked: slice 1 deploy is Oscar's)

### Slice 3 — backfill + compound exhibit
- [x] Registry backfilled from `research-corpus/` — **173 rows** (`clear_corpus.py --backfill`)
- [x] Orphan-works A/B: Run A **2** Parallel → Run B **1** Parallel, **2** corpus hits (offline; keys absent)
- [x] Receipt: `docs/COMPOUND-EXHIBIT-2026-08-29.md`
- [ ] Live orphan-works A/B on `documentary-orphan-works*.txt` — **blocked on this VM:** no Gemini/Parallel keys

**Stranger path (this VM):**
```bash
python3 clear_corpus.py research-corpus --backfill
python3 ask_registry.py "arxiv:2511.12884"          # → SOURCED span
python3 ask_registry.py "agentlint"                 # → UNSOURCED + named cause
python3 ask_registry.py --serve                     # http://127.0.0.1:8091/
```

### Slice 4 — second subject (dust-bowl)
- [x] Fixtures: `fixtures/scripts/dust-bowl-A.txt`, `dust-bowl-B.txt` (public-domain narration, not orphan works)
- [ ] Live full chain: `agent_science.py` on dust-bowl — **blocked on this VM:** no Gemini/Parallel keys
- [x] Receipt: `docs/SECOND-SUBJECT-RECEIPT-2026-08-29.md` — failures named honestly
- [x] Offline proof: `tests/test_cross_subject_reuse.py` 2/2 — dust-bowl reuses orphan-works log at 0 Parallel calls

### Controls
- `python3 tests/test_watch_it_go_red.py` → **26 passed, 13 failed** (suite crashes on missing EUR-Lex body; rightsstatements fetched OK)
- `python3 tests/test_registry_surface.py` → **5 passed**
- `python3 tests/test_cross_subject_reuse.py` → **2 passed**
- `python3 review/corpus_compound_receipt.py` → **50/50 reuse, 0 network on Run 2**

### Not touched (per constitution)
- `deploy.sh`, repo visibility, key rotation, slice 5 Agent Builder deploy claims

---

*Update the NOW section after every slice. Oscar owns slice 1 and submission gates.*
