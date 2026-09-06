#!/usr/bin/env bash
# Full gate — run before Devpost submit or after any deploy.
# Usage: bash scripts/full_gate.sh [HOSTED_URL]
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
BASE="${1:-https://agent-science-568004190078.us-central1.run.app}"
STAMP="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

echo "=== FULL GATE === stamp=$STAMP"
echo

echo "--- 1. Secret surfaces ---"
python3 tests/test_secret_surfaces.py

echo "--- 2. Seed + mutation controls ---"
python3 scripts/seed_document_cache.py
python3 tests/test_watch_it_go_red.py

echo "--- 3. Partner + ADK ---"
python3 tests/test_partner_runtime.py
python3 tests/test_parallel_integration.py
python3 tests/test_adk_default_path.py

echo "--- 4. Product suites ---"
for f in tests/test_dictionary.py tests/test_registry_surface.py tests/test_routing.py \
         tests/test_popular.py tests/test_stack_product.py tests/test_refusal_correctness.py \
         tests/test_visibility_transparency.py tests/test_contrary_verdict.py \
         tests/test_stack_fit.py tests/test_community_notes.py; do
  python3 "$f"
done

echo "--- 4a. Terminal research and decision workflow ---"
python3 -m pytest -q tests/test_terminal_case_workflow.py tests/test_evidence_cases.py tests/test_research_expansion.py tests/test_research_search.py tests/test_research_contract.py tests/test_studies_synthesis.py tests/test_night_runs.py tests/test_research_workflow.py tests/test_overnight_integration.py

echo "--- 5. Docs gate ---"
python3 scripts/bench_check_docs.py

echo "--- 5a. Qwen eval gates (holdout + scorer + cost billing) ---"
python3 scripts/eval_verify_holdout.py
python3 scripts/eval_scorer_symmetry.py
python3 scripts/eval_cost_from_billing.py

echo "--- 5b. Privacy (no home/~/CODE paths in tracked files) ---"
bash scripts/privacy_grep.sh

echo "--- 6. Cold clone ---"
bash scripts/verify_cold_clone.sh

echo "--- 7. Hosted stranger path (at the live URL) ---"
if python3 scripts/probe_hosted_stranger_path.py --url "$BASE"; then
  echo "--- 7b. Hosted long run ---"
  bash scripts/long_run_goal.sh "$BASE"
  echo "--- 8. Stranger trial ---"
  bash scripts/new_user_trial.sh "$BASE"
else
  echo "HOSTED STRANGER PATH RED — skipping long_run/new_user_trial (would false-fail or KeyError)."
  echo "Offline stranger path remains: verify_cold_clone.sh · compound_exhibit_receipt.py"
  echo "Oscar: restore public exhibit or film CLI — docs/FINDING-hosted-stranger-path-2026-09-06.md"
  echo
  echo "=== FULL GATE OFFLINE OK · HOSTED BLOCKED === $STAMP"
  exit 2
fi

echo
echo "=== FULL GATE OK === $STAMP"
echo "Update docs/STATUS.md if anything changed."
