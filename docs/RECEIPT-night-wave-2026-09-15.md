# RECEIPT — night wave 2026-09-15

**Slice:** SUBMISSION-PACK truth + CELEX/alias free-tier repair + artifact-claim Qwen gate + deploy prep (no deploy)  
**Branch:** `cursor/night-wave-sep15-8a91`  
**Keys on VM:** PARALLEL missing · GEMINI missing → live compound **BLOCKED**  
**Hosted:** `mode=private-workspaces` rev `agent-science-00028-hed` — public `/search`/`/clear` not exposed

---

## SHIPPED

1. **CELEX URL encoding fix** — `clearance/instruments.canonical` unquotes `%3A`↔`:`; `_doc_hit` resolves legacy keys. Free-tier `lookup "2012/28/EU"` → SOURCED cheap again.
2. **Alias → CELEX cheap route** — `dictionary.lookup` runs cheap routing on `canonical_query(raw)` so `orphan works directive` reaches EUR-Lex without free verdict-reuse of a different assertion.
3. **Compound-mini exact assertions** — paraphrased B failed A=2→B=3, hits=0 under exact-assertion corpus identity; B fixture + offline claim lists aligned to identical overlapping sentences → A=2→B=1, hits=2.
4. **Qwen gate: artifact claims at HEAD** — `scripts/eval_artifact_claims.py` (baseline trusts pack; shipping re-derives). First run caught stale "Private until submit" + pin `e6793ab` before pack refresh.
5. **SUBMISSION-PACK truth refresh** — public repo [x], HEAD pin, 128/128 re-measured, stranger block, hosted private note; DEVPOST 127→128.
6. **Deploy prep** — `docs/DEPLOY-PREP-2026-09-15.md` matches current candidate-only `deploy.sh` (Oscar click only).
7. **Live compound BLOCKED receipt** — `docs/RECEIPT-live-compound-BLOCKED-2026-09-15.md`.

---

## VERIFIED (command at object)

```bash
git pull && python3 tests/test_watch_it_go_red.py 2>&1 | tail -3
# 72 passed, 0 failed

python3 scripts/seed_document_cache.py
python3 -m clearance lookup "2012/28/EU"
# [SOURCED] … tier=cheap|free · via route:celex|dictionary_exact · 0 Parallel API

python3 -m clearance lookup "orphan works directive"
# [SOURCED] … tier=cheap · via route:celex · 0 Parallel API

python3 tests/test_dictionary.py
# 5/5 passed (includes t_alias_reaches_celex_cheap_route)

python3 scripts/compound_exhibit_receipt.py
# A=2 → B=1 Parallel · corpus_hits B=2 · exit 0

python3 scripts/bench_check_docs.py
# ALL 128/128 match SUBMISSION-PACK

python3 scripts/eval_artifact_claims.py
# Baseline 7/7 · Shipping 7/7 (after pack refresh; first run was discordant on public+pin)

python3 scripts/eval_refusal_baseline.py
# Baseline 5/6 · Shipping 6/6 · delta +1

gh api repos/Morkeeth/agent-science --jq .private
# false

curl -sf https://agent-science-568004190078.us-central1.run.app/health
# mode=private-workspaces · revision=agent-science-00028-hed
```

---

## Product journey (intended user · local CLI — observed)

| Dimension | Status | Evidence |
|-----------|--------|----------|
| 1. Promised user value | **observed** | Stranger gets SOURCED span + EUR-Lex URL for `2012/28/EU` / alias with no API key |
| 2. Independent use | **observed** (local) | One-command block in SUBMISSION-PACK; no builder narration required for lookup + compound |
| 3. Distinctive promise | **observed** | Verbatim span or refuse; compound A→B Parallel drop on exact overlapping claims |
| 4. Action and return | **observed** | Second script reuses corpus (hits=2); shelf grows (`boot_registry` → 241 local claims) |
| 5. Access | **partial** | Local cold path works. Hosted stranger clearance **absent** without workspace token (303→/login). Subjective: judges needing one-click hosted desk will not see the old public demo. |

Revision tested: this branch on top of `ea05a10`. Screenshots of hosted UI would only prove login wall — not usefulness.

---

## BLOCKED

- Live Parallel/Gemini compound on this VM — no keys
- Hosted public `/clear` A/B — product is private-workspaces
- Outward acts (Devpost, video, deploy traffic promote) — Oscar only

---

## WRONG / honest limits

- **First assumed pack suite counts were stale** — they were already 128/128; the real pack lies were public-repo status and commit pin (caught by artifact gate before refresh).
- **Carried "265+ claims"** in pack until re-measure — local shelf after boot was **241**; hosted truths UI not readable without login. Pack now says re-derive.
- **Paraphrase compound was falsely claimed** by compound-mini-B under exact-assertion rules — exhibit failed when opened; fixed fixtures rather than weakening identity.
- **Did not run `full_gate.sh` end-to-end** — hosted long_run/new_user_trial expect public `/search` and will fail on current revision; cold + offline subset verified instead.
- **Alias free registry replay still refuses** by design (`q == raw`); only cheap routing on the canonical form closes the casual phrasing path — exact free replay of a different assertion remains forbidden.
- **n=6 eval still not significant** — McNemar p=1.0000 on refusal baseline.
