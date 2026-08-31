# PARTNER INTEGRATION RESEARCH — final pass before ATA

**Date:** 2026-08-31 · **Repo:** Morkeeth/agent-science · **Track:** Agentic Cinema · Parallel  
**Purpose:** One last deepen on how the four partners are wired vs the field, what judges can verify without Oscar on camera, and what changed in this build pass.

---

## Executive summary

| Partner | Runtime on hosted? | SDK in repo? | Judge-visible proof |
|---------|-------------------|--------------|---------------------|
| **Parallel** | Yes (`PARALLEL_API_KEY` via Secret Manager) | **`parallel-web==1.3.2`** pinned | `/health` → `parallel_sdk`, `last_parallel_search_id`; `/partners` manifest; `cache/search_receipts.jsonl` with `search_id` |
| **Gemini / Vertex** | Yes (ADC on Cloud Run) | `google-genai` via ADK | `/health` → `gemini_path: vertex:hack-fleet` |
| **Google Cloud** | Yes | N/A (platform) | Hosted URL, GCS corpus shelf, `deploy.sh` |
| **Agent Builder / ADK** | Yes (default engine) | `google-adk==2.7.1` | `/health` → `engine_default: adk`; `docs/RECEIPT-adk-default-path-2026-08-30.md` |

**This pass:** moved Parallel from README-only REST to **official `parallel-web` SDK** as primary transport, with urllib REST fallback for cold clones without the wheel. Every live search logs **`search_id`** in `search_receipts.jsonl` — the lineage hook PeriodCheck surfaces in its evidence UI.

---

## Parallel track rubric — how we score

The Parallel track is not “mentioned Parallel in the README.” Judges look for:

1. **Search at runtime** on the default product path (`POST /clear` → `judge_claim` → `find_sources`).
2. **Official integration** — SDK, LangChain, Vercel AI, or MCP — not a one-off curl in docs only.
3. **Hosted URL** that a stranger can hit without cloning.
4. **Evidence** that spend is real and bounded (meter, cache, compound drop).

### Before this pass

| Check | Status |
|-------|--------|
| Runtime call | ✅ `clearance/facts.py` |
| SDK package in `requirements.txt` | ❌ urllib only |
| `search_id` in receipts | ❌ |
| Judge manifest endpoint | ❌ `/health` only |
| Live probe script | ❌ |

### After this pass

| Check | Status |
|-------|--------|
| `parallel-web==1.3.2` in `requirements.txt` + Docker image | ✅ |
| `_live_search()` prefers SDK, falls back to REST | ✅ |
| `LAST_SEARCH_ID` + receipt field | ✅ |
| `GET /partners` manifest | ✅ |
| `python3 scripts/partner_probe.py` | ✅ |
| `tests/test_parallel_integration.py` | ✅ |

---

## Field comparison (Parallel track, Aug 2026)

### PeriodCheck — #1 reference implementation

| Dimension | PeriodCheck | Agent Science |
|-----------|-------------|---------------|
| **First-run UX** | PDF ingest, polished evidence UI, `live-evaluation.json` | Paste script, gap report JSON/HTML |
| **Parallel wiring** | Official SDK, `search_id` in UI | **Now aligned** — SDK + `search_id` in receipts |
| **Compound economics** | Demo A→B Parallel drop | **Hosted measured** — sealed prediction `2→1`, corpus_hits |
| **Refuse / E&O angle** | Scores confidence | **Structural refuse** — UNSOURCED/UNKNOWN, no score theater |
| **Insurance buyer** | Implicit | Explicit lane — clearance memo, refusal log |

**Film implication (when Oscar returns):** do not open on compound metrics; open on **“what E&O underwriters refuse to score.”** PeriodCheck wins the PDF beauty contest; we win **honest refuse + reuse shelf**.

### Genesis / Clearance Compass (lighter field)

- **Genesis-style agents:** tool-chaining demos without a persistent refusal registry — we differentiate on **cross-subject reuse** (`refusal_log` / GCS shelf).
- **Clearance Compass:** keyword + LLM summaries — we differentiate on **verbatim structural verify** (`clearance/verify.py`) before any SOURCED verdict.

