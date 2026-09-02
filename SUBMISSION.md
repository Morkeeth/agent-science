# SUBMISSION — Agent Science · Agentic Cinema

**Event:** [Agentic Cinema](https://agentic-cinema.devpost.com/) · **Deadline:** Sep 9 2026 14:00 PDT  
**Track:** Parallel  
**Repo:** https://github.com/Morkeeth/agent-science (MIT)  
**Hosted:** https://agent-science-568004190078.us-central1.run.app  
**Claims → evidence:** `docs/CLAIMS-MAP-2026-09-02.md`

---

## Stranger path (< 5 min, no keys)

```bash
git clone https://github.com/Morkeeth/agent-science.git && cd agent-science
bash scripts/verify_cold_clone.sh
bash scripts/demo_truth_layer.sh
bash scripts/demo_clearance_desk.sh
```

**See it in the browser (no clone):**

https://agent-science-568004190078.us-central1.run.app/visibility/ui?q=ralph+loop+agentic

| Surface | URL |
|---------|-----|
| Truth layer WOW | `/visibility/ui?q=ralph+loop+agentic` |
| Truths dashboard | `/truths/ui` |
| Registry | `/registry` |
| Health / partners | `/health` · `/partners` |

---

## Ship checklist

| # | Item | Status | Where |
|---|------|--------|-------|
| 1 | Hosted URL live | ✅ | above |
| 2 | Public repo + MIT | ✅ | GitHub |
| 3 | Controls 127/127 (tests across 11 suites, 72 of them mutation-watched) | ✅ 2026-09-02 | `python3 scripts/bench_check_docs.py` (step 5 of `full_gate.sh`) |
| 4 | Sealed compound A=1→B=0 | ✅ | `docs/SEALED-PREDICTION-2026-08-31.md` |
| 5 | Demo video ≤180s | ✅ built | `demo/demo-final.mp4` (102s) · Oscar uploads |
| 6 | Devpost submit | [ ] | `docs/DEVPOST-WIN.md` |
| 7 | Privacy grep = 0 | ✅ 2026-09-02 (control rewritten on `git grep`; the old one scanned 0 files) | `bash scripts/privacy_grep.sh` |

---

## Runtime integrations

| Integration | Hosted | Receipt |
|-------------|--------|---------|
| Parallel Search (SDK) | ✅ | `/health` → `parallel_sdk: true` |
| Gemini (Vertex) | ✅ | `/health` → `gemini_path: vertex:…` |
| Google Cloud Run | ✅ | hosted URL |
| Agent Development Kit | ✅ | `/health` → `engine_default: adk` |

---

## Pitch (30s)

> Agent Science is the truth layer for what agentic builders believe and use. Transparent websearch — angles searched, field signals, sourced or refused — and CONTRARY TO RESEARCH when the field outruns papers. Ask once; shelf compounds.

Full: `docs/PITCH-TOMORROW.md` · film teleprompter: `demo/FILM-AND-SUBMIT.md`

---

## Sealed prediction

Second `/clear` on the same subject: `corpus_hits ≥ 1` and Run B `parallel_calls` < Run A.

**Measured (hosted):** A=**1** → B=**0** Parallel · corpus_hits=**1**  
**Doc:** `docs/SEALED-PREDICTION-2026-08-31.md`

---

## Do not claim on video

- Orphan-works full compound when Run B returns **503**
- Flywheel headline without showing transparency panel first

---

## Buyer

**Role:** E&O underwriter or documentary clearance supervisor at a production company or specialty insurer (illustrative roles — the media & entertainment desk at a specialty insurer, or an in-house clearance desk at a studio; **no named buyer has been contacted yet**).

**Budget line:** Errors & Omissions insurance premium and clearance labor. **Working estimate, unsourced (2026-09-02):** $15k–$80k per hour-long documentary in researcher time plus 0.5–2% of production budget on E&O premium where uncleared claims force exclusions or holdbacks — no citation in this repo; do not quote these numbers to a buyer until one is added.

**What they cancel:** Manual fact-check passes on every narration revision, duplicate researcher hours when the same orphan-works / settlement claims recur across episodes, and the **re-open cost** when a lawyer cannot show a per-claim audit trail (sourced quote + URL or named refusal).

**Recurring metric they report upward:** **claims cleared per week** and **claims caught (refused or flagged)** — the gap report row count and UNSOURCED/INDEPENDENCE causes, not model confidence. Hosted desk: `POST /clear` · cold demo: `bash scripts/demo_clearance_desk.sh`.

**Honest limit:** We prove verdict + cause on public scripts today; we do not yet sell a signed E&O endorsement. The buyer is the person who already owns that budget line and needs the audit artifact.
