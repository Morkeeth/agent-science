# Use-bar session template — Oscar fills after one real search

**Rule:** do not claim “Oscar uses Agent Science before every websearch” until this
template is filled and a matching local/CLI/MCP receipt exists. An empty template
is the honest state.

**Bar:** factual ask → Agent Science (lookup or visibility) → only then raw web if still open.  
**Skill:** `.cursor/skills/agent-science-websearch/SKILL.md`  
**Default:** `live=false`. Live spend needs an explicit decision (and for research engine: approved policy).

---

## Session header (fill once)

| Field | Value |
|-------|-------|
| Date (UTC) | |
| Operator | Oscar |
| Tool path used | ☐ Cursor MCP `science_lookup` / `science_visibility` · ☐ CLI `python3 -m clearance lookup` · ☐ CLI `visibility --full` · ☐ other: ________ |
| Hosted browser used? | ☐ no · ☐ yes (note: hosted may require workspace sign-in) |
| Receipt id / log line | |

---

## One real search (minimum to prove the habit)

Paste the **actual** query you asked (your words):

```
QUERY:
```

Command run (copy/paste exactly):

```bash
# pick one — examples only; replace QUERY
python3 -m clearance lookup "QUERY"
# or:
python3 -m clearance visibility "QUERY" --full
```

| Result field | Paste from output |
|--------------|-------------------|
| Label / verdict | |
| Cost tier (`free` / `cheap` / `live`) | |
| Citation URL (if SOURCED) | |
| Verbatim span (if SOURCED) — **do not paraphrase** | |
| Refusal cause (if not sourced) | |
| Parallel calls | |
| Did you open raw web afterward? | ☐ no · ☐ yes — why still open: |

---

## Integrity checklist (tick only what you did)

- [ ] Ran Agent Science **before** any raw browser/WebSearch for this ask
- [ ] If SOURCED: cited the verbatim span or URL — did not rewrite the quote
- [ ] If refused / NOT_CLEARED: said so; did not invent a citation
- [ ] Did **not** set `live=true` unless the miss mattered and keys/policy allowed it
- [ ] Did **not** treat a title, star count, or gallery tagline as the object

---

## Optional: second ask (compound / free tier)

Same distinctive fact, later in the day:

```
QUERY 2:
```

| Field | Value |
|-------|-------|
| Label | |
| Tier | |
| Reuse / corpus / registry hit noted? | ☐ yes · ☐ no · ☐ n/a |

---

## Stop — Oscar doors (not part of use-bar)

These do not belong in a use-bar session and are never agent acts:

1. Key rotation in console  
2. YouTube / Vimeo upload  
3. Devpost submit  
4. Approving unbounded live research spend  

---

## Empty-state honesty

As of cinema pack write (2026-09-05): **this template is blank by design.**  
A filled row above is the only evidence that counts.
