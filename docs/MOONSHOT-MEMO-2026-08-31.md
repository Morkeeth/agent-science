# Moonshot memo · agent-science · 2026-08-31 (rev 2)

## GOAL

**Press-release:** *The truth dictionary for agent work — ask once, verify once, free forever; the most-searched things get cheaper for everyone.*

**Sep 9 stranger test:** Judge on hosted URL sees Run A → Run B with Parallel API dropping and corpus hits rising — while every claim stays verbatim-or-REFUSE — in under 60 seconds. Video shows compound + refuse, not eval tables.

**Product test (4 weeks):** `dictionary_hit_rate ≥ 0.80`, `queries_logged ≥ 200`, fleet uses `science_lookup` daily — `science_popular` drives alias/ingest fixes.

---

## Current model (what we believe)

The product is a **self-tuning truth dictionary**, not a search API. Adoption → logged queries → `popular` → alias/ingest/route → hit rate ↑ → cheaper → more adoption. Documentary clearance is one vertical; daily dev websearch is the volume.

For Sep 9: **compound economics on screen** beats PeriodCheck's citation table (they have 13/13 live benchmark + hosted + Document AI). Depth/eval gates do not score on Cinema rubric.

---

## External evidence

| Source | What it says | Confidence |
|--------|--------------|------------|
| [Agentic Cinema Devpost](https://agentic-cinema.devpost.com/) | 4 equal criteria: Tech · Design · Impact · Idea. Hosted URL + video + public repo + runtime GCP + partner. **No eval line.** | high |
| [Parallel track brief](https://info.devpost.com/blog/google-cloud-agentic-cinema-hackathon) | Fact-checking for media content. Parallel Search API **at runtime**. | high |
| [PeriodCheck](https://github.com/ahsan3274/periodcheck) | **Direct competitor:** 13/13 gold live, hosted Cloud Run, ADK + Parallel + Document AI, line-level citations + confidence + fixes, bounded search cost, `live-evaluation.json`. | high |
| [PeriodCheck Devpost](https://devpost.com/software/period-check) | Evidence-first UI, stable evidence IDs, citation hydrated from Parallel response — same primitive we share, different wedge. | high |
| [AttestDB](https://github.com/omic/attest) | Claim-native DB + MCP (106 tools): sourced claims, retraction cascade, popularity/gap detection — **closest product shape** to our dictionary vision; confidence scores not structural refuse. | medium |
| `VISION-2026-08.md` | Moat = registry of most-searched verified truths + negative space. Flywheel formalized 2026-08-31. | high |
| `hack.md` PRIOR LOSS | Eval rigor ≠ Cinema placement. Wrong diagnoses retracted. | high |
| Local stats (2026-08-31) | 180 claims, **7 queries logged**, hit rate **0.57**, **1 reuse** — engine works, **flywheel barely spinning**. | high |

---

## Hypotheses (ranked)

### 1. **Truth dictionary flywheel is the company; compound is the demo** ← NET-NEW vs Attest/PeriodCheck

**Claim:** Nobody in the Parallel track shows **popularity-driven pre-clearing** (free → cheap → live tiers + `science_popular`). PeriodCheck shows first-run accuracy; we show **second-run economics** + honest refusals as first-class rows.

**Kill bar:** After 4 weeks, `queries_logged < 50` — product vision is slide deck only.

**Cost:** Adoption habit (Oscar + fleet) + 2 build slices (auto-ingest, `/popular` UI).

**Falsifiable:** `python3 -m clearance stats` → hit rate and reuses climb week-over-week.

### 2. **Live compound exhibit wins Sep 9** ← NET-NEW vs PeriodCheck on Design

**Claim:** Judges reward visible A→B Parallel drop on hosted URL — PeriodCheck does not demo compounding.

**Kill bar:** No deploy + video → indistinguishable citation-table entry.

**Cost:** Oscar `deploy.sh` + keys + ≤180s video.

**Falsifiable:** Hosted receipt B.parallel < A.parallel AND B.corpus_hits ≥ 1 (offline receipt **passes**; hosted partial).

### 3. **Video + Devpost in M&E words, not pytest**

**Claim:** Impact/Idea score when copy opens with E&O/clearance sentence and video shows compound + refuse beats.

**Kill bar:** Missing public video on Devpost (Qwen loss pattern).

**Cost:** Oscar Loop 4 only.

### 4. **More eval / semantic guard / ClickHouse index**

**Verdict:** **REFUTED for Sep 9** — rubric weight zero; Attest already owns claim-DB shape; ClickHouse doesn't replace discovery.

---

## Refute result

**Adversarial pass (inline — EYES not run):**

| Attack | Result |
|--------|--------|
| "Truth dictionary without usage is real" | **Kill.** 7 queries logged. Vision is correct; **adoption is the blocker**, not architecture. |
| "AttestDB already won this" | **Partial survive.** Attest = claim store + confidence; we = **verbatim span verify + structural refuse + Parallel compounding demo**. Integrate ideas (content_id, gap detection), don't pivot stack. |
| "PeriodCheck already shipped the product" | **Kill on clearance UX; survive on dictionary economics.** They bound search cost but don't show shelf reuse across productions. |
| "Build /popular and auto-ingest before deploy" | **Kill for Sep 9.** Judges don't see CLI. Deploy + video first. |
| "science_lookup defaults live=true" | **Kill.** Fixed — `science_lookup` defaults `live=false`; flywheel requires cheap path. |

**Surviving pair:** **#1 flywheel (post-submit company)** + **#2 compound demo (Sep 9)** — same engine, different surfaces.

**All-green check:** NOT all-green — PeriodCheck 13/13 live is real; we must ship hosted compound + video or lose Design/Tech tie-break.

---

## Collision check

| Idea | Already fired? | Verdict |
|------|----------------|---------|
| ADK default + partner runtime | ✅ 5/5 + hosted health | done |
| Compound UI strip | ✅ cloud lane + service.py | done |
| Stack product (MCP/CLI/HTTP) | ✅ science_search stack | done |
| Truth dictionary (`dictionary.py`) | ✅ free/cheap/live | done |
| URL routing (CELEX, arXiv, rights) | ✅ `routing.py` | done |
| `science_popular` + query analytics | ✅ 2026-08-31 | done |
| Live compound hosted receipt | ⚠️ partial — fresh subject pass | **Oscar deploy verify** |
| Video + Devpost + public repo | ❌ | **Oscar Loop 4** |
| Auto-ingest after research | ❌ | **BUILD post-deploy** |
| `/popular` on hosted desk | ❌ | **BUILD post-deploy** |
| Shared fleet dictionary (GCS) | ❌ | **BUILD week 2** |
| Attest-style content_id / retraction | ❌ | defer — borrow after flywheel spins |

---

## BUILD-PLAN (Loop 2 → hand to /frame)

**Sep 9 critical path (Oscar-heavy):**

1. **Deploy + verify hosted compound** — `bash deploy.sh`; curl compound-mini A/B on live URL; fill sealed-prediction table · done when: receipt with hosted transcripts OR honest BLOCKED · size S · **Oscar gate**

2. **Video ≤180s** — beats: problem (E&O) → Run A → Run B (metrics on screen) → registry browse → one refusal · done when: public YouTube/Vimeo URL · size XS · **Oscar gate**

3. **Devpost + public repo** — paste block from SUBMISSION-PACK; flip visibility; OSI licence · done when: submission URL live · size XS · **Oscar gate**

**Product flywheel (build lane — parallel, not blocking video):**

4. **Fix top-3 `popular` misses** — ingest orphan-works EU + aliases for `2012/28/EU` · done when: `popular` shows 0 misses on those queries · size XS · **shippable now**

5. **Auto-ingest hook** — research skill / ZUP appends `[CLAIM]/[URL]` → `science_ingest` on session end · done when: one fleet repo documents + one end-to-end test · size M

6. **Hosted `/popular` page** — top queries + optimization targets on desk · done when: GET returns JSON + registry nav link · size S

*(Order: 4 today without Oscar; 1–3 Oscar; 5–6 after deploy.)*

---

## OPS (Loop 4 — separate)

- **Oscar today:** rotate leaked keys · `deploy.sh` · restart Cursor for MCP
- **Oscar this week:** video · Devpost · public repo · seal prediction hash
- **Fleet habit:** `science_lookup` default · `popular` weekly · `ingest` after research
- **Review:** `node ~/CODE/zup/scripts/cloud-harness.js review agent-science`
- **Do not:** eval checklist rows · ClickHouse · cloud doc refresh without outward artifact

---

## Explicitly NOT doing

| Could do | Why not now |
|----------|-------------|
| ClickHouse index | Wrong primitive; popularity already in SQLite |
| RC5 / more eval gates | Zero rubric weight; compound + video higher |
| Compete on Document AI PDF ingest | PeriodCheck owns; not our wedge |
| Pivot to AttestDB | Collision with refuse spine; borrow patterns later |
| Fleet shared dictionary before deploy | Hosted URL first |

---

*Loop 0+1+2 complete 2026-08-31 rev 2. Loop 3 slice 4 (fix popular misses) shippable without Oscar. Loop 4 slices 1–3 are Sep 9 gates.*
