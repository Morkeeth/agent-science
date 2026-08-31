# VIDEO SCRIPT — Agent Science · Agentic Cinema

**Target:** ≤ 180 seconds · **Beats below sum to 178 s**  
**Capture:** screen record hosted URL + local registry UI · voiceover reads bold lines  
**Do not:** stage claims — use real `/clear` output and `ask_registry.py --serve`  
**EYES pass 2026-08-31:** refuse + E&E lead; compound is secondary. See `docs/EYES-HACK-PASS-2026-08-31.md`.

---

## Pre-roll (before timer)

- Browser tab 1: https://agent-science-568004190078.us-central1.run.app/
- Browser tab 2: hosted `/registry` and `/popular/ui`
- Script file ready: `fixtures/scripts/compound-mini-A.txt` (fresh subject for compound)
- `fixtures/shift-ai-training-vs-noncommercial.md` for buyer flip

---

## Timed beats (EYES order)

| Time | Sec | Beat | On screen | Voiceover |
|------|----:|------|-----------|-----------|
| 0:00 | 10 | **Hook — M&E** | Title: *Agent Science — clearance for factual production* | "Every documentary needs two reports before it can be insured: every fact sourced, every asset cleared. Miss one — that's a lawsuit." |
| 0:10 | 14 | **Problem** | E&O checklist · provenance stall | "Studios and AI labs stall on the same thing: nobody can prove provenance at asset level. Humans do this by hand." |
| 0:24 | 12 | **Rule** | Constructor rejects uncited verdict (3 s) | "Cite the document, or print that you could not. No citation — no verdict. Enforced in code." |
| 0:36 | 22 | **Demo — SOURCED** | `GET /search?q=2012/28/EU&live=false` or `/clear` one row — **verbatim span** | "Paste a script or ask a fact. We return the exact sentence from the instrument — not a summary." |
| 0:58 | 18 | **Demo — refuse** | Registry row: **UNKNOWN** + `cause` + `why` | "When we cannot prove it, we say so — with a named cause. No greenwash." |
| 1:16 | 14 | **Honest marketing** | C5: *search_found_no_admissible_source* on "94% of film archives" | "We pointed the product at our own pitch. It refused our headline. The number was fine — the object was not." |
| 1:30 | 20 | **Compound** (secondary) | Fresh subject A→B: `corpus_hits` ≥ 1 · `parallel_calls` drop if visible | "Run the same subject twice. The shelf remembers — fewer search calls, same honest verdicts." |
| 1:50 | 18 | **Second buyer** | `shift-ai-training-vs-noncommercial.md`: **247 / 600 flip** | "One index, two buyers. Forty-one percent of the library changes verdict when the use case changes." |
| 2:08 | 12 | **Dictionary** | `/popular/ui` — top queries · hit rate | "The most-asked truths get cheaper for everyone — a truth dictionary, not a chat log." |
| 2:20 | 10 | **Close** | Hosted URL + repo + MIT | "Agent Science — link in description." |

**Total: 178 s**

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
