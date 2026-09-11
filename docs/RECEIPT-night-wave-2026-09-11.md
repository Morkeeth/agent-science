# RECEIPT — night wave 2026-09-11 · artifact claims + stranger truth

**Branch lane:** Cursor cloud · Agentic Cinema submit-path gaps  
**Constitution:** no Devpost / video upload / public flip / deploy run

---

## SHIPPED

1. **Qwen PRIOR LOSS gate — artifact claims at object**  
   - `fixtures/artifact-claims/set.json` (n=8, gold frozen before run)  
   - `scripts/eval_artifact_claims.py` — baseline = title/URL/pack trust; shipping = curl/GitHub/local suite  
   - `tests/test_eval_artifact_claims.py` — RED control: baseline trusts stale hosted titles  
   - Measured: baseline **3/8**, shipping **8/8**, delta **+5**, McNemar p=0.0625 (b=0 c=5)

2. **Offline compound exhibit restored under exact-assertion reuse**  
   - Paraphrase overlap in `compound-mini-B` no longer compounds (engine post-`176f5db`/`f61635e`)  
   - Fixtures + offline claim lists now share **identical** A/B assertion text; B adds one novel claim  
   - Re-run: A=**2**→B=**1** Parallel · corpus_hits B=**2** · exit 0

3. **SUBMISSION-PACK truth refresh** (`docs/SUBMISSION-PACK-2026-08-29.md`)  
   - Hosted `private-workspaces` measured; anonymous `/search`/`/partners`/`/registry` login-gated  
   - Public repo checkbox corrected (public since 2026-08-22)  
   - Stranger block adds `eval_artifact_claims.py`  
   - Controls re-measured **128/128** via `bench_check_docs.py`

4. **Live compound BLOCKED receipt** — `docs/RECEIPT-live-compound-blocked-2026-09-11.md`  
   - Names missing Parallel/Gemini keys and hosted auth wall

5. **Deploy prep for current `deploy.sh`** — `docs/DEPLOY-PREP-2026-09-11.md`  
   - Private-workspace candidate (`--no-traffic`); no Oscar deploy click

6. **Stranger scripts honest under private-workspaces**  
   - `new_user_trial.sh` — local compound + login-wall BLOCKED exit 0  
   - `long_run_goal.sh` — skips anonymous desk; offline compound + artifact-claims substitute · **12/12**  
   - `full_gate.sh` includes `eval_artifact_claims.py`  
   - `docs/FINDING-exact-assertion-compound-2026-09-11.md`

---

## VERIFIED (command → observed)

| Claim | Command | Observed |
|-------|---------|----------|
| Mutation controls | `python3 tests/test_watch_it_go_red.py` | **72 passed, 0 failed** |
| Pack counts | `python3 scripts/bench_check_docs.py` | **ALL 128/128 match SUBMISSION-PACK** |
| Artifact claims | `python3 scripts/eval_artifact_claims.py` | baseline 3/8 · shipping 8/8 · delta +5 |
| Artifact controls | `python3 tests/test_eval_artifact_claims.py` | **all passed** |
| Offline compound | `python3 scripts/compound_exhibit_receipt.py` | A=2→B=1 · corpus_hits=2 · exit 0 |
| Registry | `python3 tests/test_registry_surface.py -q` | **16/16 passed** |
| Refusal baseline | `python3 scripts/eval_refusal_baseline.py` | baseline 5/6 · shipping 6/6 · delta +1 |
| Hosted health | `curl -sS …/health` | `mode=private-workspaces` · `revision=agent-science-00028-hed` |
| Hosted /partners | `curl -sS -L …/partners` | sign-in HTML (`Access token`) |
| Hosted /visibility/ui | `curl -sS -L …/visibility/ui?q=ralph+loop+agentic` | public entry · “local-only research route” |
| Repo public MIT | `curl …/repos/Morkeeth/agent-science` | `private=false` · `license=MIT` |
| Live keys | env + `~/.config/keys/*.key` | **absent** |

---

## WRONG / left broken

1. **Opened the night assuming the offline compound receipt was still green.** First re-run went **RED** (A=2→B=3, corpus_hits=0) because paraphrase “overlap” is not reuse under exact-assertion identity. Had to open the engine, not trust the Sep-3 receipt title.

2. **Did not find a literal “26/13” stale fraction in SUBMISSION-PACK.** Re-derived all pack suite counts at object (128/128). Stale material found instead: anonymous hosted desk claims, private-repo checkbox, `engine_default` on hosted health, Devpost “Try it /visibility/ui” CONTRARY desk.

3. **Live compound not run** — keys missing; hosted `/clear` behind workspace login. Offline substitute only.

4. **McNemar p=0.0625 on artifact-claims n=8** — real delta (+5) but not significant at conventional 0.05; CIs for baseline still wide.

5. **Cost-from-billing PRIOR LOSS row still open** — no billing object on this VM.

6. **Video / Devpost / traffic promote** — Oscar only; untouched.

7. **`cache/refusal_log.db` stats = 0 rows** on this VM — receipt now prints the measured 0 instead of carrying “29 SOURCED”.

8. **~~submission/DEVPOST-PASTE.md~~** — refreshed 2026-09-11: removed anonymous CONTRARY/desk “Try it” links; stranger path is cold clone + offline compound + artifact-claims.
