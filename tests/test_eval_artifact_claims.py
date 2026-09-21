"""Controls for scripts/eval_artifact_claims.py — RED first, then green path."""
from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))


def _load():
    path = ROOT / "scripts/eval_artifact_claims.py"
    spec = importlib.util.spec_from_file_location("eval_artifact_claims", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_baseline_trusts_hosted_title_without_opening_object():
    """Watch the failure mode go RED: baseline says TRUE on a known-stale path claim."""
    mod = _load()
    item = {
        "id": "X",
        "claim": "Hosted /partners returns JSON without a token",
        "gold": "FALSE",
        "kind": "hosted_json",
        "path": "/partners",
        "baseline_hint": "partners path named in SUBMISSION-PACK",
    }
    assert mod._baseline(item) == "TRUE"


def test_shipping_refuses_login_gated_body():
    mod = _load()
    item = {
        "id": "Y",
        "claim": "Hosted /partners returns JSON",
        "gold": "FALSE",
        "kind": "hosted_json",
        "path": "/partners",
        "expect_any": ["\"parallel\""],
        "forbid_any": ["Access token", "Sign in", "Open your workspace"],
    }
    # Inject a login-gate body without hitting the network.
    original = mod._fetch

    def fake(url, timeout=25.0):
        return 200, "<html>Sign in · Access token · Open your workspace</html>", url

    mod._fetch = fake
    try:
        label, detail = mod._shipping(item)
    finally:
        mod._fetch = original
    assert label == "FALSE", (label, detail)
    assert "forbid" in detail


def test_fixture_gold_labels_are_frozen_booleans():
    data = json.loads((ROOT / "fixtures/artifact-claims/set.json").read_text())
    assert data["items"], "empty artifact-claims set"
    for item in data["items"]:
        assert item["gold"] in ("TRUE", "FALSE")
        assert item["id"].startswith("AC")


def test_eval_script_exit_on_live_run():
    """Run the real eval once; TRUE golds must hold or the gate hard-fails."""
    proc = __import__("subprocess").run(
        [sys.executable, str(ROOT / "scripts/eval_artifact_claims.py")],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=180,
    )
    out = (proc.stdout or "") + (proc.stderr or "")
    assert "ARTIFACT-CLAIMS EVAL" in out
    assert proc.returncode in (0, 2), out[-800:]
    # The control that embarrasses us: baseline must over-trust at least one FALSE gold.
    assert "baseline trusted" in out.lower() or "FINDING:" in out


if __name__ == "__main__":
    test_baseline_trusts_hosted_title_without_opening_object()
    print("PASS  baseline trusts hosted title without opening object")
    test_shipping_refuses_login_gated_body()
    print("PASS  shipping refuses login-gated body")
    test_fixture_gold_labels_are_frozen_booleans()
    print("PASS  fixture gold labels are frozen")
    test_eval_script_exit_on_live_run()
    print("PASS  eval script exit on live run")
    print("all passed")