### What none of them ship (our moat if flywheel fires)

- Truth dictionary with **tiered lookup** (free registry → cheap URL routing → live Parallel)
- **Sealed prediction** on hosted compound behavior
- **ADK default path** with direct fallback stamped in `engine` field

---

## Integration architecture (code map)

```
POST /clear
  └─ cloud/service.py::_run_clearance
       ├─ engine=adk → cloud/agent.py → clear_script_tool
       └─ engine=direct → agent_science.py
            └─ clearance/facts.py::judge_claim
                 └─ clearance/search.py::find_sources  ← Parallel
                      ├─ parallel-web SDK (preferred)
                      └─ urllib REST (fallback)
                 └─ clearance/gemini.py (extract/locate)
                 └─ clearance/verify.py (structural — never trust model)
```

**Secret surfaces:** `PARALLEL_API_KEY` only via Secret Manager on deploy; local `~/.config/keys/parallel.key`. Gemini via Vertex ADC — no plaintext in `deploy.sh` env block.

---

## Judge verification playbook (no video required)

```bash
# 1. Health — all four partners visible
curl -s https://agent-science-568004190078.us-central1.run.app/health | python3 -m json.tool

# 2. Full partner manifest
curl -s https://agent-science-568004190078.us-central1.run.app/partners | python3 -m json.tool

# 3. Live clearance stamps engine + parallel_calls
curl -s -X POST https://agent-science-568004190078.us-central1.run.app/clear \
  -H 'Content-Type: application/json' \
  -d '{"script":"The Dust Bowl displaced 2.5 million people.","subject":"dust-bowl-probe"}' \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('engine'), d.get('parallel_calls'))"

# 4. Truth dictionary — registry hit, zero Parallel
curl -s 'https://agent-science-568004190078.us-central1.run.app/science_lookup?q=Directive+2012%2F28%2FEU' \
  | python3 -m json.tool
```

**Clone controls (no keys):**

```bash
python3 tests/test_partner_runtime.py      # 6/6
python3 tests/test_parallel_integration.py # 6/6
bash scripts/verify_cold_clone.sh
```

**With key (Oscar or CI):**

```bash
python3 scripts/partner_probe.py
# → docs/RECEIPT-partner-probe-YYYY-MM-DD.md
```

---

## Gaps that remain honest

| Gap | Impact | Mitigation |
|-----|--------|------------|
| No video / Devpost | Cannot submit for judging until filmed | Oscar on ATA; build lane continues |
| ArkivX feed | Vision doc only | Not claimed in submission copy |
| Design partner (slice 6) | No archive friction log | `docs/DESIGN-PARTNER-LOOP.md` ready |
| Orphan-works compound B **503** on hosted | Weak live demo for that subject | Film dust-bowl or compound-mini; dictionary lead is 2012/28/EU |
| Flywheel kill bar | `queries_logged < 50` in 4 weeks | Post-hackathon metric |

---

## Receipts chain

| Doc | Role |
|-----|------|
| `docs/PARTNER-INTEGRATIONS-2026-08-30.md` | Operator checklist + curl recipes |
| `docs/PARTNER-INTEGRATION-RESEARCH-2026-08-31.md` | This file — field + rubric |
| `docs/RECEIPT-adk-default-path-2026-08-30.md` | ADK default engine proof |
| `docs/SEALED-PREDICTION-2026-08-31.md` | Compound A→B commitment |
| `scripts/partner_probe.py` | Live probe → dated receipt |

---

## Recommendation for submission copy (when video lands)

**One-liner:** Agent Science is an E&O-facing clearance desk that **refuses** when evidence is missing — Parallel finds sources, Gemini proposes passages, structural verify decides, and the refusal registry compounds so the second clearance costs less.

**Partner sentence:** Built on **Parallel Search** (`parallel-web`), **Gemini on Vertex**, **Google Cloud Run**, and **Agent Builder (ADK)** — verify at `/partners` on the hosted URL.
