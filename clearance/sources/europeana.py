"""Real fixtures from a real archive. No invented rights statements, ever."""
from __future__ import annotations

import json
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Optional

API = "https://api.europeana.eu/record/v2/search.json"
DEMO_KEY = "api2demo"  # Europeana's public demo key — fine for a probe, not for the build
FIXTURES = Path(__file__).resolve().parents[2] / "fixtures"


def search(query: str, rows: int = 50, wskey: str = DEMO_KEY) -> list[dict]:
    qs = urllib.parse.urlencode(
        {"wskey": wskey, "query": query, "rows": rows, "profile": "rich"}
    )
    req = urllib.request.Request(f"{API}?{qs}", headers={"User-Agent": "CLEARED-probe/0.1"})
    with urllib.request.urlopen(req, timeout=30) as r:
        payload = json.load(r)
    if not payload.get("success"):
        raise RuntimeError(f"Europeana refused: {payload.get('error')}")
    return [normalise(i) for i in payload.get("items", [])]


def normalise(item: dict) -> dict:
    def first(key, default=None):
        v = item.get(key)
        return v[0] if isinstance(v, list) and v else (v if v else default)

    rights = item.get("rights") or []
    return {
        "subject_id": item.get("id", ""),
        "subject_title": first("title", "(untitled)"),
        "instrument_uri": rights[0] if rights else None,
        "holder": first("dataProvider"),
        "country": first("country"),
        "url": item.get("guid", "").split("?")[0],
    }


def save_fixture(items: list[dict], name: str) -> Path:
    FIXTURES.mkdir(parents=True, exist_ok=True)
    p = FIXTURES / name
    p.write_text(json.dumps(items, indent=2, ensure_ascii=False))
    return p


def load_fixture(name: str) -> list[dict]:
    return json.loads((FIXTURES / name).read_text())
