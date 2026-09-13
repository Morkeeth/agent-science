#!/usr/bin/env bash
# Stranger cold-clone verification — no keys, no network after clone.
# Run from any directory: bash scripts/verify_cold_clone.sh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "=== Agent Science cold-clone verify ==="
echo "repo: $ROOT"
echo

echo "1. Seed offline document cache..."
python3 scripts/seed_document_cache.py

echo
echo "2. Mutation controls (watch_it_go_red)..."
python3 tests/test_watch_it_go_red.py 2>&1 | tail -1

echo
echo "3. ADK default path..."
python3 tests/test_adk_default_path.py 2>&1 | tail -1

echo
echo "4. Partner runtime wiring..."
python3 tests/test_partner_runtime.py 2>&1 | tail -1

echo
echo "5. SUBMISSION-PACK doc gate..."
python3 scripts/bench_check_docs.py 2>&1 | tail -1

echo
echo "6. Holdout freeze gate..."
python3 scripts/eval_verify_holdout.py 2>&1 | tail -1

echo
echo "7. Registry surface (stranger block)..."
python3 tests/test_registry_surface.py -q 2>&1 | tail -1

echo
echo "8. Offline compound receipt..."
# Capture full output + exit explicitly. Do NOT pipe through head — SIGPIPE can
# turn a green compound (exit 0) into a false red, and grepping alone used to
# hide exit 3 as "OK" when callers ignored pipefail.
set +e
COMPOUND_OUT=$(python3 scripts/compound_exhibit_receipt.py 2>&1)
COMPOUND_RC=$?
set -e
echo "$COMPOUND_OUT" | grep -E 'parallel_calls|corpus_hits|Mode:|exhibit failed' | head -6 || true
if [[ "$COMPOUND_RC" -ne 0 ]]; then
  echo "FAIL: compound_exhibit_receipt.py exited $COMPOUND_RC (stranger compound broken)"
  exit "$COMPOUND_RC"
fi
echo "compound_exhibit_receipt.py exit 0"

echo
echo "9. Eval gate (baseline + ablation + scorer symmetry)..."
python3 scripts/eval_refusal_baseline.py 2>&1 | tail -3
python3 scripts/eval_refusal_ablation.py 2>&1 | tail -2
python3 scripts/eval_scorer_symmetry.py 2>&1 | tail -3

echo
echo "10. Compound cost arms (NAIVE / PARAPHRASE / EXACT + price card)..."
python3 scripts/eval_compound_cost_arms.py 2>&1 | tail -8

echo
echo "11. Artifact claims at HEAD (shipping re-derives; soft +claims forbidden)..."
python3 scripts/eval_artifact_claims.py 2>&1 | tail -6

echo
echo "=== cold-clone verify OK ==="
