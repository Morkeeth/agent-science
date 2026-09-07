# First live investigation and challenge — 2026-09-05

## Question and bounded conclusion

When do repository context files help coding agents, and when do they hurt?

Keep necessary project instructions. Test whether added context supplies useful information and improves accepted outcomes before standardizing it. Measure correctness and efficiency separately; neither a universal cost penalty nor a universal benefit is established.

The [Python benchmark study](https://arxiv.org/html/2602.11988v1) reports that generated context did not reliably improve test-pass success and increased inference cost in its evaluated settings. Its documentation-removal ablation favored generated context. This is a condition within one study, not independent replication. Python-heavy tasks, single sampled completions, generated task/test construction, and excluded agent settings in the ablation limit transfer.

The challenge retrieved a [separate paired efficiency study](https://arxiv.org/html/2601.20404v2) reporting lower runtime and output-token use with AGENTS.md on selected small PR tasks using one Codex configuration. Its methods explicitly leave comprehensive correctness evaluation outside scope. A manual non-degenerate-output check cannot establish equivalent accepted correctness. Different populations, context interventions and outcomes prevent treating the studies as a direct contradiction.

Practical consequence is an authored inference: retain necessary instructions and compare correctness, failures, wall time and actual resource use before selecting a file policy. Faster output alone is insufficient. An independent, repeated trial showing equally correct accepted fixes with lower total resource use would change the local recommendation.

## Actual persisted flow

Code pin: 05609dffe1ac9f268d63e72e61ce75f0cd4d77bd. Case c5d4051a667f, prior version 6. Initial live run 97952b698bfe4003 completed at version 9. Challenge b77ed463d0e14f4c pinned version 9 and completed at version 11. A subsequent zero-call review run b8759eff477a46e0 incorporated independent source-review caveats at version 12.

1. Retrieve prior work using the user's repository-context vocabulary.
2. First live search returned an off-scope social-science reproduction paper. It was not used as repository-context effectiveness evidence.
3. Inspect original benchmark methods/results. Its documentation-removal finding drove the next query; this was not a preselected fixed query list. That query returned secondary coverage of the same study, not independent replication.
4. Save a conditional conclusion, decision and followed version.
5. Launch a separate challenge looking for favorable efficiency evidence. Read the original paired study's methods, results and correctness limitation. HTML and abstract references were grouped as one study.
6. Supersede the deployment interpretation, add the different-scope relationship, and inspect compare/updates. The saved diff contains four reasoning changes, two affected claim IDs and one affected decision. Decision 76ee83173b2b was subsequently replaced by 29522e111b89, retaining its history. After source review, decision 34ca2c0ec6aa replaced that intermediate decision at version 12, preserving both earlier versions.

## Limits and receipts

The user's instruction to proceed authorized the previously prepared one-question policy. Local CLI approval was recorded before live calls. Aggregate morning-one-question-20260905 reserved 3 discovery calls, 6 document reads and all 3 rounds from its ceilings of 8/20/3; configured-model calls stayed at zero. Actual observed work: 3 completed Parallel calls and 4 source-body fetches. Host reasoning and separately issued local source-page reads are outside these engine counts. Billing remains unknown. No paid retry was made after an unknown outcome. A real continuation attempt against the exhausted shared policy stopped with zero reserved steps and zero provider calls, exercising the aggregate budget control.

The stop reason names exhausted shared investigation rounds and the remaining evidence gaps. This is one bounded live question and challenge, not the six-topic field pass or a matched scientific benchmark. Prior source snapshots were reused; only newly fetched documents received fresh body checks. The original Python study was inspected from its saved version and was not re-fetched in this run.

Source text, full request/response transcripts and the aggregate receipt remain outside Git in the local evaluation store. The empty-quotation guard fired on an invalid initial proposal before any synthesis revision; the corrected proposal used exact source spans. Provider rankings were imperfect: the first result was off scope and the second was derivative. These are recorded retrieval errors, not evidence of absence.

## Independent source review

A separate agent read original methods/results/limitations before assessing the version-11 conclusion. It found no unsupported central conclusion and verified nine active quotation/condition anchors against saved snapshots. Its omitted-caveat findings were incorporated at version 12: PR-informed task/test construction, selected small PRs, a higher reported median total-token count despite lower runtime/output tokens, and the absence of a longitudinal test of mistake retention. Source occurrence is not a numerical scientific-quality score. Full review and inspected character ranges remain in the private run receipts.

## Local experiment plan

Protocol 6bcf588dafaa version 3 is a frozen plan, with no executions. Its READY status means the definition is complete, not that an agent trial ran. Earlier draft versions remain readable. It fixes three real maintenance tasks at commit 3dd6e3bf8401564a4f09b401595cd60cf4de6233: offline-to-live metadata recovery, rejecting empty synthesis outcomes, and preventing no-op baseline repetitions. Proposed denominator: three tasks × two context conditions × three fresh repetitions = 18 attempted fixes, including failures and timeouts. These selected maintenance tasks cannot establish general coding effectiveness.

The existing full repository instruction file is the control. The candidate is a concise file of build/test/storage guidance with no task-specific answers. Its content and length both differ, so the trial cannot isolate the effect of shortening alone. Baseline file SHA256 ca746e3306cc7895a996ff7ef22744e2e2f002440dcf97db1c3be10ec7ba775b; candidate file SHA256 7318bdf1d5f601c7300ada0c89f518fbfab2100eb7e53332c11d1f6ed3bcb48a.

A separate acceptance author derived behavioral checks from the external review contracts without reading candidate fixes or tests. The frozen script SHA256 is 4ff4a68990a4b844f42948f5aca25c5621bb4520790626e6048f1a8942cdae0f. All three task scripts actually failed on 3dd6e3b and passed on 05609df; individual control counts were metadata 2/4 versus 4/4, synthesis 4/5 versus 5/5, and repetition 4/5 versus 5/5. These are acceptance-control calibrations, not context-file experiment outcomes. Synthetic acquisition/registry transport was substituted; behavioral rules were not. Exact raw results remain outside Git.

Next, implement the isolated host runner and configure its aggregate execution policy. The code-change runner cannot execute this agent_context_trial kind. No context effectiveness result is claimed.

## Remaining work

Five other topic investigations, matched baseline/fresh-web evaluation, and a substantive executed context trial remain distinct tasks. A new resource policy is needed before further discovery; the existing shared round allowance is exhausted. No public push or deployment was performed.
