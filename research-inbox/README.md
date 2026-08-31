# research-inbox — the LIVE sink

`clearance.ingest` writes here. Every claim the product ingests at runtime lands as a
dated `[CLAIM]`/`[URL]` markdown file, as an audit trail of what was put into the
registry and when.

**No published number is computed over this directory.** That is the whole reason it
exists. Until 2026-08-31 ingest wrote into `research-corpus/`, the directory the evals
replay as their measurement population, so using the product moved its own published
denominator — n=313 became n=314 mid-run and a clean checkout read 312.

- `research-corpus/` is the FROZEN measurement population. Hashed in its `MANIFEST.json`,
  resolved through `clearance/population.py`, replayed by `scripts/eval_*.py`. Never write
  there. Growing it is a reviewed act: add the files, re-run
  `python3 scripts/freeze_population.py`, commit the manifest, and say which numbers moved.
- The control that fails if the two are ever the same directory, or if a published figure
  is computed over this one, is `tests/test_frozen_population.py`.
