# Saved-source scientific review

All 18 recorded answers in frozen campaign `0c3c278d3e704325` now have source-grounded
reviews. The original observations remain byte-for-byte unchanged. The manifest is
`eca84eae7581297bffbabecc2ab7988d23ce52dc3f377c4ddbf1f394bc7cf183`.

Across its 108 authored judgments, current reviews record **52 pass, 2 fail and
54 unknown**. These are scoped criterion dispositions, not a truth percentage,
a scientific-quality lift, or independent experimental replications. Reviewers read
primary methods/results and limitations, not only the engine's own explanation.
They were separate from the answer authors but shared project context; blind review
and independent model lineage are not attested. Evaluation also received a second
source inspection after the coordinator's initial review.

## What the review changed

Memory repetition 2 described ACE as showing consistent gains across its tested task
suite. The saved Table 2 includes a loss on online FiNER without ground-truth labels,
and the accompanying discussion warns about unreliable feedback. This is one defect
with two affected criteria: citation correctness and scope. The main conclusion
against universal context-length gains remains supported. An authored correction
supersedes only the affected assessment in `morning-r2-memory` v3. The frozen v2
answer and its two failed judgments remain. This correction is not a replacement
repetition or a new measured outcome.

Retrieval repetition 3 says a file hit is not evidence of span localization. One
reviewer read that as an overly categorical claim; a second inspected the complete
answer and source and retained a contextual citation pass, because the rationale
and challenge explicitly preserve file-hit usefulness. Both reviews remain in the
case's evaluation history. The clearer wording is “does not by itself establish.”
This disputed wording is not counted as another confirmed scientific defect.

## What remains unknown

Each answer still has three unknown criteria: original-source recovery completeness,
strongest contrary-evidence coverage and experiment specificity. The retained primary
papers can be named, but the frozen rubric has no relevant-source universe or recall
denominator. It also lacks an operational adequacy threshold for experiment proposals.
We did not invent thresholds after seeing outputs. Directional experiment ideas are
not frozen runnable protocols, and one selected paper cannot establish literature
coverage. Repeated use of the same source is not independent replication.

These reviews used saved snapshots with zero fresh searches or fetches. They do not
fill the fresh-web acceptance repetitions or matched-baseline scientific comparison.
The next evaluation must define source-recovery and protocol-adequacy criteria before
running new answers, while preserving this campaign and its limitations.

[Machine summary](scientific-review.json) records each slot and current disposition.
Exact review payloads, source ranges/hashes, CLI receipts, disagreement and correction
receipts remain in the local evaluation folder, outside Git. The review history is
available through `research evaluation-show` with that campaign's local database.
