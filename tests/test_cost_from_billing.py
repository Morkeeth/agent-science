#!/usr/bin/env python3
"""RED-watched controls for the cost-from-billing Qwen gate.

A control that has not been watched going RED is not a control.
"""
from __future__ import annotations

import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def _run_eval(*extra: str) -> tuple[int, str]:
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts/eval_cost_from_billing.py"), *extra],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )
    return proc.returncode, (proc.stdout or "") + (proc.stderr or "")


def t_eval_passes_with_dated_card_and_baseline_arm():
    code, out = _run_eval()
    assert code == 0, out
    assert "fetched_at_utc:" in out, out
    assert "baseline:" in out and "shipping:" in out, out
    assert "invoice:" in out, out
    assert re.search(r"PASS\s+shipping", out), out


def t_card_parse_refuses_body_without_advanced_rate():
    """Watch RED: empty/garbage card must not mint USD."""
    from scripts import eval_cost_from_billing as m

    try:
        m._parse_card("no rates here", source="x", fetched_at="2026-09-18T00:00:00Z")
        raise AssertionError("expected parse fail")
    except SystemExit as e:
        assert "PARSE FAIL" in str(e), e


def t_card_parse_refuses_undated_card():
    body = (
        "Per 1,000 `turbo` or `fast` requests (default 10 results)     | 1 |\n"
        "Per 1,000 `basic` or `advanced` requests (default 10 results) | 5 |\n"
    )
    from scripts import eval_cost_from_billing as m

    try:
        m._parse_card(body, source="x", fetched_at=None)
        raise AssertionError("expected date fail")
    except SystemExit as e:
        assert "DATE MISSING" in str(e), e


def t_invoice_blocked_without_key(monkeypatch_env=True):
    import os
    from scripts import eval_cost_from_billing as m

    saved = os.environ.pop("PARALLEL_API_KEY", None)
    try:
        # Ensure key file absence does not invent invoice
        inv = m._attempt_invoice()
        assert inv["status"] == "BLOCKED", inv
        assert inv["invoice_usd"] is None, inv
    finally:
        if saved is not None:
            os.environ["PARALLEL_API_KEY"] = saved


def main() -> int:
    tests = [
        t_card_parse_refuses_body_without_advanced_rate,
        t_card_parse_refuses_undated_card,
        t_invoice_blocked_without_key,
        t_eval_passes_with_dated_card_and_baseline_arm,
    ]
    failed = 0
    for t in tests:
        name = t.__name__
        try:
            t()
            print(f"  PASS  {name}")
        except Exception as e:  # noqa: BLE001
            failed += 1
            print(f"  FAIL  {name}: {type(e).__name__}: {e}")
    print()
    if failed:
        print(f"{failed} failed")
        return 1
    print(f"{len(tests)}/{len(tests)} passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
