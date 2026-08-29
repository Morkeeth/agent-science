# hack.md — Agentic Cinema constitution + 7 slices

**Repo:** Morkeeth/agent-science · **Event:** Agentic Cinema · Sep 9 2026  
**Spine:** Agent Science = the websearch companion — a registry of verified truths.  
**Constitution:** verbatim span or REFUSE — never paraphrase. No public repo. No rename. No `--set-env-vars` secrets. Slice 1 deploy/keys: Oscar only.

---

## ⛔ PRIOR LOSS — read before the next result table

Mount Helicon lost Track 1 of the Qwen Cloud Global AI Hackathon to **Quên**
(`github.com/phamthanhhang208/quen`). Measured at the submitted tag `submission/devpost-2026-07-21`
against their `HEAD`: they won with **11,007 Python LOC, 17 test files, 50 commits and a top-level
`eval/`**; we lost with **29,588 LOC, 41 test files, 310 commits and no `eval/`**. We were not
under-measured — the submission carried 1,104 lines of benchmark code and two named benchmarks.
**What it never had was an alternative arm.** Every Helicon number answered *does it work*, scored
against Oscar's own vault and his own rulings. Every Quên number answered *is it better than what
you would have built instead*: FAMA 0.933 vs append-only RAG 0.400 vs full-context 0.367 on
identical inputs, plus an ablation of their own mechanism at 0.833, Wilson CIs and paired McNemar
(16–0, p=3×10⁻⁵) because n=30, an external anchor (LongMemEval n=229), a paraphrase holdout frozen
before any tuning, cost from billing, an offline no-key dry-run, and a section titled "Algorithmic
biases — found & fixed" listing defects in their own scoring. Their README is *shorter* than ours.
**Tests prove it runs; a self-benchmark proves it works; only a control arm proves it is better —
and "better than the alternative" is the only claim a judge scores.** A benchmark against your own
answer key on your own data reads as proof and is not one; it is worse than no numbers, because its
rigour vouches for a claim it never tested.

**Footnote on the retro itself, which is half the lesson.** The first retro of this loss blamed the
tagline, written from 24 scraped taglines with nobody having opened the winner's repo. The brief
that corrected it then measured `~/CODE/mountain-of-helicon` — a different, never-submitted repo —
and counted `.venv` as our code, producing a "1/63 our size" headline that is false. Two
wrong-object errors in the two documents whose job was to explain the loss. **Measure the commit
that was submitted, not the working tree and not the same-named sibling.**

**Gate before this event's result table ships:**

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
- [ ] **Every artifact claim measured at the submitted commit.**

Full record: `~/CODE/fleet-ops/retros/QWEN-LOSS-RETRO-2026-08-30.md` · playbook lesson 97.

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
