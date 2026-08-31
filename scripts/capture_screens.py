#!/usr/bin/env python3
"""Capture hosted UI screenshots for docs/assets/screens/."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "assets" / "screens"
BASE = sys.argv[1] if len(sys.argv) > 1 else "https://agent-science-568004190078.us-central1.run.app"

PAGES = [
    ("/", "01-desk-home.png", 1280, 900),
    ("/front", "02-front-wedge.png", 1280, 1400),
    ("/registry", "03-registry-shelf.png", 1280, 1400),
    ("/registry?q=2012%2F28%2FEU", "04-registry-search.png", 1280, 1200),
    ("/popular/ui", "05-popular-ui.png", 1280, 1400),
    ("/visibility/ui", "08-visibility-ui.png", 1280, 2000),
    ("/truths/ui", "07-truths-dashboard.png", 1280, 1400),
    ("/partners", "06-partners-json.png", 1280, 900),
]


def main() -> int:
    from playwright.sync_api import sync_playwright

    OUT.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1280, "height": 900})
        for path, name, w, h in PAGES:
            url = f"{BASE.rstrip('/')}{path}"
            page.set_viewport_size({"width": w, "height": h})
            page.goto(url, wait_until="networkidle", timeout=60_000)
            page.wait_for_timeout(800)
            dest = OUT / name
            page.screenshot(path=str(dest), full_page=True)
            print(f"wrote {dest.relative_to(ROOT)}")
        browser.close()
    print(f"done — {len(PAGES)} screens @ {BASE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
