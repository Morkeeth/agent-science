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

**Baseline:** `refusal_log.py` 264 lines · registry backfilled: **173 rows** (28 SOURCED + 145 proven-unprovable refusals seeded from `research-corpus/`).

### Slice 2 — registry surface
- [x] `clearance/refusal_log.py` — `queries` table, `search_registry()`, `browse_queries()`, `surface_label()`
- [x] `ask_registry.py` — CLI + `--browse` + `--serve` local UI on :8091 (CSS template bug fixed)
- [x] Every query logged as a browsable row; refusal carries named `cause` + `why`
- [x] `tests/test_registry_surface.py` — 5 controls green
- [ ] Hosted `/registry` on Cloud Run (blocked: slice 1 deploy is Oscar's)

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

### Not touched (per constitution)
- `deploy.sh`, repo visibility, key rotation, slice 5 Agent Builder deploy claims

---

*Update the NOW section after every slice. Oscar owns slice 1 and submission gates.*
