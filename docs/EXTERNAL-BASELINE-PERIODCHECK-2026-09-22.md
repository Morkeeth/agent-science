# EXTERNAL BASELINE — PeriodCheck measured at their objects · 2026-09-22

**Why this file exists:** a number scored only against our own data answers "does it
work". It cannot answer "is it better than the alternative". PeriodCheck is the
#1 Parallel-track field entry in `hack.md`. This receipt opens *their* objects.

**Not a placement claim.** No judge score is inferred.

---

## Objects opened (not title/tagline proxies)

| Object | Command / URL | Observed 2026-09-22 |
|--------|---------------|---------------------|
| Public repo | `GET https://api.github.com/repos/ahsan3274/periodcheck` | `private=false` · default `main` · pushed `2026-08-11` |
| README | `https://raw.githubusercontent.com/ahsan3274/periodcheck/main/README.md` | Claims controlled fixture **13/13** gold · hosted Cloud Run URL · Document AI + Gemini + ADK + Parallel |
| Live eval JSON | `https://raw.githubusercontent.com/ahsan3274/periodcheck/main/live-evaluation.json` | Re-derived below — do not carry README alone |
| Hosted app | `https://periodcheck-697827662390.us-central1.run.app/` | HTTP **200** · upload UI chrome present (`PeriodCheck` / upload markers) |

### Re-derived from `live-evaluation.json` (this run)

```bash
python3 -c "import json;d=json.load(open('live-evaluation.json'));print(d['summary'])"
```

| Field | Value at object |
|-------|-----------------|
| `gold_claims` | 13 |
| `correct_verdicts` | 13 |
| `scored_findings` | 13 |
| `end_to_end_accuracy` | 1.0 |
| `research_failures` | 0 |
| `successful_research` | 14 |
| `extra_extracted_claims` | 1 |

Findings array: 14 rows; 13 gold-linked; all gold-linked `correct: true`.

---

## Our arms tonight (for contrast — different task)

| Arm | Object | Result |
|-----|--------|--------|
| Offline compound | `python3 scripts/compound_exhibit_receipt.py` | A=2→B=1 Parallel, corpus_hits=2 |
| Refusal shipping vs null | `python3 scripts/eval_null_arm.py` | shipping 6/6 · null 3/6 · false-SOURCED 0/3 both |
| Artifact honesty | `python3 scripts/eval_artifact_claims.py` | OBJECT 10/10 · **NULL 6/10 > doc-baseline 4/10** |
| Live hosted stranger | our Cloud Run | `/health` stripped · `/visibility/ui` local-only · no anonymous `/clear` |
| Live Parallel compound | this VM | **BLOCKED** — no keys |

---

## Finding

PeriodCheck's public bar is a **first-run live 13/13** with traces in-repo. Ours that
strangers can run cold is **offline compound + refusal gates + an honesty gate that
caught our own stale docs**. We do not have a matching anonymous hosted live-eval
JSON on Cloud Run tonight. That gap is product-real for the submit path; closing it
is Oscar deploy + keys, not more pytest.

**What would change this reading:** a hosted Agent Science receipt with Parallel
`search_id`s on a fresh subject, anonymous partner `/health`, and a stranger URL that
still shows the visibility panel — measured after deploy, not asserted from STATUS.
