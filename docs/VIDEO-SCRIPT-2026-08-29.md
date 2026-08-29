# VIDEO SCRIPT — Agent Science · Agentic Cinema

**Target:** ≤ 180 seconds · **Beats below sum to 178 s**  
**Capture:** screen record hosted URL + local registry UI · voiceover reads bold lines  
**Do not:** stage claims — use real `/clear` output and `ask_registry.py --serve`

---

## Pre-roll (before timer)

- Browser tab 1: https://agent-science-568004190078.us-central1.run.app/
- Browser tab 2: `python3 ask_registry.py --serve` → http://127.0.0.1:8091/ (or hosted `/registry` after deploy)
- Script file ready: `fixtures/scripts/documentary-orphan-works.txt` (or shorter `compound-mini-A.txt`)

---

## Timed beats

| Time | Sec | Beat | On screen | Voiceover |
|------|----:|------|-----------|-----------|
| 0:00 | 10 | **Hook** | Title card: *Agent Science — the clearance desk* | "Every documentary needs two reports before it can be insured: every fact sourced, every asset cleared. Miss one — that's a lawsuit." |
| 0:10 | 16 | **Problem** | Split: E&O checklist · rights-holder ↔ AI lab handshake | "Studios and AI labs both stall on the same thing: nobody can prove provenance at asset level. Humans do this by hand, slowly." |
| 0:26 | 20 | **Rule** | Code flash: constructor rejects uncited verdict (3 s) · back to UI | "Our one rule: cite the document, or print that you could not. No citation — no verdict. Enforced in code, not policy." |
| 0:46 | 26 | **Demo — clear** | Paste orphan-works script → `POST /clear` → one claim row: **SOURCED** with verbatim span | "Paste a production script. Gemini extracts claims. Parallel finds sources. We return the exact sentence from the instrument — or a named refusal." |
| 1:12 | 18 | **Demo — refuse** | Registry browse: row with **UNKNOWN** + `cause` + `why` | "When we cannot prove it, we say so — with a named cause. No greenwash." |
| 1:30 | 24 | **Compound** | Side-by-side: Run A metrics vs Run B — `parallel_calls` drops, `corpus_hits` ≥ 1 | "Run the same subject twice. The second production hits the corpus shelf — fewer search calls, same honest verdicts. Measured, not asserted." |
| 1:54 | 22 | **Second buyer** | `fixtures/shift-ai-training-vs-noncommercial.md` highlight: **247 / 600 flip** | "One index, two questions. Forty-one percent of the library changes verdict when the buyer's use case changes — driven by the instruments' own terms." |
| 2:16 | 20 | **Registry** | `ask_registry.py --serve` — scroll browsable query log | "Every question becomes a browsable row. A registry of verified truths — not a chat transcript." |
| 2:36 | 14 | **Honest marketing** | C5 refusal flash: *search_found_no_admissible_source* on "94% of film archives" | "We pointed the product at our own pitch. It refused our headline. The number was fine — the object was not." |
| 2:50 | 8 | **Close** | Hosted URL + repo link + MIT badge | "Agent Science — clearance desk for factual production. Link in description. MIT licensed." |

**Total: 178 s** (2 s buffer under 180 s cap)

---

## B-roll inserts (optional, inside beats above)

- `docs/COMPOUND-EXHIBIT-2026-08-29.md` table: A=2 Parallel, B=1, corpus hits=2
- `docs/SECOND-SUBJECT-RECEIPT-2026-08-29.md` — dust-bowl reuses orphan log at 0 Parallel
- Health check: `"engine_default"` field (note ADK ⬜ until Oscar runs `deploy.sh` — do not claim ✅ on video)

---

## Post-production checklist

- [ ] Total runtime ≤ 3:00 (re-cut if over)
- [ ] At least one **SOURCED** verbatim span visible on screen
- [ ] At least one **UNKNOWN** with named cause visible
- [ ] Hosted URL readable in final frame
- [ ] No API keys, no Secret Manager values in frame
- [ ] Upload to Devpost (Oscar — not in this slice)
