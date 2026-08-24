# Night run 2026-08-24/25 — the SUBAGENTS-in-one-terminal arm of the fleet-vs-subagents A/B

This is one arm of Oscar's experiment: does a single coordinator terminal spawning
background subagents ship as much, per token, as a multi-terminal fleet? This file records
ONLY the arm that ran tonight (background agents, one terminal). The fleet arm's numbers
live in prior `~/CODE/fleet-ops/runs/SNAPSHOT-*.md`; the A/B verdict is completed in the
morning wrap-up email, not here — this is the measured input to it, not the conclusion.

Grounded at the object 2026-08-25: every "shipped" line below is a real commit sha, and
`git log @{u}..` reported **0 unpushed** in all four repos, so shipped == pushed.

## Arm: background subagents, one coordinator terminal

[CLAIM] Five substance/outward lanes shipped and pushed in one night from one terminal, spawning background subagents per lane.
[REPO] ~/CODE/cleared ~/CODE/zup ~/CODE/mountain-of-helicon ~/CODE/hack-fleet-ata

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

*A/B verdict (this arm vs the fleet arm, per-token and per-stranger) is computed in the
2026-08-25 morning wrap-up email from these numbers + the latest fleet SNAPSHOT.*
