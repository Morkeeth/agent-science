"""Tests for visibility transparency panes (angles / shallow / imbalance)."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def t_transparency_in_full_panel():
    from clearance import visibility
    data = visibility.panel("ralph loop agentic", full=True, personal=False)
    trans = data.get("transparency") or {}
    assert "angles_searched" in trans
    assert len(trans["angles_searched"]) >= 3
    assert "shallow_route" in trans
    assert isinstance(trans["shallow_route"], bool)


def t_transparency_formatted():
    from clearance import visibility
    data = visibility.panel("Directive 2012/28/EU", full=True, personal=False)
    text = visibility.format_panel(data)
    assert "Transparency" in text
    assert "SHALLOW_ROUTE" in text
    assert "IMBALANCE" in text
    assert "angles" in text.lower() or "variant=" in text


def t_stack_fit_in_full_panel():
    from clearance import visibility
    data = visibility.panel("science_lookup MCP cursor", full=True, personal=False)
    assert "stack_fit" in data
    assert data["stack_fit"].get("fit") in ("fits", "partial", "mismatch")


def t_visibility_html_panel():
    from cloud.service import _visibility_page, _visibility_panel_html, _visibility_panel
    data = _visibility_panel("ralph loop agentic", full=True)
    html = _visibility_panel_html(data)
    assert "SHALLOW_ROUTE" in html
    assert "angles" in html.lower() or "dictionary_exact" in html
    assert "IMBALANCE" in html
    page = _visibility_page("ralph loop agentic", full=True)
    assert "<pre>" not in page
    assert "Paste a script" in page


def t_angles_include_tiers():
    from clearance import visibility
    data = visibility.panel("orphan works directive", full=False, personal=False)
    angles = (data.get("transparency") or {}).get("angles_searched") or []
    tiers = {a.get("tier") for a in angles}
    assert "free" in tiers


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("t_") and callable(v)]
    failed = 0
    for fn in fns:
        try:
            fn()
            print(f"PASS  {fn.__name__}")
        except AssertionError as e:
            failed += 1
            print(f"FAIL  {fn.__name__}: {e}")
    print(f"\n{len(fns) - failed}/{len(fns)} passed")
    sys.exit(1 if failed else 0)
