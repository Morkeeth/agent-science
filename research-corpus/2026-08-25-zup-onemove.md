# One-move / next-best-action UI for agent supervision (2026) — design fact

*Captured 2026-08-25 for the ZUP SUBSTANCE lane (render `recommend()` as the one-move card
on Pulse). Grounds one decision: whether the card's OUTWARD move is a "run" button or a
handed-over command. The external claim is attributed; the ZUP-specific conclusion is
reasoned from it.*

## The one that matters: 2026's HITL standard gates outward acts, and ZUP goes one step further

By 2026 human-in-the-loop is described as "the definitive architectural standard," and the
supervision space has settled into three named oversight models — **human-ON-the-loop**
(agent acts, human watches a live feed and is flagged on a confidence/sentiment drop),
**human-IN-the-loop / gated** (agent pauses at defined checkpoints and waits for a human to
approve or authorize before it executes), and **human-OUT-of-the-loop** (full autonomy).
The tooling reflects this: platforms like Dify ship a "Human Input Node" that pauses a
workflow at a critical decision point and presents Approve / Reject / Escalate buttons.
[Pickaxe 2026 guide; Teneo NBA 2026]

The relevant nuance for a next-best-action surface: the value is not the feed of everything
the agent did — that is the crowded "dashboard" lane — it is the SINGLE recommended action
with the checkpoint attached. NBA software is defined as recommending "the most appropriate
action to take next," one move, not a ranked menu.

**Consequence for ZUP.** The one-move card sits in the gated model, but ZUP deliberately
does NOT ship the industry-standard Approve button for an outward act (push / deploy /
publish / spend). The gated pattern still lets the human authorize the agent to fire the
act; ZUP's boundary (PRD-2026-08-20) is stricter — for an outward move it renders the exact
command as copyable text and hands it over, with no affordance that runs it. So the card's
`handover` field is present only when the move is outward, and the surface's only action on
it is copy-to-clipboard. This is defensibly ahead of the 2026 default, not behind it: where
the standard gates the firing, ZUP refuses to be the thing that fires. The falsifiable
"DONE WHEN" line on each card is the same discipline one layer up — a next-best-action UI
that cannot state how you'd check the action worked is a feed, not a cockpit.

Sources: [Pickaxe — Human-in-the-Loop AI Agents: The 2026 Guide](https://pickaxe.co/post/human-in-the-loop-ai-agents) ·
[Teneo — Next Best Action Software: The AI-First Guide for 2026](https://www.teneo.ai/blog/next-best-action-software)
