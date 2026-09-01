# JUDGE-CRITERIA — Agent Science · executed on disk

**Event:** [Agentic Cinema](https://agentic-cinema.devpost.com/) · **Track:** Parallel  
**Hosted:** https://agent-science-568004190078.us-central1.run.app  
**Video:** `demo/demo-final.mp4` (103.6s) · **Measured:** 2026-09-02 UTC

This file maps each rubric line to a **hosted URL**, **video beat**, or **receipt** — not a doc claim.

---

## Rubric (four criteria, equally weighted)

Source: `docs/PHASE1-SPEC-EXTRACT.md` § JUDGING RUBRIC — verbatim from Devpost.

| Criterion | Weight | What judges see | Object | Verified |
|-----------|--------|-----------------|--------|----------|
| **Technological Implementation** | 25% | Four partners live · ADK default · compound A→B | `GET /health` · `GET /partners` · `bash scripts/long_run_goal.sh` | `engine_default: adk` · 4 partners · 19/19 long run |
| **Design** | 25% | Judge-facing visibility panel · registry · truths dashboard | `/visibility/ui` · `/registry` · `/truths/ui` | HTML panel in repo (deploy pending); hosted still `<pre>` until Oscar deploys |
| **Potential Impact** | 25% | E&O gap report · cold public scripts · 5 wrong refusals honest | `docs/COLD-SCRIPTS.md` · `POST /clear` | 15 claims · 6 SOURCED · 9 REFUSED · **5 WRONG** |
| **Quality of Idea** | 25% | Verbatim-or-refuse pole · CONTRARY stamp · buyer flip | `/search?q=2012/28/EU&live=false` · C5 beat · `fixtures/shift-ai-training-vs-noncommercial.md` | SOURCED free tier · headline refused on camera |

---

## Parallel track brief (first screen)

**Required ¶1 (Devpost + video 0:00):**

> Paste a documentary script. Get every checkable claim sourced verbatim — or refused with cause. Agent Science is the truth layer for what agentic builders believe and use.

| Surface | Where it lands | Object check |
|---------|----------------|--------------|
| Devpost paste | `docs/DEVPOST-WIN.md` ¶1 | `head -8 docs/DEVPOST-WIN.md` |
| Video 0:00 | `demo/demo-final.mp4` @ 0s | `ffmpeg -ss 0 -i demo/demo-final.mp4 -frames:v 1 /tmp/f0.png` — truth-layer hook, **no SCOUT** |
| Visibility UI hook | `cloud/service.py` `_visibility_panel_html` | Local: `grep 'Paste a script' cloud/service.py` |

---

## Video beats ↔ criteria

Measured on `demo/demo-final.mp4` (103.56s ≤ 180s cap).

| Time | Beat | Criterion served | On screen |
|------|------|------------------|-----------|
| 0:00 | Hook — truth layer | Quality of Idea · track brief | "Your agent websearches. You get one answer." |
| 0:10 | Visibility pane 1b | Design · Tech | `/visibility/ui` screenshot — angles searched |
| 0:22 | CONTRARY TO RESEARCH | Quality of Idea | Stamp overlay on visibility panel |
| 0:34 | Rule — cite or refuse | Quality of Idea | Constructor enforcement copy |
| 0:44 | SOURCED span | Tech · Impact | Registry screenshot — verbatim quote |
| 0:53 | Refuse + cause | Impact | Named refusal — not permission |
| 1:03 | C5 honest beat | Impact | "We refused our own headline" |
| 1:12 | Compound A=1→B=0 | Tech | Parallel drop + corpus hits |
| 1:22 | Truths dashboard | Design | `/truths/ui` — ranked queries |
| 1:32 | Partners + close | Tech | `/partners` · hosted URL |

**Do not show on video:** orphan-works full script Run B (504/503 on hosted).

---

## Hosted reality (re-derived 2026-09-02)

| Claim | Command | Result |
|-------|---------|--------|
| Health + ADK | `curl -s …/health` | `ok: true`, `engine_default: adk`, `parallel: true`, `gemini: true` |
| Registry size | `curl -s …/stats` | `n: 303`, `dictionary_hit_rate: 0.607`, `queries_logged: 239` |
| Free tier hit | `curl -s '…/search?q=2012%2F28%2FEU&live=false'` | `label: SOURCED`, `cost_tier: free`, `parallel_api_calls: 0` |
| Partners | `curl -s …/partners` | 4 partners (Vertex, Parallel, Cloud Run, ADK) |
| Visibility UI (hosted) | `curl -s '…/visibility/ui?q=ralph+loop+agentic' \| grep -c '<pre>'` | **1** — monospace dump until deploy |
| Visibility JSON | `curl -s '…/visibility?q=ralph+loop+agentic'` | `primary.label: CONTRARY_TO_RESEARCH` |
| Stranger path | `bash scripts/verify_cold_clone.sh` | inside `full_gate.sh` |
| Compound exhibit | `bash scripts/long_run_goal.sh` | 19/19 · B `corpus_hits ≥ 1` |
| Sealed prediction | `docs/SEALED-PREDICTION-2026-08-31.md` | A=1 → B=0 Parallel |

---

## Cold scripts (public transcripts)

Three public documentary scripts — not fixtures. Full doc: `docs/COLD-SCRIPTS.md`.

| Script | Claims | SOURCED | REFUSED | WRONG |
|--------|--------|---------|---------|-------|
| Apollo 11 ALSJ | 3 | 2 | 1 | 1 |
| NOVA *Dimming the Sun* | 4 | 0 | 4 | 3 |
| EU orphan works | 8 | 4 | 4 | 2 |
| **Total** | **15** | **6** | **9** | **5** |

```bash
python3 scripts/run_cold_scripts.py      # batch hosted POST /clear
python3 scripts/audit_cold_wrong.py      # wrong_count at source URLs
```

---

## Oscar gates (not scored until done)

| Gate | Status | Owner |
|------|--------|-------|
| Video public on Devpost | Built locally · not uploaded | Oscar |
| Devpost submit + logged-out verify | Paste in `docs/DEVPOST-WIN.md` | Oscar |
| Deploy judge UX panel | `./deploy.sh` | Oscar |
| Key rotation before public push | `hack.md` OPEN QUESTIONS | Oscar |

---

## Baseline arm (embarrassment test)

Naive competitor path: raw Parallel search → LLM summary (no verbatim span enforcement).

| Arm | Script | Measured |
|-----|--------|----------|
| Shipping | `POST /clear` on cold scripts | 6/15 SOURCED, **5 WRONG refusals** |
| Baseline | `scripts/eval_refusal_baseline.py` | 5/6 = 0.833 vs shipping 6/6 = 1.000 |

Cold-script wrong count is the finding judges should see — we ship honest limits, not a polished demo only.
