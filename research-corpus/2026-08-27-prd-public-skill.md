# Public-skill PRD — sourced claims (2026-08-27)

Written in the corpus `[CLAIM]` / `[URL]` shape so Agent Science can clear its own
distribution PRD. Repo-internal facts carry `[REPO: ...]`.

## Cursor skills and plugins (web)

- [CLAIM] Cursor Agent Skills are packages with a SKILL.md file whose YAML frontmatter requires a name and a description, and the description is what the agent uses to decide when the skill is relevant. [URL: https://cursor.com/docs/skills]
- [CLAIM] Cursor loads project skills from .cursor/skills/ and .agents/skills/, and user-level skills from ~/.cursor/skills/ and ~/.agents/skills/. [URL: https://cursor.com/docs/skills]
- [CLAIM] Cursor plugins are submitted from a public Git repository via cursor.com/marketplace/publish. [URL: https://cursor.com/docs/reference/plugins]
- [CLAIM] A Cursor Plugin requires a .cursor-plugin/plugin.json manifest, and marketplace plugins must be open source so the community can inspect them. [URL: https://forum.cursor.com/t/how-do-i-upload-my-plugin-after-filling-out-the-form-there-are-no-buttons-am-i-doing-something-wrong/155138]
- [CLAIM] Cursor plugin review has also been directed to cursor.directory as a listing location. [URL: https://forum.cursor.com/t/pending-review-xpoz-plugin-submission-submitted-june-24/165776]
- [CLAIM] Agent Skills is an open standard for packaging domain-specific knowledge and workflows that agents can use. [URL: https://cursor.com/docs/skills]

## Repo-internal (clears against the local file)

- [CLAIM] This repository has no SKILL.md and no .cursor-plugin/plugin.json, so it is not packaged as a Cursor skill or plugin. [REPO: PRD-PUBLIC-SKILL.md]
- [CLAIM] ask_registry.py is a local-sqlite registry query: sourced answer or an honest miss, no model, no network. [REPO: ask_registry.py]
- [CLAIM] The hosted service accepts POST /clear with a script and subject, not a single-question /ask. [REPO: cloud/service.py]
- [CLAIM] VISION-2026-08.md states Agent Science is the source-of-truth companion for search and a registry of the most-searched verified things, with Article 53 as a vertical not the product. [REPO: VISION-2026-08.md]
- [CLAIM] PLAN-30.md still schedules making the GitHub repo public only at hackathon submit, not now. [REPO: PLAN-30.md]
