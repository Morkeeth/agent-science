# hack.md — Agentic Cinema constitution + 7 slices

**Repo:** Morkeeth/agent-science · **Event:** Agentic Cinema · Sep 9 2026  
**Spine:** Agent Science = the websearch companion — a registry of verified truths.  
**Constitution:** verbatim span or REFUSE — never paraphrase. No public repo. No rename. No `--set-env-vars` secrets. Slice 1 deploy/keys: Oscar only.

---

## NORTH STAR

Paste a documentary script; get every checkable claim back as a verbatim quote with its source URL, or UNSOURCED with a named reason — so a production can insure and release without guessing.

## PROMISE LINE

**You get:** a gap report where every claim is SOURCED (exact passage + citation) or UNSOURCED (actionable cause).  
**Constraint:** if the document does not contain the exact passage, refuse — never paraphrase, never infer.

## OPEN QUESTIONS

- Live compound exhibit on hosted URL — blocked on keys + deploy (Oscar).
- RC5 substring false-GREEN — semantic guard not decided; structural verifier cannot catch it.
- Design partner session — Oscar outreach (slice 6).

## CONSTITUTION

- Verbatim span or REFUSE — `Verdict.__post_init__` enforces citation.
- Locator untrusted; verifier structural; model never authors verdict.
- No plaintext secrets in repo or deploy surfaces (control scans tree + git log).
- Outward acts (deploy, public repo, Devpost, video) — Oscar only.
- Do not tick a box whose done-when was not RUN; say the command.

## PLAN (risk-first slices)

| # | Slice | Risk |
|---|--------|------|
| 1 | Deploy desk | Keys leak / wrong revision |
| 2 | Registry face | False SOURCED in browse UI |
| 3 | Compound exhibit | Compounding claim unproved |
| 4 | Second subject | Cross-subject collision |
| **5** | **ADK default path** | **Agent Builder claimed but not on runtime path** |
| 6 | Design partner loop | Friction unknown |
| 7 | Submission pack | Outward gates |

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

- [x] **Alternative arm named and run** — `python3 scripts/eval_refusal_baseline.py` · `docs/QWEN-EVAL-GATE-2026-08-30.md`
- [x] **Ablation** — `python3 scripts/eval_refusal_ablation.py` · delta=0 on n=6; RC5 both false-GREEN
- [x] **External anchor** — `python3 scripts/eval_external_anchor.py` · live rightsstatements.org (EA1/EA2)
- [ ] **Holdout frozen before the first tuning pass.**
- [x] **Baseline steelmanned** — raw rows printed by eval scripts; RC5 false-GREEN both arms
- [x] **Statistic matched to n** — Wilson 95% CI + McNemar in baseline/ablation scripts
- [ ] **Scorer symmetrical** — nothing only our system can emit; judge from delivered output for every arm.
- [ ] **Cost from billing**, with the price card's date stated.
- [x] **Offline path with no API key.**
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
| **1** | **Deploy the desk** | Oscar | **LIVE: https://agent-science-33kamss2jq-uc.a.run.app** (probed 2026-08-30: `gemini: true` vertex:hack-fleet, `parallel: true`, `engine_default: adk`). Hosted URL; keys via Secret Manager; `deploy.sh` only |
| **2** | **The registry has a face** | build | Query → SOURCED/UNSOURCED/UNKNOWN; browsable |
| **3** | **Backfill + compound exhibit** | build | Orphan-works A/B shows Parallel drop |
| **4** | **A second subject** | build | Dust-bowl chain; receipt honest |
| **5** | **Agent Builder as default** | build | ADK on default `/clear`; receipt `engine: adk` locally |
| **6** | **Design partner loop** | Oscar + build | One lead; friction in CURSOR-LOG |
| **7** | **Submission pack** | Oscar | Public repo, video, Devpost |

---

## NOW — stack product · all websearch routes here (2026-08-31)

**Product:** verified websearch companion for the whole fleet — registry first, Parallel+verify on miss.

