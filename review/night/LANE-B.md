# Lane B — evidence and conditional conclusions

Worktree: `/Users/morkeeth/CODE/agent-science-night-b`
Branch: `build/night-synthesis-20260905`
First slice: `a744ba9` (11 tests passed).

Implemented in `clearance/studies.py` and `clearance/synthesis.py`:
- DOI/arXiv identity normalization, arXiv versions, explicit mirror association. Prose citations and title resemblance do not merge studies. Different IDs do not prove replication.
- Exact source anchors for findings and extracted conditions, unknown missing conditions, unavailable/retracted/superseded-source rejection.
- Authored support, contradiction, different scope, context and unresolved relationships. Conditions retain source version/hash. No model-agreement or confidence score.
- Required challenge/falsification text, optional authored empirical/official/adoption category, separate redacted local experiment summaries.
- One locked case revision per proposal. Stale version and invalid later findings do not partially write. Interpretation does not advance source check time.
- Optional claim_id/supersedes to replace an assessment while preserving history. Existing research.brief remains compatible.
- Saved version comparison distinguishes source addition, availability recovery, content changes, metadata changes and interpretation changes. Reports material_change, affected_claim_ids, affected_decision_ids, and review-required decision objects.

Actual verification (private pytest fixture databases, artificial source text):

```text
python3 -m pytest -q tests/test_studies_synthesis.py tests/test_research_expansion.py tests/test_case_storage.py tests/test_research_search.py
76 passed, 8 subtests passed in 2.12s
```

Exercised failures: fabricated quote, unavailable snapshot with retained text, unsupported numeric assertion and numeric substring mismatch, absent challenge, nonverbatim condition, qualitative causal wording, stale version, concurrent same-version writers, stale condition from a second source, retraction, invalid second finding rollback. Exercised successful distinctions: five document mirrors form one study, title/citation candidates remain separate, different_scope is not contradiction, a contradictory assertion may name a different numeric value, contested claims expose competing assessments, replacement retains historical interpretation, interpretation changes flag cited decisions, experiment output redaction.

Remaining limits:
- No paid calls, fresh research, personal case access, push or deployment occurred.
- Exact quotes establish occurrence only. Semantic support and categories are authored. Numeric and qualitative guards are narrow conservative controls, not an entailment engine; paraphrased causal claims need human/model review.
- Conditions are verbatim extraction; normalized paraphrases are rejected. Missing conditions remain unknown.
- Mirror joining depends on explicit source DOI/arXiv metadata or identifier URLs. DOI citations in prose stay candidates; arbitrary articles repeating the same paper are not inferred as identities.
- Retraction/supersession controls use available metadata; no online metadata lookup is performed.
- Challenge/falsification text has structural validation, not proof that the proposed test is decisive.
- build exposes claim state and competing interpretations but does not automatically choose a winner or aggregate an effect estimate.
