# Moonshot memo · agent-science · 2026-08-31

## GOAL

**Parallel track judge sees, on the hosted URL, Run A → Run B on the same subject with `parallel_calls` dropping and `corpus_hits ≥ 1` — while every claim stays verbatim-or-REFUSE — in under 60 seconds without opening a receipt doc.**

Press-release line: *The clearance desk where the second production about the same subject costs measurably less to verify — and refuses when it cannot cite.*

---

## Current model (what we believe)

Depth wins: 109/109 controls, PRIOR LOSS eval gates, ADK default path, partner wiring, and honest ablation docs will differentiate us in a field of vibe-coded Parallel demos. More slices = safer Sep 9 submit.

---

## External evidence

| Source | What it says | Confidence |
|--------|--------------|------------|
| [Agentic Cinema Devpost](https://agentic-cinema.devpost.com/) | 4 **equal** criteria: Tech · Design · Impact · Idea. Stage 1 pass/fail on hosted URL + video + public repo + runtime GCP + partner. **No eval-rigor line.** Parallel judges: Pranay Reddy, Nitin Kesarwani. | high |
| [Devpost rules](https://agentic-cinema.devpost.com/rules) | Tie-break order: Tech → Design → Impact → Idea. Must be "complete, coherent product experience not just a technical proof of concept." | high |
| [Parallel track brief](https://info.devpost.com/blog/google-cloud-agentic-cinema-hackathon) | Official use cases include **fact-checking agent** for media content. Runtime Parallel Search API required in code — README mention insufficient. | high |
| [PeriodCheck](https://github.com/ahsan3274/periodcheck) | **Direct Parallel-track competitor:** historical accuracy for screenwriters. ADK + Gemini + Document AI + Parallel. **13/13 live benchmark**, hosted Cloud Run, line-level citations + confidence + suggested fixes. | high |
| [CineIntel Engine](https://github.com/AtchayamG/cineintel-engine) | Parallel track. Agent crew + Parallel SDK + Gemini 3.7. Public demo at vercel; deterministic fixtures for repeatability. | medium |
| [Greenlight](https://github.com/rainingsnow0914tw-ship-it/greenlight) | Different track (ClickHouse) but sets bar: live demo, real data on screen, budget quoted before spend. | medium |
| `hack.md` PRIOR LOSS · Qwen retro | Four confident loss diagnoses were **wrong**. Eval rigor tendency (65% winners) is post-hoc, p=0.025 — **not an explanation**. Rubric weighted **30/30/25/15 with no eval line**. | high |
| `docs/AMBITION-AUDIT.md` (2026-08-22) | "Product still sells search." Compounding proven in receipt, **invisible in UI**. Without visible Parallel collapse on second script → "modal Parallel-track entry." | high |
| `VISION-2026-08.md` | Moat = **registry of verified truths** that compounds. Compliance (A1) is vertical; companion is horizontal. | high |
| Field size | **8,842** registered · judged **within partner track only** (~1,700 per track if even split). | medium |

---

## Hypotheses (ranked)

### 1. **Live compound exhibit is the winning primitive** ← NET-NEW vs field

**Claim:** Judges reward the one demo PeriodCheck and CineIntel do not show: second clearance on the same subject shelf is cheaper (Parallel calls drop) with honest verdicts preserved.

**Kill bar:** Hosted A/B cannot run (keys/deploy) AND video cannot show side-by-side metrics → we are a citation-table fact-checker indistinguishable from PeriodCheck on Design.

**Slot/build cost:** 1 Oscar gate (deploy + keys on hosted) + 1 build slice (UI strip). Sealed prediction already drafted in SUBMISSION-PACK.

**Falsifiable before Sep 9:** `POST /clear` twice on orphan-works fixtures → Run B `parallel_calls < Run A` AND `corpus_hits ≥ 1` on **hosted URL**, logged in receipt.

### 2. **Compounding Desk UI — make the fraction the hero**

**Claim:** Design criterion breaks ties when Tech is table-stakes (ADK + Parallel + Cloud Run). The product moment is A→B, not a paste box.

**Kill bar:** Stranger still sees generic search UI; compound lives only in `docs/COMPOUND-EXHIBIT*.md`.

**Cost:** 1 build slice · no outward gate.

### 3. **Track-brief-first submission copy + video beats**

**Claim:** Impact + Idea score when first screen answers E&O / documentary clearance in **M&E words**, and ≤3 min video shows compound + refuse (not eval tables).

**Kill bar:** Devpost reads like a benchmark README; video missing on live page (Qwen loss pattern).

**Cost:** Oscar outward gates · prep-only in cloud.

### 4. **Finish PRIOR LOSS checklist (external anchor, holdout, CIs)**

**Claim:** More eval rigor differentiates.

**Kill bar:** Cinema rubric has no eval line; ablation already ties at 0.833 on n=6; RC5 false-GREEN persists.

**Verdict:** **REFUTED for this event** — correct for fleet science, wrong lever for Sep 9.

### 5. **Semantic guard on RC5**

**Claim:** Fix substring false-GREEN → eval delta > 0.

**Kill bar:** n=6 held-out; judges never see eval doc; build cost ≥ 1 slice with uncertain demo payoff.

**Verdict:** **Defer past submit** unless compound + UI ship early.

---

## Refute result

**Adversarial pass (inline — EYES not run):**

| Attack | Result |
|--------|--------|
| "109 tests beat PeriodCheck's 13/13 live" | **Kill.** Judges see product + video, not pytest count. PeriodCheck is live-hosted with benchmark JSON. |
| "Verbatim-or-refuse is unique" | **Partial survive.** PeriodCheck cites + confidence; we refuse structurally (constructor). Differentiation is **insurance/clearance workflow + compounding economics**, not citation alone. |
| "ADK + four partners = done" | **Kill.** Slice 5 shipped; table stakes. PeriodCheck has ADK + Parallel + Document AI live. |
| "Eval gates prevent another Qwen loss" | **Kill for wrong reason.** Qwen loss cause unknown; Cinema rubric ≠ Qwen rubric. Gates are **submission craft**, not placement strategy. |
| "More cloud doc refresh tonight" | **Kill.** `cinema-night` already running; doc refresh without compound UI = plumbing. |

**Surviving hypothesis:** **#1 live compound + #2 Compounding Desk UI** — only pair with zero collision in kill ledger AND direct answer to AMBITION-AUDIT hole.

**All-green refute check:** NOT all-green — PeriodCheck live benchmark is a real threat on Tech + Design if we submit without hosted compound.

---

## Collision check

| Idea | Already fired? | Verdict |
|------|----------------|---------|
| ADK default path | ✅ slice 5 + hosted `/health` | done — not moonshot |
| Partner integrations doc | ✅ 5/5 offline | done |
| Eval baseline + ablation | ✅ tied 0.833 | done — no delta |
| SUBMISSION-PACK count refresh | ✅ 109/109 | done |
| Cold clone stranger path | ✅ 72/72 | done |
| **Live compound on hosted** | ❌ BLOCKED keys | **BUILD — Oscar gate** |
| **Compound strip in UI** | ❌ receipt only | **BUILD** |
| **Gap report as clearance memo** | partial — `<pre>` markdown | **BUILD** |
| RC5 semantic guard | ❌ | defer |
| External eval anchor / holdout | ❌ | defer post-submit |
| Video + Devpost + public repo | ❌ | Oscar Loop 4 |

---

## BUILD-PLAN (Loop 2 → hand to /frame)

Risk-first. Front-load the demo primitive judges haven't seen.

1. **Compound strip on hosted desk** — after `/clear`, show Run metrics + "run again on same subject" lane; surface `parallel_calls`, `corpus_hits`, delta vs prior run on subject shelf · done when: `tests/test_registry_surface.py` extended OR UI smoke + screenshot in receipt · size M · risk: UI without live keys still useful for video rehearsal

2. **Gap report clearance memo format** — structured action list (SOURCED / UNSOURCED / UNKNOWN) readable by clearance lead; not raw log dump · done when: one fixture output matches memo template in VIDEO-SCRIPT beat 0:46 · size S · risk: low

3. **Hosted compound A/B receipt** — orphan-works Run A → Run B on **hosted URL** with sealed-prediction table filled · done when: `docs/RECEIPT-live-compound-*.md` with curl transcripts OR honest BLOCKED with named missing key · size S · risk: **Oscar deploy + keys**

4. **Video + Devpost lock** — script beats 1:30–1:54 (compound) + 1:12 (refuse) as non-negotiable; Devpost paste opens with E&O sentence not test counts · done when: Oscar confirms paste block + ≤180 s script unchanged · size XS · risk: outward gate

*(Slice order: 2 can ship without keys; 1 partially; 3 blocked on Oscar; 4 Oscar-only.)*

---

## OPS (Loop 4 — separate)

- **Tonight:** `cinema-night` cloud agent ACTIVE — `bc-2c460298-a88b-499d-9aac-0cf07787e56e`
- **Scheduler:** launchd every 4h; retry 8h on fail
- **Oscar gates:** deploy.sh · PARALLEL/GEMINI keys on Cloud Run · public repo flip · YouTube/Vimeo upload · Devpost submit
- **Tomorrow review:** `node scripts/cloud-harness.js review agent-science` — score ambition vs disk, not agent prose
- **Do not:** cloud lane spends slices on eval checklist rows or doc-count gates — already green

---

## Explicitly NOT doing (effort tradeoff)

| Could do | Why not now |
|----------|-------------|
| RC5 semantic guard | n=6; judges don't see eval; compound UI higher leverage |
| External benchmark we didn't build | Correct science; zero Cinema rubric weight before Sep 9 |
| Holdout + CIs on refusal set | Submission craft; defer until compound ships |
| Rename repo / public flip | Oscar gate; not build lane |
| Design partner outreach (slice 6) | Oscar; parallel to submit prep |
| Compete on agent-crew breadth (CineIntel-style) | Collision with our refusal spine; wrong product shape |

---

*Loop 0+1+2 complete 2026-08-31. Loop 3 starts at BUILD-PLAN slice 2 (gap memo format) — shippable without keys. Loop 4 ops already running.*
