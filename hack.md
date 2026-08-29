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

- [x] **Alternative arm named and run** — `eval/refusal_correctness_gate.py`: `NaiveFirstOccurrence` vs shipping on `fixtures/refusal-correctness/set.json`; receipt `eval/RECEIPT-refusal-gate.md`
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

## NOW — 2026-08-29 night wave · Qwen eval gate + submission truth refresh

**ONE slice:** falsifiable eval gate (baseline + ablation + shipping) + SUBMISSION-PACK counts re-derived at object.

### Shipped tonight
- [x] `eval/refusal_correctness_gate.py` + `eval/README.md` — three arms on held-out set (n=6, RC5 engine_limit pinned)
- [x] `eval/RECEIPT-refusal-gate.md` — per-item rows; **RC5: all three arms false GREEN** (worst number)
- [x] `scripts/seed_test_cache.py` — stranger path to **72/72** red-watch offline (EUR-Lex 403 → honest fixture seed)
- [x] `docs/SUBMISSION-PACK-2026-08-29.md` — stale **26/13** replaced with **72/72 · 99/99**; one-command block added
- [x] `docs/DEPLOY-CHECKLIST-2026-08-29.md` — slice 1 prep for Oscar (no deploy run)
- [x] `tests/test_eval_gate.py` — 3 controls on eval gate receipt
- [x] `scripts/compound_exhibit_receipt.py` — live path BLOCKED section names missing keys

### Blocked (honest receipts, not guessed)
- [ ] Live orphan-works A/B — **no Gemini/Parallel keys** on agent VM (`docs/COMPOUND-EXHIBIT-2026-08-29.md` offline + BLOCKED section)
- [ ] Hosted `/registry` — slice 1 deploy (Oscar)
- [ ] Public repo · video · Devpost — Oscar only

### Stranger path (offline)
```bash
python3 scripts/seed_test_cache.py
python3 tests/test_registry_surface.py -q
python3 scripts/compound_exhibit_receipt.py
python3 eval/refusal_correctness_gate.py
python3 tests/test_watch_it_go_red.py   # → 72/72 after seed
```

### Controls (re-derived @ object — run 2026-08-29 night wave)
- `python3 scripts/seed_test_cache.py` → documents.json + searches.json seeded (EUR-Lex via fixture on 403)
- `python3 tests/test_watch_it_go_red.py` → **72/72**
- `python3 tests/test_registry_surface.py` → **5/5**
- `python3 tests/test_cross_subject_reuse.py` → **2/2**
- All 9 suites → **102/102** (includes `test_eval_gate.py` 3/3)
- `python3 eval/refusal_correctness_gate.py` → receipt; catchable **5/5** all arms; **RC5 all GREEN** (engine_limit); verify delta **0** on catchable

### LOG
- **2026-08-29 start:** `git pull` OK; red-watch **11 fail** on cold VM — missing `cache/documents.json` + `cache/searches.json` (hack.md claimed 72/72; NOW was stale)
- **2026-08-29 seed:** EUR-Lex HTTP 403 from VM egress → fixture `eur-lex-orphan-snippet.html` with provenance string (not silent)
- **2026-08-29 cherry-pick:** `7e0ee80` from `cursor/qwen-eval-gate-0e77` onto `cursor/qwen-eval-gate-d2e2`; seed → **72/72**
- **2026-08-29 ablation:** added ABLATION arm (StringLocator, verify off); verify delta 0 on catchable n=5; RC5 still false GREEN on all arms
- **2026-08-29 compound:** live path BLOCKED (no keys); offline receipt A=2, B=1 Parallel, corpus_hits=2; BLOCKED section names missing env vars
- **2026-08-29 counts:** SUBMISSION-PACK stale 26/13 fixed; **102/102** across 9 suites after `test_eval_gate.py`

### Prior slices (unchanged)
- Registry backfill **173 rows** · dust-bowl offline **2/2** · slice 7 video script **178 s**

---

*Update the NOW section after every slice. Oscar owns slice 1 deploy and submission gates.*
