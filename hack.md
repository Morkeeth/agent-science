---
doc: hack
project: Agent Science
phase: SHIP
last-touched: 2026-09-01 00:20 UTC
canonical: true
event: Agentic Cinema · Parallel track · deadline 2026-09-09 14:00 PDT
supersedes: docs/PHASE0-LADDER.md ClickHouse-track note (runtime track is Parallel)
---

# hack.md — Agentic Cinema constitution + handbook pass

**Repo:** Morkeeth/agent-science · **Event:** Agentic Cinema · Sep 9 2026 14:00 PDT  
**Spine:** **Agent Science** — the truth layer for what people believe and use. Companion (B) lead; clearance (A) on the same layer. Verify-or-refuse; registry compounds.  
**Constitution:** verbatim span or REFUSE — never paraphrase. No public repo until keys rotated. No rename. No `--set-env-vars` secrets. Slice 1 deploy/keys/video/Devpost: Oscar only.

> **Handbook:** ladder + judge pack below. **Living status:** `docs/STATUS.md` · `CLAUDE.md`  
> Detail: `docs/MOONSHOT-MEMO-2026-08-31.md` · `VISION-2026-08.md` · `AGENTS.md`

---

## 🪜 HANDBOOK LADDER (~70% elapsed · 9 days left)

| Phase | Gate | Status |
|-------|------|--------|
| 0 · Entry | Kill condition + hours named | ⚠️ `PHASE0-LADDER` — Oscar hours/kill still open |
| 1–4 · Spec → Build | Partners + registry + compound + ADK | ✅ slices 1–5 shipped |
| **5 · Exhibit** | Stranger one-click on hosted URL | ✅ `long_run_goal.sh` **19/19** + `new_user_trial.sh` |
| **6 · Freeze** | Oscar cold browser, degraded path | ⛔ video missing · logged-out Devpost unchecked |
| **7 · Submit** | Devpost + public repo + sealed prediction | ⚠️ repo **PUBLIC** · sealed ✅ · video + Devpost ⛔ |
| 8 · Post-result | Winners read, lesson distilled | — |

**#85:** video is the hard-fail artifact — not more build. **#72:** seal prediction before submit button.

---

## 📦 JUDGE PACKAGE (handbook 5-pack)

| Slot | Line |
|------|------|
| **Category** | Truth layer for what people believe and use — blogs, docs, stars, research, clearance |
| **One user** | Fleet dev / agent operator who websearches daily *(volume)*; E&O producer *(paying vertical)* |
| **Killer demo** | Hosted Run A → Run B: `corpus_hits` rise · `parallel_calls` drop on fresh subject — under 60s |
| **One visual** | `/popular/ui` hit-rate strip + compound metrics side-by-side on desk |
| **Why now** | Agentic Cinema + E&O/AI-training handshake stall on asset-level provenance; Parallel track requires runtime search |

**Anti-convergence wedge:** *PeriodCheck proves the first script. Agent Science proves the second one costs less.*

**Track brief first screen (rubric 30/30/25/15):** fact-checking for media content — verbatim evidence or named refusal for every claim in a production script.

---

## ⭐ NORTH STAR

Paste a documentary script; get every checkable claim back as a verbatim quote with its source URL, or UNSOURCED with a named reason — so a production can insure and release without guessing.

**Company north star (post-hack):** the truth dictionary for agent work — ask once, verify once, free forever; the most-searched things get cheaper for everyone.

## 📣 PROMISE LINE

**You get:** a gap report where every claim is SOURCED (exact passage + citation) or UNSOURCED (actionable cause).  
**Constraint:** if the document does not contain the exact passage, refuse — never paraphrase, never infer.

**Day-two user:** agent operator who runs `science_lookup` before raw web search; licensing lead who needs the gap report; archive manager who watches the shelf grow from fleet usage.

---

## 🏁 FIELD — Parallel track (measured 2026-08-31)

