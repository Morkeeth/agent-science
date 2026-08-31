"""Community notes stub — upload / dispute claims (community-notes mechanism)."""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

_DEFAULT_DIR = Path.home() / ".agent-science"
_DEFAULT_FILE = _DEFAULT_DIR / "community-notes.jsonl"
_SEED_FILE = Path(__file__).resolve().parent.parent / "data" / "community-notes-seed.jsonl"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def notes_path(path: Path | str | None = None) -> Path:
    if path is not None:
        return Path(path)
    env = os.environ.get("AGENT_SCIENCE_NOTES")
    if env:
        return Path(env)
    return _DEFAULT_FILE


def _ensure_seed(path: Path) -> None:
    if path.exists() and path.stat().st_size > 0:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    if _SEED_FILE.exists():
        path.write_text(_SEED_FILE.read_text(encoding="utf-8"), encoding="utf-8")


def list_notes(*, status: str | None = None, path: Path | str | None = None) -> list[dict]:
    p = notes_path(path)
    _ensure_seed(p)
    if not p.exists():
        return []
    rows: list[dict] = []
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if status and row.get("status") != status:
            continue
        rows.append(row)
    return rows


def upload(
    claim: str,
    *,
    submitter: str = "anonymous",
    url: str | None = None,
    path: Path | str | None = None,
) -> dict:
    p = notes_path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    row = {
        "id": str(uuid4())[:8],
        "claim": claim.strip(),
        "submitter": submitter,
        "url": url,
        "dispute": None,
        "status": "pending",
        "created_at": _now(),
    }
    with p.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")
    return row


def dispute(
    note_id: str,
    dispute_text: str,
    *,
    submitter: str = "anonymous",
    path: Path | str | None = None,
) -> dict | None:
    p = notes_path(path)
    if not p.exists():
        return None
    lines = p.read_text(encoding="utf-8").splitlines()
    updated: dict | None = None
    out_lines: list[str] = []
    for line in lines:
        if not line.strip():
            continue
        row = json.loads(line)
        if row.get("id") == note_id and updated is None:
            row["dispute"] = {
                "text": dispute_text.strip(),
                "submitter": submitter,
                "at": _now(),
            }
            row["status"] = "disputed"
            updated = row
        out_lines.append(json.dumps(row))
    if updated:
        p.write_text("\n".join(out_lines) + "\n", encoding="utf-8")
    return updated
