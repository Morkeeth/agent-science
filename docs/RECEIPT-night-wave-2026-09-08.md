# RECEIPT — night wave 2026-09-08

**Slice:** Submit-path truth at object — CELEX cache key, exact-claim compound, artifact-claim gate, pack refresh, hosted boundary  
**Branch:** `cursor/night-wave-submit-truth-6a67`  
**Keys on VM:** PARALLEL missing · GEMINI missing → live compound **BLOCKED**

---

## SHIPPED

1. **CELEX document-cache key** — `instruments.canonical` percent-decodes path/query so `CELEX%3A` and `CELEX:` share one key; `_load_docs` remaps legacy spellings. Free lookup `2012/28/EU` → SOURCED cheap again after seed.
2. **Offline compound under exact-claim integrity** — `compound-mini-B.txt` repeats A's assertion text for overlapping claims; A=**2**→B=**1** Parallel, corpus_hits=**2**.
3. **Qwen artifact-claim gate** — `scripts/eval_artifact_claims.py` (baseline trusts pack; shipping measures suites/curl/fixtures/compound).
4. **Compound paraphrase baseline** — `scripts/eval_compound_baseline.py` (soft-term false-PASS on paraphrase; shipping FAIL; exact control PASS).
5. **SUBMISSION-PACK truth refresh** — public repo; hosted = `private-workspaces`; stranger one-command block; Devpost paste no longer points at withdrawn public desk.
6. **Deploy prep** — `docs/DEPLOY-PREP-2026-09-08.md` for current `deploy.sh` (candidate tag; no deploy run).
7. **Stranger scripts** — `new_user_trial.sh` / `long_run_goal.sh` exit 2 with BLOCKED when hosted `mode=private-workspaces`.

---

## VERIFIED (command at object)

```bash
git pull && python3 tests/test_watch_it_go_red.py 2>&1 | tail -3
# 72 passed, 0 failed  (includes CELEX %3A vs : control)

python3 scripts/seed_document_cache.py
python3 -m clearance lookup "2012/28/EU"
# [SOURCED] … tier=cheap · via route:celex · 0 Parallel API

python3 scripts/compound_exhibit_receipt.py 2>&1 | head -15
# A=2 B=1 corpus_hits=2 · Run B parallel < Run A: yes

python3 scripts/eval_compound_baseline.py
# soft-term false-PASS on paraphrase; shipping FAIL; exact control PASS; exit 0

python3 scripts/eval_artifact_claims.py
# 9/10 both arms (AC7 hosted public /search honestly False/False); exit 0

python3 scripts/bench_check_docs.py
# ALL 128/128 match SUBMISSION-PACK

python3 scripts/eval_refusal_baseline.py && python3 scripts/eval_scorer_symmetry.py
# baseline 5/6 vs shipping 6/6

curl -sS https://agent-science-568004190078.us-central1.run.app/health
# mode=private-workspaces revision=agent-science-00026-zel

curl -sS -o /dev/null -w '%{http_code}\n' https://agent-science-568004190078.us-central1.run.app/search?q=x&live=false
# 303

gh api repos/Morkeeth/agent-science --jq '{private,visibility}'
# {"private":false,"visibility":"public"}

test -n "$PARALLEL_API_KEY" || test -f ~/.config/keys/parallel.key; echo $?
# 1 — MISSING

bash scripts/verify_cold_clone.sh
# === cold-clone verify OK === (steps 1–11, incl. artifact + compound baseline)
```

### Pre-fix findings (why this wave existed)

Measured **before** code/docs changes on this VM:

| Object | Measured | Pack / memory claimed |
|--------|----------|------------------------|
| `instruments.document(CELEX:…)` after seed | **miss** (cache under `%3A` only) | free CELEX SOURCED |
| `compound_exhibit_receipt.py` (paraphrase B) | A=2 B=3 hits=0 **FAIL** | A=2→B=1 hits≥1 |
| Hosted `/search` | **303** sign-in | public SOURCED desk |
| Repo visibility | **public** | "Private until submit" |
| Live compound keys | **MISSING** | — |

---

## BLOCKED

**Live compound exhibit (orphan-works A/B on hosted `/clear`):**

```text
PARALLEL_API_KEY / ~/.config/keys/parallel.key — MISSING
GEMINI_API_KEY / ~/.config/keys/gemini.key — MISSING
Hosted /clear — 303 (private-workspaces; not a public clearance desk)
```

Offline `compound_exhibit_receipt.py` is authoritative for this VM. Hosted stranger scripts now refuse early with exit 2.

**Oscar only:** deploy / Devpost / video / whether to restore a public judge desk.

---

## WRONG / honest limits

- **Started by assuming pack counts were the gap** — 128/128 already matched; the real breaks were CELEX encoding, exact-claim compound, and hosted private mode. Nearer proxy (suite table) answered faster than opening hosted `/search` and the compound receipt.
- **Alias `orphan works directive` → NOT_CLEARED** after exact-assertion integrity (aliases do not reuse another assertion's verdict). `2012/28/EU` and `Directive 2012/28/EU` SOURCED via CELEX; casual alias free-hit is not restored.
- **Artifact eval after pack refresh shows arms tied 9/10** — the embarrassing false-GREENs were caught by measuring first, then the pack was corrected; a second run cannot re-show the pre-fix discordant pairs without a frozen stale pack fixture.
- **Seeded EUR-Lex body is 355 chars** (fixture/partial) — span is real but thin; not a full directive text.
- **Did not run `full_gate.sh` end-to-end** — hosted long_run/new_user now intentionally exit 2 on private-workspaces; would fail the old "FULL GATE OK" contract until Oscar chooses narrative A (cold-clone) or B (restore public desk).
- **Live Parallel/Gemini compound not re-run** — no keys.
- **`cache/` mutations** from seed/boot are local — not committed.
