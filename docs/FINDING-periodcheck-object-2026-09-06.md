# FINDING — PeriodCheck measured at its objects · 2026-09-06

**Objects opened (not taglines):**

1. `git clone https://github.com/ahsan3274/periodcheck` → HEAD tree  
2. `live-evaluation.json` in that tree  
3. Hosted `https://periodcheck-697827662390.us-central1.run.app/` (HTTP 200 upload UI)

**Nearer proxies not used as the answer:** hack.md field table memory; prior “11–14k LOC” line without re-count.

---

## What their objects say tonight

| Measure | Command / object | Result |
|---------|------------------|--------|
| Python LOC | `find . -name '*.py' \| xargs wc -l` in their clone | **2576** |
| Test files | `tests/unit/*.py` | **7** |
| Live eval summary | `live-evaluation.json` → `summary` | **13/13** gold correct · `end_to_end_accuracy: 1.0` · `research_failures: 0` |
| Hosted stranger UI | `curl` homepage | **HTTP 200** upload page (“Historical accuracy, grounded”) |

Our tree tonight (same `find` pattern, excluding `.venv`): **27701** Python LOC. Refusal shipping arm: **6/6** on n=6 holdout (`eval_refusal_baseline.py`) — not the same task as their 13-claim period fixture.

---

## Embarrassing contrast for Sep 9

- Their **logged-out hosted URL serves the product UI**. Ours (`agent-science-568004190078…`) serves `mode=private-workspaces` and 303→login for `/search`, `/visibility/ui`, `/truths/ui` (`probe_hosted_stranger_path.py` RED).
- Their public README leads with a **live eval file in-repo** (13/13). We have offline eval gates and a sealed compound prediction from when the desk was public — the stranger cannot replay hosted compound without a workspace token.
- LOC is not the story: they are ~**10× smaller** on Python lines at HEAD and still show a first-run hosted path. More code here is not an advantage on the Cinema rubric.

## What this does *not* settle

- Why we lost Qwen remains unknown (see hack.md PRIOR LOSS). This is a Sep 9 field measurement, not a new Qwen diagnosis.
- Their 13/13 is on a controlled 1985 fixture with Document AI + Parallel; our refuse pole and compound economics are different primitives. Do not pretend one number beats the other without a shared task.

## Oscar action

Film / paste a path a logged-out judge can complete (CLI cold-clone or restore public exhibit). PeriodCheck already has the logged-out try-it bar.
