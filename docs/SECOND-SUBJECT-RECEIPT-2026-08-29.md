# SECOND SUBJECT RECEIPT — dust-bowl

**Date:** 2026-08-29 12:55 UTC · **Subject:** `dust-bowl` (unrelated to orphan-works)
**Scripts:** `dust-bowl-A.txt` → `dust-bowl-B.txt`

## Constitution check

- Verbatim span or REFUSE — pipeline unchanged
- No deploy, no public repo, no secrets in env vars
- Slice 1 keys/deploy: not touched

## Live full chain

**NOT RUN on this VM.** Blockers:
- no Gemini credential (GEMINI_API_KEY / ~/.config/keys/gemini.key / Vertex ADC)
- no Parallel credential (PARALLEL_API_KEY / ~/.config/keys/parallel.key)
- instrument cache empty (cache/instruments.json has no fetched bodies)

Command that would run when keys are present:

```bash
python3 agent_science.py fixtures/scripts/dust-bowl-A.txt --subject dust-bowl
python3 agent_science.py fixtures/scripts/dust-bowl-B.txt --subject dust-bowl
```


## Offline proof — cross-subject reuse (dust-bowl ← orphan-works log)

Exit code: `0` (0 = pass)

```
PASS  test_not_gameable_reuse_carries_the_original_verdict_both_poles
PASS  test_second_subject_reuses_the_log_and_spends_no_parallel_call

2/2 passed
```

## Controls on this VM

`python3 tests/test_watch_it_go_red.py` → **26 passed, 13 failed (suite crashed)**

Instrument fixtures absent on this VM; several controls are UNMEASURABLE or fail
until `pull_fixtures.py` / key paths are populated.

## What a stranger can do today (slice 2)

```bash
python3 clear_corpus.py research-corpus --backfill   # seed registry (urllib only)
python3 ask_registry.py "arxiv:2511.12884"          # → SOURCED span
python3 ask_registry.py "agentlint"                 # → UNSOURCED + named cause
python3 ask_registry.py --browse
python3 ask_registry.py --serve   # http://127.0.0.1:8091/
```
