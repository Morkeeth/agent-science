# Independent review, 2026-09-05

Cursor and Fable independently reviewed pinned candidate `61e791d36a0b8f75cbd9bbcf0d3ee0cefafc1cf4`. They used temporary case stores and actual CLI/stdio MCP calls. Neither performed live research. Full reports remain outside Git; hashes are in `independent-reviews.json`. Their findings apply to that exact candidate. Later changes below were checked separately; the original review pin was never moved.

Cursor ran 67 new-workflow tests and 82 regression tests with eight storage subtests. Fable ran 188 tests and 27 subtests across 13 pytest-style files. These overlap the coordinator tests and must not be added as independent coverage counts. Fable also executed a real temporary Git comparison (baseline 0/1, candidate 1/1), killed a subprocess mid-operation, and exercised a shared capacity of two under six concurrent processes: exactly two provider stubs ran. These are controlled effects, not paid provider measurements.

## Findings and disposition

- Budget/diminishing stop prevented a final local conclusion: allow an explicit host finish while retaining the investigation stop reason and external-call ceiling.
- Cancellation overwrote completed/unknown states: preserve terminal outcomes; uncertain operation history stays visible.
- Invalid model output appeared to run forever: persist rejected known output; received invalid JSON is distinct from a transport outcome that was not observed.
- Missing recovery action and duplicate response spending: explicit reconcile preserves reservations and requires a fresh host proposal; a completed saved model response is reused after restart.
- Offline source reasons hidden from reasoning: include source failure reason and distinguish absent cache from attempted live access.
- Early start side effects on invalid input: validate the question/retrieval before creating case/policy records.
- Caller-minted MCP limits could authorize live calls: require a matching immutable approval recorded by the explicit local CLI. MCP cannot approve its own policy.
- Repeated searches with changed explanation bypassed stopping: compare operation identity, excluding explanation prose.
- General prior research excluded by repository start: include general and matching-repository research, scanning beyond unrelated result pages.
- Missing shared-validator caller, source database hints and CLI parent-option handling: production uses the shared validator; source references retain the local store; adapter requests strip store-routing paths; both shorthand flag orders work.
- Contradictory numerical findings bypassed number control: fresh non-unresolved numerical statements need anchored numbers; an existing current numerical target requires explicit claim_id. Numbers written as words and semantic entailment remain outside this narrow control.
- Qualitative causal support bypassed an omitted study-design field: detect explicit qualitative/interview language in the checked quote too. Contrary/context treatment of a causal target remains permitted. The guard does not infer every study design from full prose.
- Different-scope/context and data-only answers hid gaps: expose unresolved relationships, applicability and unassessed evidence.
- DOI closing punctuation split a study: trim surplus closing parentheses while preserving balanced DOI suffixes.
- Offline source work moved the check clock: research interpretation/offline reads retain the prior timestamp; only an observed live document read advances it.
- Decision views disagreed after changed reasoning: common semantic review logic now serves case and research views. A real agent rechecked the exact affected decision in current and historical views.
- Full-source inspection unavailable to configured reasoner: local paging preserves selected offset, source version/hash and truncation, including sources beyond the first context page.

## Scope findings retained

Permanent per-case lock files remain intentionally: deleting a flock path can let two processes lock different files for the same case. Readable evidence, original-source quality, causal support and tool-authority resistance are separate concerns; rejecting a shell action is not a measured prompt-injection defence against a live model.

Retraction/supersession controls use available metadata. No online retraction registry was connected. DOI/arXiv grouping uses explicit identifiers; prose-only reports can remain separate uncertain documents. A reasoner/host authors the question decomposition, category, follow-up choices and practical recommendation. It can be wrong despite exact quotes. Unknown billing, fresh-web field investigations, live model behavior and matched-budget research-quality improvement remain named gaps.

The reviewers correctly found missing final integration/docs/install receipts on their earlier pin. The later integrated receipt records the actual installed commit, test results, repeated saved-source investigations, changed-decision report and fixed-protocol repository comparison. A local release candidate is not a public launch.
