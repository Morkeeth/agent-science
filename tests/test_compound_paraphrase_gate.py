"""Control: paraphrase compound embarrassment must stay measurable.

Watches RED first: if shipping starts equating paraphrases (or naive stops
compounding), this fails — do not silently lose the differential.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def _load():
    path = ROOT / "scripts/eval_compound_paraphrase.py"
    name = "eval_compound_paraphrase"
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = mod  # dataclasses need the module present during exec
    spec.loader.exec_module(mod)
    return mod


def test_naive_term_beats_shipping_on_paraphrased_compound():
    mod = _load()
    shipping = mod._run_shipping()
    naive = mod._run_naive_term()
    assert not mod._compound_ok(shipping), (
        "shipping unexpectedly compounds on paraphrased B — "
        f"A={shipping['a']['parallel_calls']} B={shipping['b']['parallel_calls']} "
        f"hits={shipping['b']['corpus_hits']}"
    )
    assert mod._compound_ok(naive), (
        "naive term baseline failed to compound — gate is broken, not product progress"
    )
    print("PASS  test_naive_term_beats_shipping_on_paraphrased_compound")


def test_exact_match_compound_exhibit_exits_zero():
    import subprocess
    r = subprocess.run(
        [sys.executable, str(ROOT / "scripts/compound_exhibit_receipt.py")],
        cwd=ROOT, capture_output=True, text=True,
    )
    assert r.returncode == 0, r.stdout[-500:] + r.stderr[-200:]
    assert "exhibit failed" not in r.stdout
    print("PASS  test_exact_match_compound_exhibit_exits_zero")


if __name__ == "__main__":
    test_naive_term_beats_shipping_on_paraphrased_compound()
    test_exact_match_compound_exhibit_exits_zero()
    print("\n2/2 passed")
