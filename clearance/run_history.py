"""Last clearance run per subject — for compound delta on the desk."""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


def _path() -> Path:
    override = os.environ.get("RUN_HISTORY_JSON")
    if override:
        return Path(override)
    corpus_db = os.environ.get("CORPUS_DB")
    if corpus_db:
        return Path(corpus_db).parent / "run_history.json"
    return Path(__file__).resolve().parent.parent / "cache" / "run_history.json"


def _load() -> dict:
    p = _path()
    if not p.is_file():
        return {}
    try:
        return json.loads(p.read_text())
    except json.JSONDecodeError:
        return {}


def _save(data: dict) -> None:
    p = _path()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")


def prior(subject: str) -> Optional[dict]:
    return _load().get(subject.strip())


def record(subject: str, *, parallel_api_calls: int, corpus_hits: int,
           claims: int) -> None:
    data = _load()
    data[subject.strip()] = {
        "parallel_api_calls": parallel_api_calls,
        "corpus_hits": corpus_hits,
        "claims": claims,
        "at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    _save(data)
