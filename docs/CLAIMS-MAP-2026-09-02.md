# Claims → evidence map · 2026-09-02

**Scope:** every factual claim in `docs/PITCH-TOMORROW.md` and `SUBMISSION.md` (numbers, "live", "verified", partner names, test counts).
**Method:** each URL was curled and each script was run on 2026-09-02 (~23:30–23:55 UTC) from a fresh worktree of `main` @ `5d03583`; the branch was then rebased onto `main` @ `a055ba3` (the sibling lane's log-poison fix), which had scrubbed the same two privacy lines in parallel — main's wording kept for both. Outputs are pasted, not quoted from other docs. A claim is **PROVEN** only when the proof is a URL that returned 200 today, a script + its output line, or a file:line that states it.
**Probe machine:** macOS, Python 3.12, `~/.config/keys/{gemini,parallel}.key` present (so the history control does not early-return).

**Totals:** 35 claims (19 PITCH + 16 SUBMISSION) · **32 PROVEN** · **3 UNPROVEN as written** — P4 ("on camera"), P16 (proof pointed at the wrong file), S14 (buyer names); all softened or re-pointed in the two docs — see §F. **S15 (E&O numbers) resolved 2026-09-03:** the buyer §'s dollar figures now carry primary sources and the unsourced numbers were removed.

---

## A · Hosted surfaces (curl, 2026-09-02)

```
$ for p in /health /partners "/visibility/ui?q=ralph+loop+agentic" /truths/ui /registry /popular/ui; do curl -s -o /dev/null -w "$p %{http_code} %{size_download}B\n" "$H$p"; done
/health                                       200 322B
/partners                                     200 1713B
/visibility/ui?q=ralph+loop+agentic           200 4995B
/truths/ui                                    200 2929B
/registry                                     200 96383B
/popular/ui                                   200 3103B
```

```
$ curl -s $H/health
{"ok": true, "service": "agent-science", "gemini": true, "gemini_path": "vertex:hack-fleet",
 "parallel": true, "parallel_sdk": true, "parallel_sdk_version": "1.3.2", "parallel_transport": "parallel-web",
 "agent_builder": true, "adk_version": "2.7.1", "engine_default": "adk"}
```

```
$ curl -s $H/truths/ui | <strip tags>
… Truths dashboard · Most websearched claims · field adoption strip · hit rate at object
Shelf: 276 claims · hit rate 0.66 · 191 queries logged
Top queries: 72 ralph loop agentic · 23 Directive 2012/28/EU · 20 2012/28/EU · 18 ralph loop agentic practice …
```

```
$ curl -s "$H/visibility?q=ralph+loop+agentic" | python3 -c "…"
top keys: ['query','mode','primary','personal_prior','aliases','field','agentic_practices','peer_queries','optimization','parallel_probes','discipline','transparency','stack_fit','shelf_stats','popular_bundle']
primary.verdict: CONTRARY_TO_RESEARCH  cause: field_outruns_research  parallel_api_calls: 0  cost_tier: free
transparency keys: ['angles_searched', 'shallow_route', 'imbalance']

$ curl -s "$H/visibility/ui?q=ralph+loop+agentic" | <strip tags>
… Primary verdict CONTRARY_TO_RESEARCH tier=free · parallel=0 … Transparency · what was searched … IMBALANCE: github (0.21) …
```

```
$ POST $H/clear  {"script": "94% of film archives are unclearable for AI training.\n", "subject": "claims-map-2026-09-02"}
http 200 secs 19.6
claims: 1 sourced: 0 unsourced: 1 parallel_api_calls: 1 engine: adk corpus_hits: 0
C1 · UNSOURCED · search_found_no_admissible_source · 94% of film archives are unclearable for AI training.
```

```
$ bash scripts/demo_clearance_desk.sh docs/cold-scripts/google-books-settlement.txt claims-map-desk-0902   (exit 0)
claims: 4 | sourced: 0 | unsourced: 4
parallel_api_calls: 3 | engine: adk
C1 · UNSOURCED · search_found_no_admissible_source
C2 · UNVERIFIED INDEPENDENCE · no_independent_source
C3 · UNSOURCED · search_found_no_admissible_source
C4 · UNVERIFIED INDEPENDENCE · no_independent_source
```

## B · Public record (curl, 2026-09-02)

```
$ curl -s https://api.github.com/repos/Morkeeth/agent-science | jq .private,.license.spdx_id,.created_at,.visibility
false  MIT  2026-08-22T17:17:41Z  public
$ curl -s "https://api.github.com/repos/Morkeeth/agent-science/events?per_page=100" | jq 'PublicEvent'
PublicEvent 2026-08-22T17:17:41Z
$ curl -sL -o /dev/null -w "%{http_code}" https://agentic-cinema.devpost.com/
200   page text: "Agentic Cinema: The Blockbuster Hackathon  Deadline: Sep 9, 2026 @ 2:00pm PDT … $ 75,000 in cash"
```

## C · Scripts (run 2026-09-02 in the worktree)

```
$ bash scripts/verify_cold_clone.sh        (exit 0)
2. Mutation controls (watch_it_go_red)...   72 passed, 0 failed
3. ADK default path...                      5/5 passed
4. Partner runtime wiring...                6/6 passed
5. SUBMISSION-PACK doc gate...              ALL 127/127 match SUBMISSION-PACK
6. Eval gate:  McNemar p=1.0000 (b=0 c=1 discordant)  FINDING: shipping beats ablation by 1 item(s)
=== cold-clone verify OK ===

$ python3 tests/test_watch_it_go_red.py | grep -iE "key|secret"
  PASS  missing key raises and is never stubbed
  PASS  the key is nowhere in the tree          ← the history control (tests/test_watch_it_go_red.py:535-553): tree + `git log -p --all`
  PASS  no deploy surface passes a secret in the clear
  PASS  the secret scanner actually catches one
72 passed, 0 failed

$ git log -p --all | grep -cE "AIza[0-9A-Za-z_-]{35}"                                  → 0
$ git log -p --all | grep -oE "(pk|sk)[-_](live|test)[-_][A-Za-z0-9]{3,}" | sort | uniq -c   → 4 pk-live-abc   (test fixture only)
$ git log -p --all | grep -ciE "(PARALLEL_API_KEY|GEMINI_API_KEY|GOOGLE_API_KEY)\s*[=:]\s*['\"]?[A-Za-z0-9_-]{20,}"  → 0

$ bash scripts/full_gate.sh   (main tree, 23:3x–23:4x UTC)
--- 1. Secret surfaces ---           6 passed, 0 failed
--- 2. Seed + mutation controls ---  72 passed, 0 failed
--- 3. Partner + ADK ---             6/6 · 6/6 · 5/5 passed
--- 4. Product suites ---            4/4 · 16/16 · 4/4 · popular OK · stack OK · all passed · 5/5 · 4/4 · 4/4 · 3/3
--- 5. Docs gate ---                 ALL 127/127 match SUBMISSION-PACK   (watch_it_go_red 72 + adk 5 + registry 16 + … + parallel_integration 6)
--- 5b. Privacy ---                  PRIVACY OK   ← FALSE GREEN, see §D
--- 6. Cold clone ---                === cold-clone verify OK ===
--- 7. Hosted long run ---           passed=18 failed=1  (FAIL watch_it_go_red — raced with a concurrent `pytest` I had started in the same tree)
   re-run #1 alone (worktree):       LOCAL 8/8 OK · hosted surfaces 6/6 OK · then AssertionError on `/search?q=2012/28/EU&live=false` (transient: the same URL returned SOURCED/free/0 Parallel 30 s later)
   re-run #2 alone (worktree, ~23:50Z):  passed=19 failed=0  EXIT=0
     Run A: parallel=1 corpus_hits=0 engine=adk
     Run B: parallel=0 corpus_hits=1
     COMPOUND PASS · stats after: claims=280 hit_rate=0.654 queries=211   ← the shelf moved 276→280 during this hour from my own probes; numbers on the shelf are read-at-use
     receipt: docs/LONG-RUN-RECEIPT-2026-09-02.md

$ bash scripts/demo_truth_layer.sh      (exit 0)
--- 5 · Hosted visibility JSON (first keys) ---
primary: CONTRARY_TO_RESEARCH
transparency: ['angles_searched', 'shallow_route', 'imbalance']
=== done ===

$ python3 -m pytest -q                  (exit 3)
INTERNALERROR> SystemExit: 0 … no tests ran        ← tests are `t_*` functions with their own runners; `tests/test_watch_it_go_red.py` calls sys.exit at import. The repo's runners are `python3 tests/test_*.py` (what full_gate / verify_cold_clone call). pytest is not a runner here.

$ python3 -m clearance.stack_cli visibility "ralph loop agentic" --full --no-personal | head   → "# Agent Science websearch · full visibility / # Query · ralph loop agentic / ## 0 · Personal prior …"
$ python3 -m clearance.stack_cli lookup "ralph loop agentic practice"                          → [CONTRARY_TO_RESEARCH] … tier=free · via contrary_check · 0 Parallel API
$ python3 -m clearance.stack_cli stack-fit "science_lookup MCP fleet"                         → fit=fits stack=python,cursor …
$ ffprobe demo/demo-final.mp4 → duration 102.000000
```

## D · Privacy (the reason this map exists)

```
$ git grep -lE '<home path>|<vault name>|<claude projects dir>'   (before)  → scripts/scrub_privacy_paths.py   (1 file: the scrub script's own regexes carried the literal home path; now /Users/[^/\s]+/CODE/…)
$ git grep -lE '<home path>|<vault name>|<claude projects dir>'   (after)   → (none)  count=0
```

`scripts/privacy_grep.sh` was a **false green**: it ran `git ls-files | xargs rg … 2>/dev/null || true`, and on this machine `rg` is a shell function (Claude Code snapshot), not a binary `xargs` can exec → `xargs: rg: No such file or directory` was silenced and it printed `PRIVACY OK` having scanned **zero files**. The uncommitted `hack.md` STATE line carried a home-relative `CODE/fleet-ops/…` path straight through it. Rewritten on `git grep`, exits 2 if the candidate list is empty, and verified both ways:

```
$ bash scripts/privacy_grep.sh                       → PRIVACY OK: 0 hits in 314 tracked files (home paths, ~/CODE, vault paths)   exit=0
$ echo 'x /Users/<someone>/CODE/x' >> README.md   # planted with a real username on the probe machine; elided here so the map does not trip the control; bash scripts/privacy_grep.sh
                                                     → PRIVACY FAIL: 1 hit(s) in tracked files (scanned 314)  README.md:238:x /Users/<someone>/CODE/x   exit=1
```

---

## E · The map

Status key: **PROVEN** = URL 200 today / script output pasted above / file:line. **UNPROVEN** = nothing in the repo or on the wire proves it as written.

### `docs/PITCH-TOMORROW.md`

| # | Claim (as it stood this morning) | Where it is proven | Status |
|---|---|---|---|
| P1 | Deadline 2026-09-09 14:00 PDT · "8 days" | Devpost page text "Deadline: Sep 9, 2026 @ 2:00pm PDT" (§B) · 8 days was true for the doc's 09-01 date; today it is 7 | PROVEN (day count updated to 7) |
| P2 | Run A **1** Parallel → Run B **0**, `corpus_hits=1` (sealed) | `docs/SEALED-PREDICTION-2026-08-31.md` table (A=1, B=0, corpus_hits 0→1, subject `longrun-0831-1320`, commit `c845812`) · today's hosted A/B: first pass (warm shelf) A parallel=0 corpus_hits=0 → B parallel=0 corpus_hits=1; re-run #2 on a fresh subject **A parallel=1 → B parallel=0, corpus_hits 0→1, COMPOUND PASS, 19/19** (§C) — the headline reproduced live today | PROVEN |
| P3 | Four partners wired at runtime: Vertex, Parallel, Cloud Run, ADK | `/health` → `gemini_path: vertex:hack-fleet`, `parallel_sdk: true` (1.3.2), `engine_default: adk` (2.7.1); host `*.run.app` (§A) | PROVEN |
| P4 | "We refused our own pitch headline **on camera**" | Refusal: hosted `POST /clear` today → `C1 · UNSOURCED · search_found_no_admissible_source` (§A); `PITCH.md:86-87`; `cache/search_receipts.jsonl:2-5` (`n_candidates: 0`). **"On camera":** `demo/FILM-AND-SUBMIT.md:32` puts the beat at 1:00 in the *script*; nobody in this lane watched `demo/demo-final.mp4` to confirm it is in the cut | refusal PROVEN · "on camera" **UNPROVEN** → softened |
| P5 | `/visibility/ui?q=ralph+loop+agentic` live: CONTRARY stamp + transparency keys | UI 200 shows `CONTRARY_TO_RESEARCH` + Transparency pane; the literal keys `angles_searched/shallow_route/imbalance` are in the JSON `/visibility?q=…` (§A) | PROVEN (pointer fixed: keys → JSON URL) |
| P6 | `/truths/ui` — **271 claims** (live 2026-09-02) | `/truths/ui` → `Shelf: 276 claims · hit rate 0.66 · 191 queries logged` (§A) | stale number → **updated to 276** with timestamp |
| P7 | Hosted URL · film URL · "deployed with `/visibility` + `/truths/ui`" | all 200 (§A) | PROVEN |
| P8 | Truth layer code on `main`: `clearance/visibility.py`, `contrary.py`, `stack_fit.py` | `git ls-files` → all three tracked | PROVEN |
| P9 | **284 claims** on shelf (live) / 271 in the same row | live 276 (§A) — the row disagreed with itself | stale → **updated to 276** |
| P10 | Deployed: `/health` → `engine_default: adk`, `parallel_sdk: true` | §A | PROVEN |
| P11 | `/truths/ui` live → dashboard HTML | 200, 2929 B, "Truths dashboard" (§A) | PROVEN |
| P12 | 52 inbox ingests | `docs/RECEIPT-agent-science-shape-2026-09-01.md:27` "`auto_ingest_inbox.py` → 52 ingested, 0 failed" — a receipt, not re-run (re-running would ingest again) | PROVEN (receipt) |
| P13 | Film scout doc | `docs/FILM-SCOUT-COMMANDS.md` tracked | PROVEN |
| P14 | Full gate OK | steps 1–6 OK today (§C); step 7 hosted long run 18/19 on the first pass (self-inflicted race), then **19/19** on the clean re-run (§C) | PROVEN |
| P15 | Demo commands (4 copy-paste lines) | all four ran (§C) | PROVEN |
| P16 | Claim-audit row "Refused own pitch headline → `fixtures/shift-ai-training-vs-noncommercial.md`" | that fixture is the Europeana 600-item table and contains no "94%" (`grep -n 94 fixtures/shift-ai-training-vs-noncommercial.md` → empty) | wrong pointer → **re-pointed** to the live `/clear` + `PITCH.md` §C5 |
| P17 | Cold clone stranger path | `docs/COLD-CLONE-2026-09-02.md` tracked · `verify_cold_clone.sh` exit 0 today (§C) | PROVEN |
| P18 | Hard public claim trace | `docs/TRACE-2026-09-02-google-books.md` tracked · same script re-run on hosted today (§A desk demo, 4 claims → 4 unsourced/independence) | PROVEN |
| P19 | "PeriodCheck wins first-run UX" (objection table) | `hack.md` FIELD table row 1 (measured 2026-08-31) — competitor observation, not re-probed | PROVEN (file:line, dated) |

### `SUBMISSION.md`

| # | Claim | Where it is proven | Status |
|---|---|---|---|
| S1 | Event URL + deadline Sep 9 2026 14:00 PDT | Devpost 200, page text (§B) | PROVEN |
| S2 | Repo public + MIT | GitHub API `private=false`, `license=MIT`, `PublicEvent 2026-08-22T17:17:41Z` (§B) · `LICENSE:1` | PROVEN |
| S3 | Hosted URL | 200 (§A) | PROVEN |
| S4 | Stranger path: `verify_cold_clone.sh` · `demo_truth_layer.sh` · `demo_clearance_desk.sh` | exit 0 · exit 0 · exit 0 (§C, §A) | PROVEN |
| S5 | Surfaces `/visibility/ui` · `/truths/ui` · `/registry` · `/health` · `/partners` | all 200 (§A) | PROVEN |
| S6 | Ship #1 hosted live | §A | PROVEN |
| S7 | Ship #2 public repo + MIT | §B | PROVEN |
| S8 | Ship #3 "Controls 127/127" | `scripts/bench_check_docs.py` → `ALL 127/127 match SUBMISSION-PACK` — 127 is the **test count across 11 suites** (72 of them mutation-watched), not 127 distinct guards | PROVEN (relabelled) |
| S9 | Ship #4 sealed compound A=1→B=0 | `docs/SEALED-PREDICTION-2026-08-31.md` (P2) | PROVEN |
| S10 | Ship #5 demo video built, 102 s | `ffprobe demo/demo-final.mp4` → 102.000000 (§C) | PROVEN |
| S11 | Ship #7 privacy grep = 0 | true **only after** the rewrite (§D); this morning's ✅ was a check that scanned nothing | PROVEN today (control rewritten) |
| S12 | Runtime integrations table (Parallel SDK, Vertex, Cloud Run, ADK) | `/health` (§A) | PROVEN |
| S13 | Sealed prediction measured A=1→B=0, corpus_hits=1 | P2 | PROVEN |
| S14 | Buyer names: Chubb Media & Entertainment, Beazley, BBC Studios, Participant | no contact, receipt, or doc in the repo names any of them (`git grep -n "Chubb\|Beazley"` → only SUBMISSION.md) | **UNPROVEN** → replaced by illustrative roles + "no named buyer contacted" |
| S15 | Budget line — E&O premium | **Resolved 2026-09-03.** The percentage frame is wrong-object: no source expresses documentary E&O as % of budget; sources give a flat premium of ~$2,000–$10,000 — Desktop Documentaries (broker C&S International Insurance Brokers, "$2,000 … up to $3,500", undated, read 2026-09-03) and Wrapbook ("$2,500 to $10,000 for a standard three-year term with a $1 million limit", 2025-10-01, read 2026-09-03). The only %-of-budget figure any source gives is *all* insurance combined ≈ 2.5% (Media Services, *Film Production Insurance: A Definitive Guide*, 2022-07-12 — "All adding up to about 2.5% of the film or show's budget"), which is why E&O-as-a-percentage was the wrong object. | **PROVEN** (buyer § figures cited; see Sources there) |
| S15b | Budget line — $15k–$80k researcher time | **Removed 2026-09-03, no primary source.** Archives access is "a few hundred to several thousand dollars" per collection (Academy Voices, 2024-04-07); there is no union rate card for documentary research — the Archival Producers Alliance (founded 2023) publishes best-practice guidance, not rate minimums (NEA/arts.gov, 2025-03-07). No source produces a $15k–$80k per-hour-long-doc total; we did not manufacture one. | **REMOVED** (deleted from SUBMISSION.md §Buyer) |
| S16 | Hosted desk `POST /clear` · cold demo `demo_clearance_desk.sh` | §A | PROVEN |

**Counts:** PITCH 19 rows → 17 PROVEN, 2 UNPROVEN as written (P4 "on camera"; P16 wrong proof pointer); SUBMISSION 16 rows → 15 PROVEN, 1 UNPROVEN (S14 buyer names); S15 resolved 2026-09-03 (E&O premium sourced; $15k–$80k researcher figure removed as unsourced). Total 35 → **32 PROVEN · 3 UNPROVEN**. P6/P9 were **stale** (271/284 vs live 276) and are counted PROVEN because the object exists and the number was refreshed — they are why the docs now say "re-curl before saying a number".

---

## F · Edits made to the two docs (2026-09-02)

| Doc | Change |
|---|---|
| PITCH-TOMORROW | "8 days" → "7 days (as of 2026-09-02)"; claims-map pointer added |
| PITCH-TOMORROW | "refused our own pitch headline **on camera**" → "in the product" + the live `/clear` result; "say on camera only after checking the cut" |
| PITCH-TOMORROW | transparency keys claim re-pointed from the UI to the JSON `/visibility?q=…` |
| PITCH-TOMORROW | 271 / 284 claims → **276** (three places), with timestamp and "re-curl" note; "Removed / do not say" now lists 271 and 284 |
| PITCH-TOMORROW | audit row "Refused own pitch headline" re-pointed from the Europeana fixture to the live `/clear` + `PITCH.md` §C5 + `search_receipts.jsonl` |
| PITCH-TOMORROW | "Full gate OK" rows now say steps 1–6 OK today and point here for step 7 |
| SUBMISSION | "Controls 127/127" relabelled: tests across 11 suites, proof = `bench_check_docs.py` |
| SUBMISSION | privacy row dated today, notes the rewrite |
| SUBMISSION | buyer names (Chubb, Beazley, BBC Studios, Participant) **removed** → illustrative roles, "no named buyer has been contacted yet" |
| SUBMISSION | E&O budget line **sourced 2026-09-03**: flat premium ~$2,000–$10,000 cited to Desktop Documentaries (C&S broker) + Wrapbook; the "$15k–$80k researcher time" and "0.5–2% of budget" numbers **removed** as unsourced (no primary source; %-of-budget is the wrong object — only all-insurance-combined ≈2.5% has a source) |

## G · Not done / could not do

- Did not watch `demo/demo-final.mp4` to confirm the refusal beat is in the cut (only duration measured). Oscar or the film lane confirms before saying "on camera".
- E&O budget numbers **now sourced (2026-09-03):** the premium is a flat fee (~$2,000–$10,000), cited to a broker interview (C&S International) and Wrapbook; the "$15k–$80k researcher time" and "0.5–2% of budget" figures were **removed** — no primary source, and archival research has no union rate card (Archival Producers Alliance publishes guidance, not rates). Could not verify a broker's own rate page at the object (Front Row Insurance returns 403 to automated fetches), so it is not cited even though a search index surfaced documentary-specific numbers there.
- No deploy, no push, no Devpost edit, no key touched. Key files were only `ls`-ed to confirm the history control would not early-return.
- `docs/LONG-RUN-RECEIPT-2026-09-02.md` and `research-inbox/2026-09-02-claim.md` were generated in the **main** tree by my `full_gate.sh` run and left untracked there; `cache/search_receipts.jsonl` gained rows from the demo runs and is left unstaged.
- Another lane was editing `agent_science.py`, `clearance/refusal_log.py`, `cloud/service.py` in the main tree while this ran (mtimes 23:46–23:47Z); it landed as `a055ba3` on `main` and this branch now sits on top of it. The cold-clone verify below was re-run after the rebase.
