---
doc: status
project: Agent Science
canonical: true
last-updated: 2026-08-31T11:28:00Z
deadline: 2026-09-09T14:00:00-07:00
---

# STATUS — Agent Science (living board)

> **For Claude / fleet:** this file is the single “where we are” surface.  
> `hack.md` = process · `CLAUDE.md` = entry · this file = gates + evidence.

**Last gate run:** 2026-08-31T11:27:44Z — `bash scripts/full_gate.sh` → **FULL GATE OK** (117/117 · 19/19 long run · trial OK)

---

## TL;DR (Oscar returns)

| State | Detail |
|-------|--------|
| **Product** | LIVE on Cloud Run · public repo · sealed prediction |
| **Build lane** | **IDLE** — nothing left before video |
| **Oscar** | **3 clicks:** record video → Devpost + video URL → logged-out verify |
| **Film lead** | E&O + refuse first (not compound) — `docs/FALSIFICATION-PERIODCHECK-2026-08-31.md` |

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
| All test suites | **117/117** | `tests/test_*.py` (see full_gate log) |
| Secret scan | **6/6** | `test_secret_surfaces.py` |
| Partner runtime | **5/5** | `test_partner_runtime.py` |
| ADK default | **5/5** | `test_adk_default_path.py` |
| Registry surface | **13/13** | `test_registry_surface.py` |
| Cold clone | ✅ | `verify_cold_clone.sh` |
| Hosted long run | **19/19** | `long_run_goal.sh` |
| Stranger trial | ✅ | `new_user_trial.sh` |
| Sealed prediction | ✅ | `SEALED-PREDICTION-2026-08-31.md` |
| Public repo | ✅ | github.com/Morkeeth/agent-science |
| Video | ⛔ | `VIDEO-SCRIPT-2026-08-29.md` |
| Devpost | ⛔ | `DEVPOST-READY.md` + paste pack |

---

## Hosted (now)

| | |
|---|---|
| **URL** | https://agent-science-568004190078.us-central1.run.app |
| **Revision** | `agent-science-00014-p56` (re-deploy if unsure: `bash deploy.sh`) |
| **Health** | `engine_default: adk` · Parallel · Gemini |
| **Stats** | ~183 claims · hit rate ~0.70 · queries logged growing |

**Compound (sealed):** `longrun-0831-1320` A=**1** → B=**0** Parallel · B `corpus_hits=1`

---

## Oscar checklist (only human work left)

1. **Record** ≤180s — `docs/VIDEO-SCRIPT-2026-08-29.md`
2. **Devpost** — `docs/DEVPOST-READY.md` (all fields pre-filled)
3. **Verify** logged-out: video on live entry page
4. **Optional:** rotate Vertex/Gemini if leaked (`hack.md` OPEN QUESTIONS)

---

## Do not on video / Devpost

- Full orphan-works script compound (B **503** hosted)
- Flywheel metrics as headline (low query count)
- Lead with Parallel-drop only (PeriodCheck wins first-run UX)

---

## Replay

```bash
cd ~/CODE/cleared
bash scripts/full_gate.sh
```

---

## Session log

| When (UTC) | What |
|------------|------|
| 2026-08-31 11:30 | Full gate audit while Oscar away — STATUS.md · full_gate.sh · DEVPOST-READY · pack counts 117 |
| 2026-08-31 11:25 | Submit pass — sealed · public repo · falsification doc |
| 2026-08-31 11:22 | Long run goal 19/19 · Cursor goal complete |
| 2026-08-31 11:14 | Deploy 00014 · alias fix · handbook pass |

---

*Update `last-updated` + session log after every gate run.*
