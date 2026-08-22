# NEXT STEPS — read this first, every session
_Kept current by the coordinator + build lane. If this disagrees with a chat message, open the object._

**PRODUCT:** Agent Science — a documentary script in, every factual claim out with the document that supports it, and the unsourced ones printed with the reason. **Agentic Cinema, Sep 9 14:00 PDT. Track: Parallel.**

## State (verify with `git log --oneline -1` and the test run)
- Engine, citation guard, corpus, gap report, both nouns (FACT + ASSET): **built**
- **Parallel Search: LIVE at runtime** — `Claim.source_url` is now found, not hand-filled
- **Gemini 3.5: LIVE at runtime** behind `locate()` — the model LOCATES, never ASSERTS
- Controls: run `python3 tests/test_watch_it_go_red.py`. It must be green before anything ships.
- **Agent Builder: NOT WIRED** — blocked on Oscar's GCP project + billing. This is the last admissibility item.

## The rule nothing may break
`Verdict.__post_init__` refuses to construct an uncited GREEN/RED. A proposed passage that is not
verbatim in the fetched document is `source_does_not_state_it`, never GREEN. **Do not relax this to
make a demo work.** If a slice needs it relaxed, that slice is wrong.

## Known-open, do not silently fix
- `StringLocator` still accepts the sloppy C3 claim — deliberately left, see `docs/FINDING-substring-is-not-a-statement.md`
- Refusal-correctness has no held-out set — spec only, see `docs/SPEC-refusal-correctness-set.md`
- Gemini free tier 429s after ~4 consecutive calls. **A demo script with N claims will rate-limit on camera.**

## Review lane (Cursor)
Read `FOR-CURSOR.md` + `CURSOR-LOG.md`. One writer on product code at a time. Append-only log. Never `git add -A`.
