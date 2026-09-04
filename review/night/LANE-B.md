# Lane B — evidence and conditional conclusions

Worktree: `agent-science-night-b`
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

## Replay acceptance follow-up — visible unresolved scope

Context-only conclusions now expose an `unresolved relationship` gap. Different-scope assessments expose an `unresolved scope` gap with explicit wording that scope mismatch is not evidence of no effect. Sources with no active interpretation expose `unassessed evidence`. Actual authored support plus context retains `SUPPORTED_AS_ASSESSED`; a separate different-scope source still names its applicability gap without changing the supported claim into a no-effect conclusion.

```text
python3 -m pytest -q tests/test_studies_synthesis.py tests/test_research_expansion.py
43 passed in 0.96s
```

The five added artificial-fixture cases exercise context-only, different-scope-only, source-data-only, support+context and support+different-scope answers. No provider calls or private case data.

## Final independent-review fixes — decision consistency and numerical targets

`cases.decision_review` now compares active assessment semantics associated with each decision's cited evidence IDs, including condition anchors and their source state. Material rationale, scope, conditions and challenge changes require review. Superseded assessment history, timestamps, generated assessment IDs and evidence-version counters alone do not. `synthesis.compare` uses this same decision state instead of a second broader rule. Historical versions and decisions citing unrelated evidence retain their state. This pure snapshot comparison does not load cases recursively.

Numerical statement contract: every new non-unresolved finding, including contradiction/context/different-scope findings, must anchor its numerical statement tokens in the quoted source. A non-support assessment can instead name an explicit `claim_id` with exactly the existing statement; missing numeric target tokens must occur in a current active target assessment's checked source quote. Unassessed imported claims, stale hashes, unavailable/retracted/superseded sources, and stale target conditions cannot supply that exception. Thus an existing anchored target of 37% may be contradicted by a source reporting 20; a newly invented 37% result against that source is rejected. Contradiction remains an authored relationship, not mechanically proven entailment. The conservative token check still includes date numbers in statements; rationale and proposed falsification conditions remain authored interpretation, not extracted results.

```text
python3 -m pytest -q tests/test_studies_synthesis.py tests/test_case_storage.py tests/test_research_expansion.py tests/test_terminal_case_workflow.py tests/test_evidence_cases.py
90 passed, 8 subtests passed in 6.23s
```

Controls exercised: fabricated numeric contradiction rejected; legitimate anchored numeric target accepted; unavailable, retracted, superseded and stale target sources rejected; unassessed imported target rejected; interpretation replacement flags the matching saved decision through both case and comparison views; unrelated and historical decisions retain state; semantically identical replacement and authored-clock changes do not flag; condition changes flag their cited decision. All source text and databases in these tests are artificial/private fixtures. No live or paid calls.
