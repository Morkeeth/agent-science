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

echo "--- 5. Docs gate ---"
python3 scripts/bench_check_docs.py

echo "--- 5a. Qwen eval gates (holdout + scorer symmetry + null + artifact claims) ---"
python3 scripts/eval_verify_holdout.py
python3 scripts/eval_scorer_symmetry.py
python3 scripts/eval_null_arm.py
python3 scripts/eval_artifact_claims.py --offline
python3 tests/test_artifact_claims.py
python3 scripts/eval_suite_coverage.py

echo "--- 5b. Privacy (no home/~/CODE paths in tracked files) ---"
bash scripts/privacy_grep.sh

echo "--- 6. Cold clone ---"
bash scripts/verify_cold_clone.sh

echo "--- 7. Hosted long run ---"
bash scripts/long_run_goal.sh "$BASE"

echo "--- 8. Stranger trial ---"
bash scripts/new_user_trial.sh "$BASE"

echo
echo "=== FULL GATE OK === $STAMP"
echo "Update docs/STATUS.md if anything changed."
