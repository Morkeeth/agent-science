---
doc: status
project: Agent Science
canonical: true
last-updated: 2026-09-04T00:12:00Z
deadline: 2026-09-09T14:00:00-07:00
---

# STATUS — Agent Science (living board)

> **For Claude / fleet:** this file is the single “where we are” surface.  
> `hack.md` = process · `CLAUDE.md` = entry · this file = gates + evidence.

**Last gate run:** 2026-09-04 — `test_watch_it_go_red` **72/72** · `bench_check_docs` **127/127** · artifact-claims eval shipped (stale pack caught, then fixed)

---

## TL;DR (Oscar returns)

| State | Detail |
|-------|--------|
| **Product noun** | **Agent Science** — truth layer for what people believe and use · B lead · A on the same layer |
| **Product** | LIVE on Cloud Run · public repo · sealed prediction |
| **Build lane** | Artifact-claims gate + SUBMISSION-PACK truth refresh · null-arm steelman |
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
| Pack suites | **127/127** + truth-layer suites | `bench_check_docs.py` + `full_gate.sh` |
| Secret scan | **6/6** | `test_secret_surfaces.py` |
| Partner runtime | **6/6** | `test_partner_runtime.py` + `test_parallel_integration.py` |
| ADK default | **5/5** | `test_adk_default_path.py` |
| Registry surface | **16/16** | `test_registry_surface.py` |
| Artifact claims | **eval** | `eval_artifact_claims.py` — trust-doc baseline vs re-derive |
| Null arm | null 3/6 · ship 6/6 | `eval_null_arm.py` |
| Cold clone | ✅ | `verify_cold_clone.sh` |
| Hosted long run | **19/19** | `long_run_goal.sh` |
| Stranger trial | ✅ | `new_user_trial.sh` |
| Sealed prediction | ✅ | `SEALED-PREDICTION-2026-08-31.md` |
| Public repo | ✅ | github.com/Morkeeth/agent-science (public since 2026-08-22) |
| Video | ⛔ | `VIDEO-SCRIPT-2026-08-29.md` |
| Architecture pack | ✅ | `docs/ARCHITECTURE.md` + `docs/assets/` |
| Devpost | ⛔ | `DEVPOST-READY.md` + paste pack |

---

## Hosted (now)

| | |
|---|---|
| **URL** | https://agent-science-568004190078.us-central1.run.app |
| **Revision** | `agent-science-00018-n4s` · `parallel_sdk: true` · **`/truths/ui` live** |
| **Health** | `engine_default: adk` · gemini vertex · parallel-web SDK |
| **Stats (GET /stats, 2026-09-04T00:11Z)** | **306 claims** · hit rate **0.627** · queries_logged **279** · aliases **39** |
| **New** | `GET /visibility/ui` — full websearch panel for judges (film this) |
| **New** | `GET /truths/ui` — truths dashboard |

**Compound (sealed):** `longrun-0831-1320` A=**1** → B=**0** Parallel · B `corpus_hits=1`

**Honesty:** earlier STATUS carried the Aug-31 shelf snapshot (**n≈265 / hr≈0.80**) — stale on 2026-09-04 against live **n=306 / hr=0.627**. Re-derived at `GET /stats`; do not carry the old pair forward.

---

## Oscar checklist (only human work left)

1. **Read** `docs/PITCH-TOMORROW.md` — 30s pitch + morning plan
2. **Record** ≤180s — transparency WOW first · `docs/FILM-SCOUT-COMMANDS.md`
3. **Devpost** — `docs/DEVPOST-READY.md` (elevator pitch updated)
4. **Verify** logged-out: video on live entry page

---

## Do not on video / Devpost

- Full orphan-works script compound (B **504** hosted @ 300s ceiling)
- Flywheel hit-rate as headline (live **0.627**, not ~0.80)
- Lead with Parallel-drop only (PeriodCheck wins first-run UX)

---

## Replay

```bash
cd agent-science
bash scripts/full_gate.sh
python3 scripts/eval_artifact_claims.py
```

---

## Session log

| When (UTC) | What |
|------------|------|
| 2026-09-04 00:12 | Night wave — artifact-claims gate · null arm · pack/STATUS truth · stale 265/0.80 caught |
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
