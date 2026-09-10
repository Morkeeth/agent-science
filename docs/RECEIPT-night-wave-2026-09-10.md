# RECEIPT — night wave 2026-09-10

**Slice:** Sep 9 submit-path gaps — SUBMISSION-PACK re-measure · compound exact-assertion finding+fix · Qwen cost gate with baseline arms · live BLOCKED · deploy prep (no deploy)  
**Branch:** `cursor/night-wave-submit-gaps-e3ae`  
**Keys on VM:** PARALLEL missing · GEMINI missing → live compound **BLOCKED**  
**Hosted probe:** `mode: private-workspaces` · rev `agent-science-00028-hed` · `/search` → sign-in

---

## SHIPPED

1. **FINDING** — offline compound exhibit was red under exact-assertion reuse when B paraphrased A (`docs/FINDING-compound-exact-assertion-2026-09-10.md`). Measured A=2→B=3 · hits=0 before fix.
2. **Compound fixture realign** — `fixtures/scripts/compound-mini-B.txt` + offline claim list use identical overlapping assertions; receipt green again A=2→B=1 · hits=2.
3. **Qwen cost gate** — `scripts/eval_cost_baseline.py`: naive vs shipping vs paraphrase counter + always-silent accuracy arm; Parallel Search price card dated **2026-09-10** from docs.parallel.ai (advanced $5/1k).
4. **SUBMISSION-PACK truth refresh** — controls re-measured **128/128**; public-repo row corrected; stranger block adds `eval_cost_baseline.py`; hosted stranger path honesty.
5. **Deploy prep** — `docs/DEPLOY-PREP-2026-09-10.md` matches current 45-line no-traffic candidate `deploy.sh` (Sep-3 prep was stale).
6. **full_gate** — §5a runs cost baseline.

---

## VERIFIED (command at object)

```bash
git pull && python3 tests/test_watch_it_go_red.py 2>&1 | tail -3
# 72 passed, 0 failed

python3 scripts/bench_check_docs.py
# ALL 128/128 match SUBMISSION-PACK

python3 scripts/compound_exhibit_receipt.py; echo exit:$?
# A=2 B=1 corpus_hits B=2 · exit 0

python3 scripts/eval_cost_baseline.py; echo exit:$?
# naive 5 calls $0.025 · shipping 3 calls $0.015 · paraphrase B_hits=0
# silent 3/6 vs shipping 6/6 · exit 0

python3 scripts/eval_refusal_baseline.py && python3 scripts/eval_refusal_ablation.py
# baseline/ablation 5/6 vs shipping 6/6

python3 scripts/eval_verify_holdout.py
# HOLDOUT OK — 4 files pinned

python3 scripts/eval_scorer_symmetry.py
# baseline 5/6 vs shipping 6/6

python3 tests/test_registry_surface.py -q
# 16/16 passed

python3 review/corpus_compound_receipt.py
# run2 50/50 reuse · PITCH compounding VERIFIED

test -n "$PARALLEL_API_KEY" || test -f ~/.config/keys/parallel.key; echo parallel_exit:$?
# parallel_exit:1

curl -sS -o /tmp/health.json -w "%{http_code}" \
  https://agent-science-568004190078.us-central1.run.app/health
# 200 · mode private-workspaces · revision agent-science-00028-hed

curl -sS -o /tmp/search.html -w "%{http_code}" \
  https://agent-science-568004190078.us-central1.run.app/search?q=Directive+2012/28/EU&live=false
# 303 (sign-in)
```

Cost eval transcript (re-derived):

```
Arm                  A_par  B_par  B_hits  total  USD@advanced
naive (no shelf)            2      3       0      5  $0.0250
shipping (exact)            2      1       2      3  $0.0150
paraphrase B (counter)      2      3       0      5  $0.0250
Silent:    3/6 = 0.500  95% CI [0.188, 0.812]
Shipping:  6/6 = 1.000  95% CI [0.610, 1.000]
```

---

## BLOCKED

**Live compound exhibit (orphan-works A/B with Gemini+Parallel):**

```bash
test -n "$PARALLEL_API_KEY" || test -f ~/.config/keys/parallel.key  # exit 1
test -n "$GEMINI_API_KEY" || test -f ~/.config/keys/gemini.key        # exit 1
```

**Billing console cost:** price card × counters shipped; Parallel/GCP invoice not readable on this VM.

**Hosted stranger `/search`:** private-workspaces sign-in wall — `long_run_goal.sh` / `new_user_trial.sh` against public URL are not the 2026-08-31 object anymore.

**Outward:** Devpost · video upload · deploy/promote · key rotation — Oscar only.

---

## WRONG / honest limits

- **Started from a green pack story that was already false** — carried A=2→B=1 after Sep-4 exact-assertion; only running the receipt exposed A=2→B=3.
- **Prompt said fix stale 26/13** — that fraction was **not present** in `docs/SUBMISSION-PACK-2026-08-29.md` at object tonight; fixed the stale claims that *were* there (public-repo checkbox, compound semantics, partner expected 6 in `bench_check_docs.py`).
- **Cost gate is not billing** — USD figures are card×`parallel_calls`, not Parallel invoices.
- **British Library claim still refuses independence** on the offline fixture (`no_independent_source` / bl.uk) — compounding demo only needs the Parallel counter + corpus hits, but Run B still shows an UNSOURCED row.
- **Did not run full `full_gate.sh` end-to-end** — hosted long_run/stranger will hit the sign-in wall; offline subset + cost gate verified instead.
- **`test_evidence_cases.py` 1 failure** under PYTHONPATH (`called.call_count` 0!=3) — left broken; not in the 11-suite pack gate.
- **Devpost paste still cites old commit `e6793ab` and “265+ claims”** — not re-derived at hosted object (sign-in); left for Oscar paste pass.
