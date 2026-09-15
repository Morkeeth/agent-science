# FINDING — CELEX URL encoding broke free-tier lookup · 2026-09-15

## Object

`python3 -m clearance lookup "2012/28/EU"` after `scripts/seed_document_cache.py`.

## Failure (watched)

```
[UNSOURCED] 2012/28/EU
  search_found_no_admissible_source
  tier=cheap · via route:celex · 0 Parallel API
  why: searched, read 0 of 1 candidate document(s)
```

Routing constructed:

`https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32012L0028`

Seed / cache key was:

`http://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32012L0028`

`instruments.canonical()` normalized scheme only. Percent-encoding of `:` remained → cache miss → registry poison (`UNKNOWN` / `search_found_no_admissible_source`) on the exact stranger query the README and `new_user_trial.sh` advertise.

## Fix

`canonical()` now `urllib.parse.unquote`s before scheme collapse. `_doc_hit` resolves legacy encoded keys. Control extended in `t_one_key_per_document_not_per_url_spelling`:

`CELEX%3A32012L0028` and `CELEX:32012L0028` must share one key; different CELEX numbers must not.

## Re-measure

```bash
python3 scripts/seed_document_cache.py
python3 -m clearance lookup "2012/28/EU"
# [SOURCED] … tier=cheap · via route:celex · 0 Parallel API

python3 tests/test_watch_it_go_red.py
# 72 passed, 0 failed
```

## Also measured

Alias `orphan works directive` did not contain a CELEX shape, so cheap routing on the raw phrase returned `dictionary_miss` while `2012/28/EU` was SOURCED. `dictionary.lookup` now runs `_cheap_route` on `canonical_query(raw)` as well. Free registry replay still requires `q == raw` (exact assertion) — aliases do not silently reuse another wording's verdict.

## Related compound finding

Offline compound exhibit with **paraphrased** mini-B failed A=2→B=3, corpus_hits=0 under exact-assertion corpus identity (`t_the_corpus_requires_exact_assertion_identity`). Fixtures aligned to identical overlapping assertions (same pattern as `test_cross_subject_reuse.py`). Paraphrase compounding is not claimed.
