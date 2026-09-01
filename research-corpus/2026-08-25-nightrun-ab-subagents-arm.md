# Night run 2026-08-24/25 — the SUBAGENTS-in-one-terminal arm of the fleet-vs-subagents A/B

This is one arm of Oscar's experiment: does a single coordinator terminal spawning
background subagents ship as much, per token, as a multi-terminal fleet? This file records
ONLY the arm that ran tonight (background agents, one terminal). The fleet arm's numbers
live in prior `fleet-ops (internal)/runs/SNAPSHOT-*.md`; the A/B verdict is completed in the
morning wrap-up email, not here — this is the measured input to it, not the conclusion.

Grounded at the object 2026-08-25: every "shipped" line below is a real commit sha, and
`git log @{u}..` reported **0 unpushed** in all four repos, so shipped == pushed.

## Arm: background subagents, one coordinator terminal

[CLAIM] Five substance/outward lanes shipped and pushed in one night from one terminal, spawning background subagents per lane.
[REPO] agent-science github.com/Morkeeth/zup github.com/Morkeeth/mountain-of-helicon github.com/Morkeeth/hack-fleet-ata

| lane | repo | done-when proof | commit(s) |
|---|---|---|---|
| MOONSHOT · execute-and-compare | mountain-of-helicon | CONTRADICTED prints with stderr on a false passing-test claim; version-vs-manifest slice | `8dc0e04` · `172b6b6` |
| OUTWARD #1 · Helicon reaches a stranger | mountain-of-helicon | `review .` front door fixed + one-line npx-shape entry + Show HN / awesome-list DRAFT in repo | `e8e22ee` |
| OUTWARD #2 · prompting-coach | hack-fleet-ata | ran on Oscar's own ~/.claude logs; names a landed prompt + a looped one, witness behind each | `7124f60` · `704823c` |
| SUBSTANCE · Agent Science log wired | cleared | 2nd production, different subject → 0 Parallel calls, 2 log hits (measured at net boundary); rename ledger→refusal_log (0 in code) | `ff35de7` · `e1f7fac` · `66c96c6` |
| SUBSTANCE · ZUP one-move card | zup | seeded board: at-risk repo AND clean-but-due repo each show the right single move; 508 tests green | `d854b4f` · `8e04572` |

[CLAIM] Two lanes carry clean per-agent cost measurements from the task runtime; the other three are attributed by commit but not by isolated token count.
- ZUP one-move card: 110,871 subagent output tokens · 46 tool uses · 708,591 ms (11.8 min).
- Agent Science log wiring: 149,447 subagent output tokens · 67 tool uses · 958,865 ms (16.0 min).
- The three earlier lanes (moonshot, coach, outward-Helicon) shipped as commits above; their
  isolated token counts were not captured in the coordinator's context this run — a gap in
  the measurement, noted honestly rather than estimated.

## The number that actually matters

[CLAIM] Outward reach this night = 0 strangers. Nothing reached a person who is not Oscar.
Every lane produced code, a proof, and a push to a PRIVATE remote. The one act that would
change the scoreboard — publishing Helicon so a stranger runs one line — is drafted and
waiting on Oscar's click, by design (outward acts are never auto-taken).

**So the honest read of this arm: high internal throughput (5 lanes, ~5 hrs, one terminal),
zero external delivery.** Throughput is not the scoreboard. A fleet arm that shipped 3 lanes
but got one in front of a stranger would win the A/B on the only axis that counts.

## What this arm shows about the method (for the A/B)

- **Parallelism held:** two independent lanes ran as concurrent background agents (ZUP +
  Agent Science) with no cross-talk and no merge conflict; a peer session's commit `bd9647a`
  landed in cleared/main mid-run and rebased linearly.
- **The coordinator kept conclusions, dropped tool spam:** each lane returned a ≤10-line
  verdict; the ~260k tokens the two measured agents spent stayed OUT of the coordinator's
  context. This is the claimed advantage of the subagent arm — cheap context for the driver.
- **Failure mode to watch:** no lane self-verified against a stranger. The subagent arm is
  as blind to outward reach as the fleet arm; neither method fixes the click gap.

## THE A/B VERDICT — subagents-in-one-terminal vs the fleet

The comparison arm is the fleet's OWN measured 3-day scoreboard, lifted from
`fleet-ops (internal)/runs/SNAPSHOT-2026-08-13.md` (its honest self-report, not my relay).

| axis | FLEET arm (3-day, measured) | SUBAGENTS arm (this session, ~10h) |
|---|---|---|
| output tokens | **19,027,962** (~6.3M/day) | ≥**476,437** measured across 4 named agents (partial — coordinator turns + pre-compaction agents uncounted) |
| commits | **389** (~130/day) | **59** (one evening+night, across 4 repos) |
| **strangers reached** | **1** (verified floor; a 2nd DM unverifiable) | **0** |
| coordination overhead | socket protocol, N terminals, broadcast-storm risk, peer-to-peer confusion | none — one process, parent holds the gate by construction |
| the fleet's own verdict | *"narrowly worth it on error-containment, NOT throughput. No control arm was run, so 'fleet beats solo' is unproven."* | — |

**What the A/B actually shows (three honest reads):**

1. **The bottleneck is not the build engine — it is the outward click.** Both arms shipped
   real code at volume; both reached ~0–1 strangers. The fleet spent 19M tokens over 3 days
   to reach ONE verified stranger; the subagent arm reached zero in a night. Neither method
   fixes the click gap because the click is Oscar's, by design. **No orchestration topology
   moves the only number that counts.** That is the finding, and it indicts both arms equally.

2. **On internal throughput per token, the subagent arm looks cheaper — but the measurement
   is not clean enough to declare a winner.** 59 commits at a measured floor of ~0.48M tokens
   is a far better commits-per-token ratio than 389 at 19M, but (a) my token count is partial,
   (b) commit counts are not outcome counts (a commit is not a shipped feature), and (c) this
   was NOT pre-registered with a matched board and wall-clock. It is a second data point, not
   the controlled experiment. The fleet study asked for exactly that control arm and never ran
   it; this night is a partial, imperfect version of it.

3. **The subagent arm's real, defensible advantage is structural, not numeric:** the parent
   keeps conclusions and sheds tool-spam (each lane returned ≤10 lines while ~0.48M tokens of
   tool churn stayed out of the coordinator's context), and there is no cross-peer protocol to
   go wrong (no broadcast storm, no peers-messaging-peers, the gate is the parent by
   construction). The fleet's failure modes this replaces are documented, not hypothetical.

**Bottom line for the morning:** if the goal is internal throughput and error-containment,
the single-terminal subagent arm delivers it at a fraction of the coordination cost and looks
cheaper per token — but "cheaper" is unproven without a pre-registered, matched control. If
the goal is OUTWARD (it is), **both arms score ~0 and the experiment's real result is that the
build method was never the constraint.** The next experiment worth running is not fleet-vs-
subagents; it is *anything that reaches a stranger* vs the current zero.

*To turn this into the clean experiment: pre-register one matched board, same wall-clock, same
five metrics, denominator written before the first token — the control arm the fleet study
named and never ran.*
