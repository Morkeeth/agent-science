# Submit follow-up — Agent Science · 2026-08-31

**Living board:** `docs/STATUS.md` · **Devpost form:** `docs/DEVPOST-READY.md`  
**Build lane:** IDLE — three Oscar clicks remain.

---

## ✅ Done (this session)

| Item | Evidence |
|------|----------|
| Cloud Run live | `agent-science-00014-p56` |
| Long run goal | `bash scripts/long_run_goal.sh` → **19/19** |
| Sealed prediction | `docs/SEALED-PREDICTION-2026-08-31.md` |
| PeriodCheck falsification doc | `docs/FALSIFICATION-PERIODCHECK-2026-08-31.md` |
| Video script (EYES order) | `docs/VIDEO-SCRIPT-2026-08-29.md` |
| Controls | 72/72 · partner 5/5 · cold clone · trial PASS |
| Secret scan | 6/6 |
| MIT LICENSE | in repo |
| Public repo | see below |

---

## ⛔ Oscar only (≈2 hours total)

### 1. Record video (~45 min)

```bash
open https://agent-science-568004190078.us-central1.run.app/
open https://agent-science-568004190078.us-central1.run.app/popular/ui
open agent-science/fixtures/shift-ai-training-vs-noncommercial.md
# Script: docs/VIDEO-SCRIPT-2026-08-29.md
```

**Lead:** E&O hook → SOURCED span → refuse → C5 beat → compound → buyer flip → URL.

### 2. Rotate keys (~15 min)

Parallel key rotated on last `deploy.sh` (Secret Manager v7). **Vertex/Gemini:** rotate if any key ever lived in plaintext env (see `hack.md` OPEN QUESTIONS).

### 3. Devpost submit (~30 min)

1. https://agentic-cinema.devpost.com/
2. Partner track: **Parallel**
3. Hosted URL: `https://agent-science-568004190078.us-central1.run.app`
4. Repo: `https://github.com/Morkeeth/agent-science`
5. Paste: `docs/SUBMISSION-PACK-2026-08-29.md` § Devpost block
6. Video URL (YouTube/Vimeo public)
7. Logged-out verify video plays on entry page

---

## Paste-ready fields

| Field | Value |
|-------|-------|
| **Project name** | Agent Science |
| **Tagline** | Every claim sourced verbatim — or refused with a named reason. |
| **Hosted URL** | https://agent-science-568004190078.us-central1.run.app |
| **Repo** | https://github.com/Morkeeth/agent-science |
| **Track** | Parallel |
| **License** | MIT |

---

## Sealed prediction (for Devpost “what we predicted”)

> Second `/clear` on same subject: `corpus_hits ≥ 1` and `parallel_api_calls` B ≤ A.  
> **Measured:** A=1 → B=0 Parallel, corpus_hits=1 (`LONG-RUN-RECEIPT`).  
> **Hash:** `a510bfa72bc5dad770ee2db800d4abc83da89e9f97bbb056232404b3fa5292b3`

---

## Replay commands

```bash
bash agent-science/scripts/long_run_goal.sh
bash agent-science/scripts/new_user_trial.sh
bash agent-science/scripts/verify_cold_clone.sh
```

**Deadline:** 2026-09-09 14:00 PDT
