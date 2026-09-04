# Cold clone run · 2026-09-02

**Machine:** macOS · **Clone target:** `/tmp/agent-science-cold`  
**Remote:** `https://github.com/Morkeeth/agent-science.git`  
**Rule:** no local repo state — fresh `git clone` only.

---

## Run 1 · README before fix (`af517ee`)

**Commands (README quick start only):**

```bash
rm -rf /tmp/agent-science-cold
git clone https://github.com/Morkeeth/agent-science.git /tmp/agent-science-cold
cd /tmp/agent-science-cold
bash scripts/verify_cold_clone.sh
bash scripts/demo_truth_layer.sh
```

### Transcript

```
$ git clone https://github.com/Morkeeth/agent-science.git /tmp/agent-science-cold
Cloning into '/tmp/agent-science-cold'...

$ bash scripts/verify_cold_clone.sh
=== Agent Science cold-clone verify ===
repo: /tmp/agent-science-cold
...
=== cold-clone verify OK ===

$ bash scripts/demo_truth_layer.sh
=== Agent Science · truth layer demo ===
...
primary: CONTRARY_TO_RESEARCH
transparency: ['angles_searched', 'shallow_route', 'imbalance']
=== done ===
```

**Exit code:** 0 · **Wall-clock:** ~18s (verify) + ~7s (demo) [CORRECTED 2026-09-04: verify measures 203s, not ~18s. This run was a real clone on a WARM machine, so ambient site-packages and local API keys were still in play. Re-measured on 2026-09-04 in a scrubbed environment with an empty HOME and a bare virtualenv where google-adk and parallel-web are both absent.]

### Where a stranger got stuck

A **documentary producer or E&O underwriter** (the $75K buyer) is not served by the quick start alone:

1. Quick start demos the **agentic truth layer** (`ralph loop agentic`), not script clearance.
2. README § Clearance desk points to `python3 agent_science.py fixtures/scripts/documentary-orphan-works.txt` — that path requires **local API keys** (`~/.config/keys/gemini.key`, `parallel.key`) not mentioned in quick start.
3. First attempt at local clearance on a pristine clone (before `cache/corpus.db` exists) hit:

```
sqlite3.OperationalError: attempt to write a readonly database
```

   at `corpus.remember()` during `agent_science.py` (intermittent on first write; second run on same clone succeeded after `corpus.db` was created).

**First stuck point for the buyer:** no keyless path from README to paste-script → verdict.

### Fix (`068265c`)

- Added `scripts/demo_clearance_desk.sh` — `POST /clear` on hosted URL, no local keys.
- README quick start line 3: `bash scripts/demo_clearance_desk.sh`
- `SUBMISSION.md` stranger path updated to match.

---

## Run 2 · README after fix (`068265c`)

**Commands (README quick start, all three lines):**

```bash
rm -rf /tmp/agent-science-cold
git clone https://github.com/Morkeeth/agent-science.git /tmp/agent-science-cold
cd /tmp/agent-science-cold
bash scripts/verify_cold_clone.sh
bash scripts/demo_truth_layer.sh
bash scripts/demo_clearance_desk.sh docs/cold-scripts/google-books-settlement.txt cold-clone-2026-09-02
```

### Transcript

```
$ git clone https://github.com/Morkeeth/agent-science.git /tmp/agent-science-cold
Cloning into '/tmp/agent-science-cold'...

$ bash scripts/verify_cold_clone.sh
=== Agent Science cold-clone verify ===
repo: /tmp/agent-science-cold
1. Seed offline document cache...
...
=== cold-clone verify OK ===

$ bash scripts/demo_truth_layer.sh
=== Agent Science · truth layer demo ===
...
primary: CONTRARY_TO_RESEARCH
transparency: ['angles_searched', 'shallow_route', 'imbalance']
=== done ===

$ bash scripts/demo_clearance_desk.sh docs/cold-scripts/google-books-settlement.txt cold-clone-2026-09-02
=== Agent Science · clearance desk (hosted) ===
script:  docs/cold-scripts/google-books-settlement.txt
subject: cold-clone-2026-09-02
url:     https://agent-science-568004190078.us-central1.run.app/clear

claims: 4 | sourced: 0 | unsourced: 4
parallel_api_calls: 1 | engine: adk

C1 · UNVERIFIED INDEPENDENCE · no_independent_source
  The Google Books settlement was rejected by a federal judge in 2011.
  why: documents state this, and every one traces to a derived or unclassified origin — a human must judge whether that is independent support

C2 · UNVERIFIED INDEPENDENCE · no_independent_source
  Google proposed a deal with authors and publishers to digitize millions of books.
  why: documents state this, and every one traces to a derived or unclassified origin — a human must judge whether that is independent support

C3 · UNSOURCED · search_found_no_admissible_source
  A federal judge ruled that the Google Books settlement would give Google too much power over orphan works.
  why: we searched and no document we read states it

C4 · UNSOURCED · search_found_no_admissible_source
  Authors argued that the Google Books settlement went too far in granting Google exclusive rights.
  why: we searched and no document we read states it

wall-clock: 30s
desk UI:    https://agent-science-568004190078.us-central1.run.app/
=== done ===
```

**Exit code:** 0 · **Wall-clock:** ~50s total (verify + truth layer + clearance desk) [CORRECTED 2026-09-04: 4m00s measured on a scrubbed environment, with step 1 at 203s, step 2 at 12s and step 3 at 25s.]

---

## Privacy grep (same day)

```bash
$ bash scripts/privacy_grep.sh
PRIVACY OK: 0 hits
```

---

## Done-when

| Gate | Status |
|------|--------|
| Cold transcript exists | ✅ this file |
| Single hard trace | ✅ `docs/TRACE-2026-09-02-google-books.md` |
| Privacy grep zero | ✅ 0 hits |
