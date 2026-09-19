---
doc: status
project: Agent Science
canonical: true
last-updated: 2026-09-19T00:12:00Z
deadline: 2026-09-09T14:00:00-07:00
---

# STATUS — Agent Science (living board)

> **For Claude / fleet:** this file is the single “where we are” surface.  
> `hack.md` = process · `CLAUDE.md` = entry · this file = gates + evidence.

**Last gate run:** 2026-09-19 — partner honesty land · `bench_check_docs.py` **129/129** · `test_watch_it_go_red.py` **72/72** · live baseline **naive 3/3 / shipping 0/3** on `00028-hed` · in-tree checklist+film fix on branch awaiting Oscar deploy

---

## TL;DR (Oscar returns)

| State | Detail |
|-------|--------|
| **Product noun** | **Agent Science** — truth layer for what people believe and use · B lead · A on the same layer |
| **Product** | LIVE on Cloud Run · public repo · sealed prediction |
| **Build lane** | WOW websearch transparency · CONTRARY stamp · stack-fit · community notes · `/truths/ui` |
| **Oscar** | **Film 30 min** — `docs/PITCH-TOMORROW.md` · transparency WOW first · Devpost paste ready |
| **Film lead** | Ask → sourced/refuse → free on re-ask · ≥2 domains · E&O as *a* truth not the only story |

---

## Handbook ladder

| Phase | Gate | Status |
|-------|------|--------|
| 0–4 Build | Partners, registry, compound, ADK | ✅ |
| 5 Exhibit | Stranger one-click hosted | ✅ `long_run_goal.sh` 19/19 |
| 6 Freeze | Oscar cold browser + film | ⛔ **video** |
| 7 Submit | Devpost + sealed + public repo | ⚠️ repo public · sealed ✅ · **Devpost + video** ⛔ |

---

## Gates (measured)

| Gate | Result | Command / doc |
|------|--------|----------------|
| Mutation controls | **72/72** | `test_watch_it_go_red.py` |
| All test suites | **129/129** | `bench_check_docs.py` (re-run 2026-09-18) |
| Secret scan | **6/6** | `test_secret_surfaces.py` |
| Partner runtime | **8/8** + parallel **6/6** | `test_partner_runtime.py` + `test_parallel_integration.py` |
| ADK default | **5/5** | `test_adk_default_path.py` |
| Hosted partner health (live) | ⛔ RED on `00028-hed` | `eval_hosted_partner_baseline.py` · naive PASS / shipping FAIL · needs Oscar deploy |
| Judge film surfaces (local) | ✅ | `prove_judge_surfaces_local.sh` · live still 303 until deploy |
| Registry surface | **16/16** | `test_registry_surface.py` |
| Cold clone | ✅ | `verify_cold_clone.sh` |
| Hosted long run | **19/19** | `long_run_goal.sh` |
| Stranger trial | ✅ | `new_user_trial.sh` |
| Sealed prediction | ✅ | `SEALED-PREDICTION-2026-08-31.md` |
| Public repo | ✅ | github.com/Morkeeth/agent-science |
| Video | ⛔ | `VIDEO-SCRIPT-2026-08-29.md` |
| Architecture pack | ✅ | `docs/ARCHITECTURE.md` + `docs/assets/` |
| Devpost | ⛔ | `DEVPOST-READY.md` + paste pack |

---

## Hosted (now) — measured 2026-09-18 at object

| | |
|---|---|
| **URL** | https://agent-science-568004190078.us-central1.run.app |
| **Revision** | `agent-science-00028-hed` (curl `/health`) |
| **Health** | ⛔ stripped — only `ok`/`service`/`mode`/`revision` · **no** `engine_default` / `gemini` / `parallel` |
| **Partners** | ⛔ `/partners` → **303** login HTML (not JSON) |
| **Film** | ⛔ `/truths/ui` · `/visibility/ui` → **303** login (not mounted on this revision) |
| **In tree (undeployed)** | full `health_payload` + public judge surfaces + checklist not hardcoded |

**Do not cite older STATUS rows** that claimed `00018-n4s` / `engine_default: adk` on live — those were nearer proxies than tonight's curl.

**Compound (sealed, historical):** `longrun-0831-1320` A=**1** → B=**0** Parallel · B `corpus_hits=1`

---

## Oscar checklist (only human work left)

1. **Read** `docs/PITCH-TOMORROW.md` — 30s pitch + morning plan
2. **Record** ≤180s — transparency WOW first · `docs/FILM-SCOUT-COMMANDS.md`
3. **Devpost** — `docs/DEVPOST-READY.md` (elevator pitch updated)
4. **Verify** logged-out: video on live entry page

---

## Do not on video / Devpost

- Full orphan-works script compound (B **503** hosted)
- Flywheel metrics as headline (low query count)
- Lead with Parallel-drop only (PeriodCheck wins first-run UX)

---

## Replay

```bash
cd agent-science
bash scripts/full_gate.sh
```

---

## Session log

| When (UTC) | What |
|------------|------|
| 2026-09-18 00:15 | Partner night — hardcoded checklist RED · judge surfaces mounted in tree · baseline eval naive PASS/shipping FAIL · STATUS revision corrected to `00028-hed` |
| 2026-09-01 06:00 | **Hammer** — `/visibility/ui` hosted · demo_truth_layer.sh · README truth-layer lead · Devpost §0 |
| 2026-08-31 21:23 | Truth layer night — transparency, CONTRARY, stack-fit, community notes, `/truths/ui` (branch) |
| 2026-08-31 21:55 | Competitor research — websearch field map + steal angles → `RESEARCH-WEBSEARCH-COMPETITORS-2026-08-31.md` |
| 2026-08-31 20:35 | Full websearch rundown — `WEBSEARCH-FULL-RUNDOWN.md` + `visibility --full` (10 panes) |
| 2026-08-31 20:32 | Skill + `clearance visibility` / `science_visibility` — multi-pane websearch, not one answer |
| 2026-08-31 20:28 | **RULING:** Agent Science websearch = the truth layer (believe+use), not raw search+citations |
| 2026-08-31 20:30 | Truth layer > research — blogs + GitHub ★ field-signals + refresh script |
| 2026-08-31 20:26 | **RULING:** Agent Science = truth layer for what people believe and use (not citation wall) |
| 2026-08-31 20:25 | **RULING sharpened:** Agent Science = scientific coach with facts · B lead · A works with B on one shelf |
| 2026-08-31 20:24 | **RULING:** Agent Science = Companion (B) priority; Clearance (A) is a truth inside B — not a rename |
| 2026-08-31 20:25 | Grinder PRACTICES-CORPUS → Agent Science inspiration + seed claims + aliases |
| 2026-08-31 20:20 | Use-case pack beyond EU — 4 demo scripts, aliases, USE-CASES doc |
| 2026-08-31 16:10 | Architecture pack — ARCHITECTURE.md, diagrams, 6 hosted screenshots |
| 2026-08-31 14:10 | Partner deepen — `parallel-web` SDK, `/partners`, `search_id` receipts, research doc |
| 2026-08-31 11:30 | Full gate audit while Oscar away — STATUS.md · full_gate.sh · DEVPOST-READY · pack counts 117 |
| 2026-08-31 11:25 | Submit pass — sealed · public repo · falsification doc |
| 2026-08-31 11:22 | Long run goal 19/19 · Cursor goal complete |
| 2026-08-31 11:14 | Deploy 00014 · alias fix · handbook pass |

---

*Update `last-updated` + session log after every gate run.*
