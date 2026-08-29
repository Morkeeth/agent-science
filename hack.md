# hack.md — Agentic Cinema constitution + 7 slices

**Repo:** Morkeeth/agent-science · **Event:** Agentic Cinema · Sep 9 2026  
**Spine:** Agent Science = the websearch companion — a registry of verified truths.  
**Constitution:** verbatim span or REFUSE — never paraphrase. No public repo. No rename. No `--set-env-vars` secrets. Slice 1 deploy/keys: Oscar only.

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

## NOW — 2026-08-29 (slices 2 + 4 run)

**Baseline:** `refusal_log.py` 220 lines · registry backfilled: **173 rows** (29 SOURCED + 144 proven-unprovable refusals seeded from `research-corpus/`).

### Slice 2 — registry surface
- [x] `clearance/refusal_log.py` — `queries` table, `search_registry()`, `browse_queries()`, `surface_label()`
- [x] `ask_registry.py` — CLI + `--browse` + `--serve` local UI on :8091
- [x] Every query logged as a browsable row; refusal carries named `cause` + `why`
- [x] `tests/test_registry_surface.py` — 4 controls green
- [ ] Hosted `/registry` on Cloud Run (blocked: slice 1 deploy is Oscar's)

### Slice 4 — second subject (dust-bowl)
- [x] Fixtures: `fixtures/scripts/dust-bowl-A.txt`, `dust-bowl-B.txt` (public-domain narration, not orphan works)
- [ ] Live full chain: `agent_science.py` on dust-bowl — **blocked on this VM:** no `~/.config/keys/{gemini,parallel}.key`, no Vertex ADC (instrument cache OK after backfill fetch)
- [x] Receipt: `docs/SECOND-SUBJECT-RECEIPT-2026-08-29.md` — failures named honestly
- [x] Offline proof: `tests/test_cross_subject_reuse.py` 2/2 — dust-bowl reuses orphan-works log at 0 Parallel calls

### Controls
- `python3 tests/test_watch_it_go_red.py` → **28 passed, 11 failed** (suite crashes on missing InC/EUR-Lex instrument bodies; UNMEASURABLE controls)
- `python3 tests/test_registry_surface.py` → **4 passed**

### Not touched (per constitution)
- `deploy.sh`, repo visibility, key rotation, slice 5 Agent Builder deploy claims

---

*Update the NOW section after every slice. Oscar owns slice 1 and submission gates.*
