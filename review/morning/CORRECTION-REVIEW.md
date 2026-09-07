# Source correction review: implementation and verification

A user can inspect a registry notice, record its effect on one exact assessment,
retain the original source warning and compare the affected decision. The CLI and
MCP share the validation contract described in
[source correction review](../../docs/source-correction-review.md).

Source lane `a266fd7` was integrated as `a647374`; CLI/MCP and decision propagation
landed at `99ebf5d`. The real MCP user pass exposed an opaque nested schema and the
wrong field name in an error. `7af5505` added the full typed contract and corrected
help. The user pass then completed unresolved → unaffected through those public
surfaces, preserving history and registry fields. This used an explicitly synthetic
correction fixture, not a real corrected-paper investigation.

Cursor reviewed frozen `99ebf5d` against `243fa1a`, ran the shipped tests and separate
reproductions. It found an older unaffected review reviving after a newer disposition,
and ambiguous DOI redirects satisfying multiple notice identities. It also exposed
an unpinned post-commit response and indistinguishable notice errors. Fix source
`39b3a9e`, integrated `597cd69`, made the latest review authoritative, rejected
ambiguous/reused notice evidence, pinned the response and exposed named failures.
The reproduction controls failed before the edits and passed afterwards.

Coordinator controls additionally found repeated review IDs/timestamps creating
false semantic changes (`279b189`) and partial registry responses dropping earlier
warnings (`ca3d0ae`). Both failure paths were exercised. Historical review records
remain; semantic comparisons ignore bookkeeping. Previously observed warnings are
retained until assessed, rather than silently replaced by a partial response.

Fable independently reviewed the same frozen `99ebf5d` and reproduced three further
gaps: withdrawal/removal/partial-retraction could receive an unaffected disposition;
a same-study mirror could escape the warning; and an unavailable original could not
accept an unresolved record. Source fix `99d3e77`, integrated `ff7d6c9`, derives
warnings across exact study identities without changing stored registry facts. arXiv
supersession remains version-specific. Withdrawn/removed/partially retracted sources
cannot be cleared; expression-of-concern remains a distinct, scoped review. An exact
null snapshot hash is accepted only for unresolved missing-source reviews.

Coordinator integration `56ce5c8` also flags evidence-only decisions when a warning
arrives on a mirror, and exposes the nullable MCP field. `d971d78` names inherited
and non-clearable warnings in the terminal. The missing-source MCP failure and
mirror decision failure fired before the fix; tests exercise the repaired paths.
Fable's stale-history finding was already fixed by `597cd69`. Its schema, error,
fixture and vocabulary comments are covered by the typed contract, named failures,
realistic fixture and revised user guide. No reported correction-review finding
remains unaddressed within the reviewed scope.

Tested code `d971d78689e98aa8756d899428fcd6bc1a5cafe0` passed the full local research
suite: **297 tests and 39 subtests in 30.12s**. A clean archive with isolated
production dependencies passed actual CLI/MCP trial, correction, missing-source
and mirror-decision flows. A real MCP agent exercised the final module at `ff7d6c9`
with seven tool calls: exact-null unresolved saved, mirror warning visible, notice
inspected and withdrawal refusal preserving version. Installed main MCP then passed
the missing-source unresolved/refusal flow at `d971d78`.

Full review reports, synthetic stores and MCP transcripts remain outside Git.
No live correction lookup was performed in this slice. Quote occurrence and registry
identity checks do not establish semantic entailment. Changed sources, notices,
warnings or assessment bindings require another explicit review. The external
reviewers examined the earlier pinned candidate; follow-up changes were exercised
locally and through the real MCP agent, not subjected to another full external audit.
