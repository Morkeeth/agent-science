# FOR CURSOR — review lane

**Git is the mailbox. One writer on product code at a time. Never `git add -A`.**
Log to `CURSOR-LOG.md`, append-only. That file is the only cross-channel between us.

## Ownership this run

| Mine (Claude Code) — do not edit | Yours |
|---|---|
| `clearance/*.py` | `CURSOR-LOG.md` |
| `tests/test_watch_it_go_red.py` | new files under `review/` |
| `check_pitch.py`, `run_clearance.py`, `compare_questions.py`, `clear_production.py` | |
| `PITCH.md`, `BUILD-PLAN.md`, `CLOSE.md`, `docs/*` | |

If you need a change in a file that is mine, write it in `CURSOR-LOG.md` as a diff or a
description and I will apply it. Do not edit product code while I am building.

## The one rule the product is built on

**A locator may only LOCATE evidence. It may never ASSERT it.**
`Verdict.__post_init__` cannot construct GREEN or RED without a citation and verbatim
quoted terms. `clearance/verify.py` refuses any proposed passage that is not verbatim in
the fetched document. If you find a path that reaches a verdict without passing that
guard, that is the highest-value finding available and it outranks everything else here.

## Your three jobs

**1. Attack the verifier with proposers I did not think of.**
`clearance/verify.py` is structural and provider-independent. Five adversarial locators
are already refused (`tests/`): a hallucinated passage, a real passage from the WRONG
document, an in-document passage missing the claim's terms, the whole page, a mid-word
slice. Write proposers I missed. Candidates I have NOT covered: a passage assembled from
two non-adjacent fragments that happen to concatenate; a passage differing by one
character of whitespace or a unicode look-alike; a passage that is verbatim but is the
document's own quotation of somebody else's claim; a negated sentence that contains the
required terms.

**2. Audit every control for the live-object binding class.**
Swept once today and found three. A control that carries its own copy of what it grades
is a claim about the past wearing a test's clothes. Check: does each control import the
shipping constant, or restate it? Does it use the product's own loader, or recompute a
path? `tests/` should contain no literal that mirrors a value in `clearance/`.

**3. Read `PITCH.md` cold and mark every claim whose evidence you cannot find in the repo.**
You are the stranger. If a number has no artifact behind it, or a denominator is missing,
say so. Two known-open items to check rather than trust: the competitor names (Troveo,
Veritone, Vermillio) came from another tree marked "re-verify before quoting", and I did
not verify them; and `docs/FINDING-substring-is-not-a-statement.md` records a FALSE GREEN
that `StringLocator` still produces on purpose.

## Facts you need

- Keys live at `~/.config/keys/{gemini,parallel}.key`, 0600, read at runtime. **Never copy
  a key into this repo, a `.env`, a doc, a commit message or a log line.**
- Gemini free tier rate-limits at roughly four consecutive calls — expect HTTP 429. A
  transport error must PROPAGATE, never render as UNKNOWN. There is a control for this.
- `python3 tests/test_watch_it_go_red.py` — currently **37 passed, 0 failed**. Offline
  except where noted.
- Nothing is pushed and nothing is public. That is Oscar's click, not ours.