### Surfaces (pick one)
| Surface | Command |
|---------|---------|
| **MCP** | `science_search` — installed in `~/.cursor/mcp.json` via `scripts/install-mcp.sh` |
| **CLI** | `python3 -m clearance search "query"` |
| **HTTP** | `GET/POST /search` · `/registry` · `/ingest` · `/stats` |
| **Desk** | `python3 -m clearance serve` or hosted `/` |

### Boot once
```bash
python3 scripts/boot_registry.py   # fleet research-corpus → 176 registry rows
```

### Docs
- `AGENTS.md` — fleet rule: use Agent Science instead of raw web search
- Hosted compound + eval gates shipped (cloud lane)

### Oscar
- `bash deploy.sh` — ships `/search` + MCP stack to Cloud Run
- Video · Devpost · public repo

---

## LOG (prior)

| When | What | Command | Outcome |
|------|------|---------|---------|
| 2026-08-31 | Vision wiring | boot + tests | `/registry` · run_history · 176 registry rows |
| 2026-08-30 night | Live compound hosted | cloud lane | RECEIPT-live-compound exhibit |
| 2026-08-30 start | Baseline claimed 72/72 but cache missing | `python3 tests/test_watch_it_go_red.py` | **13 fail + TypeError** — no `documents.json` |
| 2026-08-30 | EUR-Lex live fetch | `urllib` to eur-lex | **HTTP 403** — seeded from fixture |
| 2026-08-30 | Cache seed | `python3 scripts/seed_document_cache.py` | documents + searches on disk |
| 2026-08-30 | Controls green | `python3 tests/test_watch_it_go_red.py` | **72/72** |
| 2026-08-30 | ADK engine tests | `python3 tests/test_adk_default_path.py` | **5/5** |
| 2026-08-30 | Eval gate | `python3 scripts/eval_refusal_baseline.py` | baseline=shipping=5/6; RC5 both false-GREEN |
| 2026-08-30 | Live compound | env keys | **BLOCKED** — doc written |
| 2026-08-30 | Cold clone path | `git clone --no-local file://… && seed && test_watch_it_go_red` | **72/72** |
| 2026-08-30 | google-adk dep | `pip install google-adk==2.7.1 && python3 -c "…version…"` | **2.7.1** (not preinstalled on VM; in `requirements.txt`/Dockerfile) |
| 2026-08-30 | Full suite | 9× `python3 tests/test_*.py` | **104/104** |
| 2026-08-30 | Push gate | `git push origin main` | **83d1f7a** on origin/main |
| 2026-08-30 night | Ablation eval | `python3 scripts/eval_refusal_ablation.py` | **5/6=0.833** tied shipping; RC5 both false-GREEN |
| 2026-08-30 night | Docs gate | `python3 scripts/bench_check_docs.py` | **109/109** match SUBMISSION-PACK |
| 2026-08-30 night | Partner runtime | `python3 tests/test_partner_runtime.py` | **5/5** |
| 2026-08-30 night | Hosted ADK | `curl -s …/health` | **`engine_default: adk`** — slice 5 hosted done |
| 2026-08-30 night | Cold clone | `git clone file://… && seed && test_watch_it_go_red` | **72/72** |
| 2026-08-30 night2 | Baseline missing cache | `python3 tests/test_watch_it_go_red.py` | **13 fail + TypeError** — re-seeded |
| 2026-08-30 night2 | Cache seed | `python3 scripts/seed_document_cache.py` | **72/72** restored |
| 2026-08-30 night2 | Hosted compound | `POST /clear` compound-mini A/B | **2→1 Parallel, hits=2, pass** |
| 2026-08-30 night2 | Hosted /clear | dust-bowl one-liner | **engine=adk, parallel_calls=1** |
| 2026-08-30 night2 | External anchor | `python3 scripts/eval_external_anchor.py` | **2/2 tied** baseline=shipping |
| 2026-08-30 night2 | Eval stats | `python3 scripts/eval_refusal_baseline.py` | Wilson CI + McNemar p=1.0 |
| 2026-08-30 night2 | Cold clone script | `bash scripts/verify_cold_clone.sh` | **all gates green** |

---

*Update NOW after every slice. Oscar owns slice 1 deploy and submission gates.*
