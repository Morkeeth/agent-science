# How CLI dev-tools actually get their first users (2026) — launch-mechanics fact

*Captured 2026-08-25 for the Helicon OUTWARD lane (make it runnable by a stranger in one
line + draft the launch). This grounds one decision: why the console entry point +
`uvx`/`pipx run` one-liner is the launch, not a nice-to-have. Reasoned from known 2026
distribution mechanics; the one hard external number is flagged.*

## The one that matters: install friction is the launch, not the README

For a developer CLI, the top-of-funnel conversion is not the pitch — it is the number of
steps between "I read the tweet" and "I saw output on my repo." Every step (clone, cd,
create a venv, install, configure a key) halves the pool. The tools that win the
context-linter category ship a **zero-install one-liner** as the headline command:

- `npx <tool>` for the JS-native ones (ctxlint's headline is `npx ctxlint`).
- `uvx <tool>` / `pipx run <tool>` for Python ones — the direct equivalent: fetch, run in
  an ephemeral isolated env, no global install, no clone.

Consequence for Helicon: `git clone && pip install -e .` is a launch blocker, not a
distribution channel. The console-scripts entry point (`helicon-review =
"helicon.review:main"`) is what makes `uvx --from mountain-of-helicon helicon-review
<repo>` possible, and that command IS the product's front door for a stranger. Building the
wheel and reserving the PyPI name is the gate; nothing downstream (Show HN, awesome-lists)
converts without it, because each of those funnels lands on the one-liner.

## The three first-user channels for an agent-tooling CLI, in order of yield

1. **Where the pain is already felt: CI + the agent's own session.** For context-file
   tooling specifically, the durable channel is not a launch post — it is the GitHub Action
   that turns a PR red when the docs drift, and the MCP/hook that warns the agent in-session.
   Launch posts spike; the CI gate is the weekly habit that retains. Ship both entry points:
   the one-liner for the first look, the Action for the second week.

2. **Show HN + the "awesome-*" lists.** Show HN is the highest-signal cold channel for a
   dev CLI because the audience is exactly the buyer (engineers who own tooling), and the
   ranking rewards a concrete, honest "it does X that nothing else does" over polish. The
   `awesome-claude-code` / `awesome-claude-skills` lists are low-effort, durable backlinks
   that keep delivering long after the post falls off the front page. Both require the
   one-liner to already work.

3. **The tool's own output as the ad.** A CLI whose output is screenshot-worthy (ranked,
   colored, graded, with file:line evidence) spreads because users paste the terminal, not
   a marketing image. This is why the first-screenshot command must hit a repo with a real
   CONTRADICTED finding, not a clean pass — the defect frame is the shareable one.

## The wedge rule for the post itself

A launch into a category with a shipping incumbent (here: ctxlint, agents-lint on the
existence tier) must lead with the ONE thing the incumbent does not do, stated as a
capability, not an adjective. For Helicon that is execute-and-compare: it runs the
documented command and grades the "this passes" claim. Leading with the commoditized tier
("we also check dead paths") ranks the launch as a slower clone of the incumbent.

## Flagged for verification

- The claim that Show HN is the *highest-yield* cold channel for a dev CLI is a widely-held
  practitioner belief, not a number I can cite to a source here. Treat as a prior, not data.
- ctxlint's `npx`-first shape and existence-tier scope: cited in PRD-2026-08.md §4 from a
  read of its repo on 2026-08-24. Re-verify at the object before quoting it in public copy.
