# Review a source correction

A registry notice marks affected conclusions for review. Read the original source
and the notice before deciding whether the conclusion still holds. The engine
checks quote occurrence, document identity and version bindings. Your interpretation
of the correction remains authored judgment.

```text
agent-science research source-reviews CASE_ID --json
agent-science case source CASE_ID --evidence NOTICE_EVIDENCE_ID --version CASE_VERSION
agent-science research source-review CASE_ID --version CASE_VERSION --review-file review.json
agent-science research compare CASE_ID --from-version PREVIOUS_VERSION
```

Use `agent-science case source --help` for source pagination. If the notice is not
saved, retrieve it through an explicitly permitted research read; review itself
makes no network or provider call. Do not interpret missing access as no effect.

`source-reviews` returns `pending`, `resolved` and historical `reviews`. Each row
names the assessment, source, warning fingerprint and notice identities. Copy
`assessment_id`, `evidence_id`, `source_snapshot_hash` and `warning_fingerprint`
from the inspected row into the review object. Add:

- `disposition`: `unaffected`, `revise` or `unresolved`.
- `rationale`: 20–5000 characters explaining the effect on this exact finding.
- `notices`: one entry per inspected registry notice, with `notice_identity`,
  `evidence_id`, `quote` and `snapshot_hash`. The evidence ID is the saved notice
  document. Use an exact 20–4000 character quote and its current snapshot hash.

`unaffected` requires every notice in that warning set to be inspected. It resolves
only the exact assessment and source snapshot. `revise` records that reassessment is
needed; submit a superseding finding through the existing research flow. It does not
rewrite the claim automatically. `unresolved` keeps the review requirement and can
use an empty notice list when access is missing. If the source itself has no saved
snapshot, copy its `null` snapshot hash exactly and use `unresolved`; do not invent
a hash. A missing source body cannot be cleared.

After a `revise` review, submit the superseding assessment, inspect its pending
review and explain how the correction is accounted for. `unaffected` on that new
assessment means the inspected notice requires no further change to its stated scope.

The full typed object is also exposed in MCP `science_research` tools/list. Actions
are `source-reviews` with `case_id`, and `source-review` with `case_id`, `version`
and `source_review`. CLI and MCP use the same validator.

Registry warnings, body timestamps and historical cases stay intact. A different
warning, changed original or notice body, changed condition, or new assessment
reopens review. Retraction, withdrawal, removal, partial-retraction and supersession
warnings cannot be cleared by this action. An expression of concern can receive an
explicit scoped review; it is not silently relabeled a retraction. Exact DOI mirrors
share warnings, while version-specific arXiv notices apply to their named version.
Each assessment still needs its own review. The terminal names inherited warnings.
A resolved conclusion can still cause a saved decision to need review because its
supporting interpretation changed. Inspect the comparison before replacing that
decision; no automatic reversal is implied.

No semantic truth score is produced. An exact quote can still be interpreted
incorrectly. A review is visible with its rationale so another reader can challenge
it against the retained source version.

A later review remains authoritative even if the source body returns to an older
version. A partial registry response cannot erase a previously observed warning.
Distinct notice identities need distinct, unambiguous saved evidence; conflicting
DOI redirects are not treated as two inspected notices. Error codes identify missing,
stale, ambiguous, unavailable or separately flagged notice evidence. The response
after a review is pinned to that committed case version.