| Entry | Threat | Our answer |
|-------|--------|------------|
| [PeriodCheck](https://github.com/ahsan3274/periodcheck) | **#1** — 13/13 live, PDF ingest, evidence UI, bounded Parallel, `live-evaluation.json` | Lose first-run UX; **win compound economics + structural refuse** |
| [Clearance Compass](https://github.com/rumi7911/Clearance-Compass) | Same clearance wedge + ClickHouse agent memory | Win **verbatim-or-REFUSE**; they may win "studio pipeline" narrative |
| [Genesis OS](https://github.com/MoreSalamander/01-genesis-parallel) | Mission ledger, nested questions, evidence lineage | Different buyer (studio intel); overlap on verification states |
| [Lienmark](https://github.com/lx-singw/lienmark) | Rights clearance + immutable audit ledger | Collision on clearance; we have dictionary + compound |
| [AttestDB](https://github.com/omic/attest) | Closest **product shape** — claim DB, popularity, retraction | We have span verify + refuse pole; borrow `content_id` later |
| [Plotkraft](https://github.com/0xhaz/plotkraft) · [Auteur](https://github.com/sodiq-code/auteur) | Writers' room / continuity — adjacent, not same primitive | Category fit risk if judges bucket all as "script tools" |

**Not in field:** ArkivX, external "truths by agentic coders" feed — **no such ingest exists**; see §WEBSEARCH DATA.

**Published bar:** PeriodCheck has public repo + Devpost + live eval. We have **hosted URL** — still need **video + public repo** to match.

---

## 🔍 WEBSEARCH & TRUTH DICTIONARY

### Flows

| Flow | Entry | Tier | When |
|------|-------|------|------|
| Daily lookup | `science_lookup` · `GET /search?live=false` | free → cheap → live | **Default** for fleet |
| Fresh discovery | `science_search` · `live=true` | live (Parallel) | Dictionary miss |
| Script clearance | `POST /clear` | live + ADK | Hackathon demo · E&O vertical |
| Browse shelf | `/registry` · `/popular/ui` | free | Judges · ops |
| Grow shelf | `zup dictionary ingest` | — | After every research session |

### Cost tiers

1. **free** — registry exact replay + alias hit  
2. **cheap** — URL routing (CELEX, arXiv, rights vocab) + fetch, no Parallel  
3. **live** — Parallel + Gemini on miss  

### Data pipeline (where "the science" lives)

```
fleet websearch → research-corpus/ [CLAIM][URL]
                → boot_registry.py / zup dictionary ingest
                → refusal_log.db + GCS dictionary
                → query_analytics → /popular → alias + routing fixes
```

| Source | What it is |
|--------|------------|
| `research-corpus/*.md` | ~22 fleet research files — each websearch as `[CLAIM]` + `[URL]` |
| `refusal_log.db` / GCS | Registry of sourced + refused claims — reuse = 0 Parallel |
| `truth-dictionary/aliases.json` | Casual phrasings → canonical queries |
| Live clearance | Parallel → fetch → structural verbatim verify |

**Not wired:** ArkivX · ClickHouse (was Phase 0 ideation; **runtime track is Parallel**) · external archive APIs.

### Live stats (hosted, 2026-08-31)

- **185 claims** · hit rate **0.72** · **18 queries logged** · **9 reuses**  
- Top popular: `2012/28/EU` (8 asks) — alias fragmentation on `Directive 2012/28/EU` still open  
- Flywheel **architecturally done, adoption-empty** — kill bar: `queries_logged < 50` in 4 weeks = slide deck only

### Known websearch issues

| Issue | Symptom | Mitigation |
|-------|---------|------------|
| EUR-Lex 403 | Live fetch blocked | CELEX routing + fixtures; free tier for `2012/28/EU` |
| Alias fragmentation | Short form SOURCED, long form refused | Fix top `/popular` miss — `aliases.json` |
| Warm shelf | Reused subject → A=0 Parallel | Video: **fresh subject** or show `corpus_hits` not Parallel drop |
| Orphan-works hosted B | Run B **503** | Offline receipt authoritative; don't claim full script on video |
| C5 headline refuse | "94% of film archives" → `search_found_no_admissible_source` | **Video beat** — product refused our own pitch |
| Keys leaked | Plaintext in old Cloud Run revision | **Oscar only** — rotate before public repo |

### Stranger path (one command)

```bash
bash scripts/new_user_trial.sh
# lookup 2012/28/EU → SOURCED free · NOT_CLEARED on miss · corpus_hits ≥ 1 on repeat
```

---

## 🏆 WINNER ANGLES (Sep 9 + company)

*Queued for EYES multi-model review — claims below are falsifiable.*

### What wins Sep 9 (Parallel track rubric)

| Angle | Claim | Falsify when |
|-------|-------|--------------|
| **Compound economics** | Only entry showing A→B Parallel drop + corpus hits on **hosted** URL | PeriodCheck ships same demo |
| **Honest refuse on camera** | UNKNOWN row with named cause + C5 beat (headline refused) | Judges can't read span on screen |
| **Truth dictionary flywheel** | `/popular/ui` shows real queries driving free tier | `queries_logged` stays &lt; 20 at submit |
| **M&E words first** | E&O / clearance / provenance in first 10s of video | Opens with eval tables |
| **Second buyer** | 247/600 flip when buyer use-case changes (`shift-ai-training` fixture) | Not in video |

### New angles to explore (not yet built — post-submit or stretch)

| Angle | Thesis | Build cost |
|-------|--------|------------|
| **Fleet corpus as moat** | "Truths by agentic coders" — shared GCS dictionary across Oscar's repos; every fleet research session grows everyone's free tier | M — GCS shared dict + auth |
| **Negative space product** | Sell the **refusal map** — "here's what we cannot prove about your library" as the gap report buyers pay for | S — already in registry |
| **Insurance API** | Export gap report as E&O-ready PDF with stable claim IDs (PeriodCheck has evidence IDs; we have term + cause) | M |
| **Buyer-context flip** | Same asset, different verdict by licensee intent — already in dust-bowl + shift fixtures; needs UI | S |
| **Attest bridge** | Emit ClaimReview / Attest-compatible records from sourced rows — interoperability without pivoting stack | M |
| **Patent / prior-art routing** | Extend `routing.py` for USPTO, EPO, scholar — dev-truth volume beyond M&E | S |
| **Witness × Science** | Agent Work Record cites Agent Science rows as evidence for "agent said X, corpus said Y" | L — fleet integration |
| **Anti-slop for agents** | `science_lookup` as fleet policy gate — no raw web without citation attempt | S — habit + hook exists |

### What does NOT win (explicit kills)

- More eval gates / pytest on Devpost — **zero rubric weight** (Qwen lesson)  
- ClickHouse index — wrong primitive for discovery  
- Competing on Document AI PDF ingest — PeriodCheck owns  
- Pivot to confidence scores — collides with refuse spine  

---

## 🗺 ROADMAP

### Sep 9 critical path (Oscar gates — stop building past this)

| # | Slice | Done when | Owner |
|---|-------|-----------|-------|
| 1 | **Video ≤180s** | Public YouTube/Vimeo URL on Devpost | Oscar |
| 2 | **Rotate keys + public repo** | MIT license visible; no secrets in history | Oscar |
| 3 | **Devpost + sealed prediction** | `docs/SUBMISSION-PACK-2026-08-29.md` pasted; logged-out page verified | Oscar |
| 4 | **Fix top popular alias** | `Directive 2012/28/EU` → free hit | build (30 min, non-blocking) |

### Week 1 post-submit (product flywheel)

- Fleet habit: `science_lookup` default · `popular` weekly · `zup dictionary ingest` after research  
- Fix top 3 `/popular` optimization targets  
- `dictionary_hit_rate ≥ 0.80` · `queries_logged ≥ 200` (4-week product test)

### Month 1 (if flywheel spins)

- Shared fleet dictionary on GCS (multi-repo read, single write path)  
- Attest-style `content_id` + retraction cascade on sourced rows  
- Design partner loop (slice 6) — one archive/licensing lead; friction in `docs/DESIGN-PARTNER-LOOP.md`  
- E&O export format · buyer-context UI for shift flip  

### Month 3+ (company bets)

- Insurance / E&O channel partnership  
- Witness integration — claims in agent reports cite dictionary rows  
- Analytics-only ClickHouse *(if ever)* — query logs at fleet scale, not discovery  

---

## ❓ OPEN QUESTIONS

- **Rotate the leaked Parallel/Gemini keys — OSCAR ONLY.** Plaintext Cloud Run revision cannot be un-written; rotate before public repo.
- ~~RC5 substring false-GREEN~~ **CLOSED 2026-08-31** — `docs/FINDING-semantic-guard-2026-08-31.md`.
- Design partner session — Oscar outreach (slice 6).
- **EYES:** do winner angles survive PeriodCheck + Clearance Compass field? (next step)
- **Alias:** `Directive 2012/28/EU` — **CLOSED 2026-08-31** (aliases + SOURCED-only replay).

## CONSTITUTION

- Verbatim span or REFUSE — `Verdict.__post_init__` enforces citation.
- Locator untrusted; verifier structural; model never authors verdict.
- No plaintext secrets in repo or deploy surfaces (control scans tree + git log).
- Outward acts (deploy, public repo, Devpost, video) — Oscar only.
- Do not tick a box whose done-when was not RUN; say the command.
- `science_lookup` defaults `live=false` — flywheel requires cheap path first.

## PLAN (risk-first slices)

| # | Slice | Risk | Status |
|---|--------|------|--------|
| 1 | Deploy desk | Keys leak | ✅ LIVE |
| 2 | Registry face | False SOURCED in UI | ✅ `/registry` hosted |
| 3 | Compound exhibit | Compounding unproved | ✅ fresh subject hosted pass |
| 4 | Second subject | Cross-subject collision | ✅ dust-bowl receipt |
| 5 | ADK default path | Agent Builder not on path | ✅ `engine_default: adk` |
| 6 | Design partner loop | Friction unknown | ⛔ Oscar |
| 7 | Submission pack | Outward gates | ⚠️ repo public · sealed · **video + Devpost** |

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

- [x] **Alternative arm named and run** — `python3 scripts/eval_refusal_baseline.py` · **re-run 2026-08-31: baseline 5/6 = 0.833, shipping 6/6 = 1.000, delta +1, McNemar p=1.0000 (b=0 c=1) — a real delta where 08-30 had a tie, and NOT significant at n=6; the CIs overlap [0.436,0.970] vs [0.610,1.000]**
- [x] **Ablation** — `python3 scripts/eval_refusal_ablation.py` · **re-run 2026-08-31: ablation 5/6, shipping 6/6, delta +1, McNemar p=1.0000.** (2026-08-30 reading, before the semantic guard: delta=0, RC5 false-GREEN in both arms.)
- [x] **External anchor** — `python3 scripts/eval_external_anchor.py` · live rightsstatements.org (EA1/EA2)
- [ ] **Holdout frozen before the first tuning pass.**
- [x] **Baseline steelmanned** — raw rows printed by eval scripts; RC5 is now the single discordant item (baseline GREEN, shipping UNKNOWN)
- [x] **Statistic matched to n** — Wilson 95% CI + McNemar in baseline/ablation scripts
- [ ] **Scorer symmetrical** — nothing only our system can emit; judge from delivered output for every arm.
- [ ] **Cost from billing**, with the price card's date stated.
- [x] **Offline path with no API key.**
- [x] **Honesty & limitations** section carrying our worst number — README §Honesty & limitations; PITCH first screen
- [x] **Answer the track brief in the track's own words on the first screen** — judge pack § above; Devpost §0 rewritten 2026-09-02 (`docs/SUBMISSION-PACK-2026-08-29.md` §0: M&E fact-check lead → truth-layer pivot)
- [ ] **Video verified attached and public on the live entry page, from a logged-out browser** — not in a checklist file, on the page.
- [ ] **Every artifact claim measured at the submitted commit.** Four retros of that loss failed this row.

Full record: `fleet-ops (internal)/retros/QWEN-LOSS-RETRO-2026-08-30.md` (corrected) ·
`QWEN-FIELD-TEST-2026-08-30.md` (the n=40 falsification) · playbook lesson 97.

---

## 🎯 NOW — AS-SHIP-4 submit pack + gate + receipt (build lane)

**Slice:** Freeze Devpost submission pack · fix compound number contradictions · run full gate · write ship receipt.

### Build

- [x] Devpost paste §0 — track brief (M&E fact-check / E&O) **then** truth-layer pivot
- [x] Compound numbers unified to **A=1 → B=0** in pitch docs (`PITCH.md`, `PITCH-TOMORROW.md`, `SUBMISSION-PACK` §3)
- [x] `SUBMISSION.md` — video marked built, Oscar uploads (`demo/demo-final.mp4`)
- [x] `docs/STATUS.md` — phase 6/7 gates honest
- [x] `bash scripts/full_gate.sh` → **FULL GATE OK** (2026-09-01T20:24:08Z)
- [x] `docs/RECEIPT-ship-2026-09-02.md`

### Verify (one command each)

```bash
rg 'A=2|2 Parallel' docs/ PITCH.md SUBMISSION.md README.md   # pitch docs clean
bash scripts/privacy_grep.sh                                    # 0 hits
bash scripts/full_gate.sh                                       # FULL GATE OK
```

### BLOCKED (Oscar outward)

- Video upload · Devpost submit · logged-out verify

---

## 🎯 NOW (prior) — Partner integrations night wave (build lane)

**Slice:** P1–P7 partner integrations + promise line + eval gate + compound exhibit — all four partners provable at runtime.

### Build (shipped 2026-09-01 night)

- [x] P1 Promise line — README opening + PITCH first screen (outcome · proof · constraint)
- [x] P2 Partner doc verified — `docs/PARTNER-INTEGRATIONS-2026-08-30.md` + hosted `/health` + `/partners`
- [x] P3 ADK default path — `engine_default: adk` on hosted `/health`
- [x] P4 Qwen eval gate re-run — baseline 5/6 vs shipping 6/6, delta +1
- [x] P5 Compound exhibit — compound-mini PASS (A=2→B=1 Parallel, corpus_hits=1)
- [x] P6 SUBMISSION-PACK truth refresh — `bench_check_docs.py` 127/127 match
- [x] P7 Design partner loop — `docs/DESIGN-PARTNER-LOOP.md` (slice 6 prep, pre-existing)

### Verify (one command each)

```bash
python3 scripts/seed_document_cache.py && python3 tests/test_watch_it_go_red.py   # 72/72
curl -s https://agent-science-568004190078.us-central1.run.app/health | python3 -m json.tool
python3 scripts/bench_check_docs.py                                                # 127/127
python3 scripts/eval_refusal_baseline.py && python3 scripts/eval_refusal_ablation.py
bash scripts/full_gate.sh                                                          # FULL GATE OK
```

### Receipt

- `docs/RECEIPT-partner-integrations-night-2026-09-01.md`

### BLOCKED

- Orphan-works full script Run B — **504 Gateway Timeout** at 300s (Run A ok, 7 Parallel). Do not claim on video.

---

## 🎯 NOW (prior) — WOW websearch transparency (build lane)

**Slice:** S1–S8 truth layer night — transparency panes, CONTRARY stamp, stack-fit, community notes, truths dashboard.  
**Oscar film:** `python3 -m clearance.stack_cli visibility "ralph loop agentic" --full` → pane 1b + CONTRARY stamp.

### Build (shipped 2026-08-31 night)

- [x] S1 transparency — angles / shallow / imbalance (`visibility --full`)
- [x] S2 `CONTRARY_TO_RESEARCH` + ralph-loop demo + tests
- [x] S3 `stack-fit` + `truth skill --fit`
- [x] S4 HN live + ARKIVX snapshot (`refresh_hn_signals.py`)
- [x] S5 community notes CLI
- [x] S6 `/truths/ui` + video script beats
- [x] S7 vision + STATUS + receipt
- [x] S8 full gate — `bash scripts/full_gate.sh` → **FULL GATE OK** 2026-08-31T21:23:08Z

### Verify (one command each)

```bash
python3 -m clearance.stack_cli visibility "ralph loop agentic" --full --no-personal | head -30
python3 -m clearance.stack_cli lookup "ralph loop agentic practice"
python3 -m clearance.stack_cli stack-fit "science_lookup MCP fleet"
python3 tests/test_visibility_transparency.py && python3 tests/test_contrary_verdict.py
bash scripts/full_gate.sh
```

### Receipt

- `docs/RECEIPT-truth-layer-night-2026-08-31.md`

---

## 🎯 NOW (prior) — Phase 6 freeze + video (Oscar outward)

**Slice:** handbook phase 6 — Oscar drives degraded judge path and films compound + refuse.  
**Hard-fail artifact:** ≤180s video with hosted URL readable · `docs/VIDEO-SCRIPT-2026-08-29.md`

### LIVE

**URL:** https://agent-science-568004190078.us-central1.run.app  
**Revision:** agent-science-00012-98d · **182 claims** · hit rate 0.75

```bash
**Replay long run:** `bash scripts/long_run_goal.sh` → `docs/LONG-RUN-RECEIPT-2026-08-31.md`
curl -s …/popular/ui                    # flywheel face for judges
curl -s '…/search?q=Directive+2012/28/EU&live=false'  # SOURCED free tier
```

**Compound note:** fresh subject → `parallel_calls` drops + `corpus_hits ≥ 1`. Warm dictionary may show A=0 Parallel — still valid if corpus hits rise.

### Oscar (outward acts only)

**Follow-up:** `docs/SUBMIT-FOLLOW-UP-2026-08-31.md` · checklist `docs/OSCAR-SUBMIT-CHECKLIST-2026-08-31.md`

1. Record video (`docs/VIDEO-SCRIPT-2026-08-29.md`)  
2. Devpost submit + video URL  
3. Logged-out verify Devpost page  
4. Rotate Vertex/Gemini if needed (Parallel via deploy)  

### Build (shipped 2026-08-31 PM)

- [x] Alias canonical `2012/28/EU` + SOURCED-only exact replay (`clearance/dictionary.py`)
- [x] Deploy `agent-science-00012-98d` — `Directive 2012/28/EU` SOURCED free on hosted
- [x] EYES receipt · video script reorder · Oscar checklist

### Verify (one command each)

```bash
python3 scripts/seed_document_cache.py && python3 tests/test_watch_it_go_red.py  # 72/72
python3 tests/test_partner_runtime.py                                             # 6/6
python3 tests/test_parallel_integration.py                                        # 6/6
curl -s https://agent-science-568004190078.us-central1.run.app/partners          # judge manifest
bash scripts/verify_cold_clone.sh                                                 # stranger path
```

### Receipts

- `docs/RECEIPT-live-compound-exhibit-2026-08-31.md` — hosted compound (fresh pass; orphan-works B 503)
- `docs/PARTNER-INTEGRATIONS-2026-08-30.md` — all four partners on path
- `docs/PARTNER-INTEGRATION-RESEARCH-2026-08-31.md` — field comparison + judge playbook
- `docs/MOONSHOT-MEMO-2026-08-31.md` — flywheel + field detail

---

## LOG (prior)

| When | What | Command | Outcome |
|------|------|---------|---------|
| 2026-09-02 | AS-SHIP-4 submit pack | `full_gate.sh` · `privacy_grep.sh` · `rg A=2` | **FULL GATE OK** · 0 privacy hits · Devpost §0 track-brief lead · receipt |
| 2026-09-01 night | Partner integrations wave | `curl …/health` · compound-mini · `full_gate.sh` | **4/4 partners** on hosted · compound PASS · 127/127 · promise line shipped |
| 2026-09-01 hammer | Hosted visibility + demo | `./deploy.sh` · `demo_truth_layer.sh` | `/visibility/ui` live · 127/127 gate |
| 2026-09-01 overnight | Deploy + pitch pack | `./deploy.sh` | rev 00018 · PITCH-TOMORROW |
| 2026-08-31 night | Truth layer night S1–S8 | `bash scripts/full_gate.sh` | **FULL GATE OK** · transparency · CONTRARY · stack-fit · notes · receipt |
| 2026-08-31 11:27Z | Full gate | `bash scripts/full_gate.sh` | **FULL GATE OK** · STATUS.md · DEVPOST-READY · CLAUDE.md |
| 2026-08-31 PM | Handbook pass | hack.md rewrite | ladder · field · websearch · roadmap · winner angles |
| 2026-08-31 L5 | Semantic guard RED first | `python3 tests/test_semantic_guard.py` (null guard) | **4 fail / 9 pass** — watched red before implementing |
| 2026-08-31 L5 | Semantic guard measured | `python3 scripts/eval_semantic_guard.py` | **gold 5/6 -> 6/6**; registry **0/313** verdicts changed; **8/27** better spans |
| 2026-08-31 L5 | RC5 promoted | `python3 tests/test_refusal_correctness.py` | `engine_limit` dropped; enforced pole; **all passed** |
| 2026-08-31 L5 | C3 secret control audit | `python3 tests/test_secret_surfaces.py` (old rule) | **3 of 7 leak shapes MISSED**; control's control graded a copy |
| 2026-08-31 L5 | C3 closed | `python3 tests/test_secret_surfaces.py` | **6/6** — 7/7 leaks caught, 0/4 safe forms flagged |
| 2026-08-31 L5 | Registry face | `python3 tests/test_registry_surface.py` + rendered 1280/390 | **11/11**; 12/28 sourced rows marked thin evidence |
| 2026-08-31 L5 | Full suite | 16x `python3 tests/test_*.py` | **all green** (watch_it_go_red 72/72) |
| 2026-08-31 | Vision wiring | boot + tests | `/registry` · run_history · 176 registry rows |
| 2026-08-31 | Deploy + trial | `deploy.sh` · `new_user_trial.sh` | LIVE · compound PASS · 185 claims |
| 2026-08-30 night | Live compound hosted | cloud lane | RECEIPT-live-compound exhibit |
| 2026-08-30 | EUR-Lex live fetch | `urllib` to eur-lex | **HTTP 403** — seeded from fixture |
| 2026-08-30 night2 | Hosted compound | `POST /clear` compound-mini A/B | **2→1 Parallel, hits=2, pass** |
| 2026-08-31 | Compound fresh subject | `compound-fresh-c1eb52fe` A/B | **2→1 Parallel, hits=1, pass** |
| 2026-08-31 | Orphan-works hosted | `orphan-works-live-66d21d70` | **A ok (9 Parallel); B 503** |

---

*Update NOW after every slice. Oscar owns phase 6–7. Next: EYES on §WINNER ANGLES.*
