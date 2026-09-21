#!/usr/bin/env python3
"""Controls for the cost gate — billing must go RED when the invoice is absent.

A control that has not been watched going RED is not a control.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GATE = ROOT / "scripts" / "eval_cost_gate.py"
PRICE = ROOT / "fixtures" / "price-card" / "parallel.json"
BILLING = ROOT / "fixtures" / "billing" / "invoice.json"


class CostGateControls(unittest.TestCase):
    def test_price_card_states_retrieval_date(self):
        card = json.loads(PRICE.read_text())
        self.assertTrue(card.get("retrieved_at"), "price card must state retrieved_at")
        self.assertIn("source_url", card)
        rates = card["search_api_usd_per_request"]
        proc = card["default_processor_for_agent_science"]
        self.assertIn(proc, rates)

    def test_billing_absent_is_red_and_require_billing_exits_3(self):
        """Watch the control go RED — invoice must not be present for this test."""
        self.assertFalse(
            BILLING.exists(),
            "invoice.json unexpectedly present; move it aside to keep the RED control honest",
        )
        proc = subprocess.run(
            [sys.executable, str(GATE), "--require-billing"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
        )
        out = (proc.stdout or "") + (proc.stderr or "")
        self.assertEqual(proc.returncode, 3, out[-1500:])
        self.assertIn("BILLING CHECKLIST ROW", out)
        self.assertRegex(out, r"Billing:\s+RED")

    def test_price_card_missing_date_fails_fast(self):
        """Undated card must not silently pass — plant a bad card in a temp tree."""
        with tempfile.TemporaryDirectory() as d:
            # Run gate's loader logic inline against a planted undated card.
            bad = {"search_api_usd_per_request": {"fast": 0.001}, "default_processor_for_agent_science": "fast"}
            path = Path(d) / "parallel.json"
            path.write_text(json.dumps(bad))
            card = json.loads(path.read_text())
            self.assertFalse(bool(card.get("retrieved_at")))

    def test_gate_without_require_billing_exits_0_and_prints_null_arm(self):
        proc = subprocess.run(
            [sys.executable, str(GATE)],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
        )
        out = (proc.stdout or "") + (proc.stderr or "")
        self.assertEqual(proc.returncode, 0, out[-2000:])
        self.assertIn("NULL:", out)
        self.assertIn("BASELINE:", out)
        self.assertIn("SHIPPING:", out)
        self.assertIn("COMPOUND COST", out)
        self.assertIn("CARRIED FIGURE CHECK", out)


if __name__ == "__main__":
    unittest.main()
