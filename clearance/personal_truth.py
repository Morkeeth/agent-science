"""Personal truth DB — per-user shelf for Agent Science websearch.

Each user (or machine) gets their own indexed shelf of verified asks, refuses,
and ingested material. Shared field signals (★, blogs, practices) are inputs;
this DB is what *they* remember.

Default path: ~/.agent-science/truth.db
Override: AGENT_SCIENCE_TRUTH_DB

Magnet skill verdicts (helped/hurt/baseline) land here as claim rows when wired.
"""
from __future__ import annotations

import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

DEFAULT_DIR = Path.home() / ".agent-science"
DEFAULT_DB = DEFAULT_DIR / "truth.db"

_SCHEMA = """
CREATE TABLE IF NOT EXISTS asks (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    query_text    TEXT NOT NULL,
    result_label  TEXT NOT NULL,
    verdict       TEXT,
    cause         TEXT,
    citation_url  TEXT,
    quoted_terms  TEXT,
    cost_tier     TEXT,
    source        TEXT NOT NULL DEFAULT 'visibility',
    panel_json    TEXT,
    asked_at      TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS asks_q ON asks(query_text);
CREATE INDEX IF NOT EXISTS asks_at ON asks(asked_at);

CREATE TABLE IF NOT EXISTS truths (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    kind          TEXT NOT NULL,   -- claim | skill | field_fetch
    assertion     TEXT NOT NULL,
    verdict       TEXT,            -- GREEN | UNKNOWN | helped | hurt | baseline
    cause         TEXT,
    citation_url  TEXT,
    quoted_terms  TEXT,
    meta_json     TEXT,
    established_at TEXT NOT NULL,
    reused        INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS truths_kind ON truths(kind);
CREATE INDEX IF NOT EXISTS truths_assert ON truths(assertion);

CREATE TABLE IF NOT EXISTS fetches (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    url           TEXT NOT NULL,
    title         TEXT,
    kind          TEXT,            -- blog | github | docs | other
    fetched_at    TEXT NOT NULL,
    note          TEXT
);
"""


def db_path(path: Path | str | None = None) -> Path:
    if path is not None:
        return Path(path)
    env = os.environ.get("AGENT_SCIENCE_TRUTH_DB")
    if env:
        return Path(env)
    return DEFAULT_DB


def connect(path: Path | str | None = None) -> sqlite3.Connection:
    p = db_path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(str(p))
    con.row_factory = sqlite3.Row
    con.executescript(_SCHEMA)
    return con


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def record_ask(
    query: str,
    primary: dict,
    *,
    panel: dict | None = None,
    source: str = "visibility",
    path: Path | str | None = None,
) -> int:
    """Index one websearch / visibility result into the personal shelf."""
    con = connect(path)
    cur = con.execute(
        """
        INSERT INTO asks(
            query_text, result_label, verdict, cause, citation_url,
            quoted_terms, cost_tier, source, panel_json, asked_at
        ) VALUES (?,?,?,?,?,?,?,?,?,?)
        """,
        (
            query.strip(),
            primary.get("label") or primary.get("result_label") or "UNKNOWN",
            primary.get("verdict"),
            primary.get("cause"),
            primary.get("citation_url"),
            (primary.get("quoted_terms") or "")[:2000] or None,
            primary.get("cost_tier"),
            source,
            json.dumps(panel, default=str) if panel else None,
            _now(),
        ),
    )
    ask_id = int(cur.lastrowid)
    # Promote SOURCED / explicit refuses into truths table for reuse
    label = (primary.get("label") or primary.get("result_label") or "").upper()
    if label in ("SOURCED", "UNSOURCED", "UNKNOWN", "REFUTED") and (
        primary.get("citation_url") or primary.get("cause")
    ):
        con.execute(
            """
            INSERT INTO truths(
                kind, assertion, verdict, cause, citation_url,
                quoted_terms, meta_json, established_at
            ) VALUES (?,?,?,?,?,?,?,?)
            """,
            (
                "claim",
                query.strip(),
                primary.get("verdict") or label,
                primary.get("cause"),
                primary.get("citation_url"),
                (primary.get("quoted_terms") or "")[:2000] or None,
                json.dumps({"ask_id": ask_id, "cost_tier": primary.get("cost_tier")}),
                _now(),
            ),
        )
    con.commit()
    con.close()
    return ask_id


def record_skill_truth(
    skill: str,
    verdict: str,
    *,
    probe: str | None = None,
    note: str | None = None,
    path: Path | str | None = None,
) -> int:
    """Magnet bridge — helped / hurt / baseline as a truth row."""
    v = verdict.strip().lower()
    if v not in ("helped", "hurt", "baseline"):
        raise ValueError("skill verdict must be helped|hurt|baseline")
    con = connect(path)
    assertion = f"skill:{skill}" + (f" probe:{probe}" if probe else "")
    cur = con.execute(
        """
        INSERT INTO truths(
            kind, assertion, verdict, cause, citation_url,
            quoted_terms, meta_json, established_at
        ) VALUES (?,?,?,?,?,?,?,?)
        """,
        (
            "skill",
            assertion,
            v,
            note,
            None,
            None,
            json.dumps({"skill": skill, "probe": probe}),
            _now(),
        ),
    )
    tid = int(cur.lastrowid)
    con.commit()
    con.close()
    return tid


def record_fetch(
    url: str,
    *,
    title: str | None = None,
    kind: str = "other",
    note: str | None = None,
    path: Path | str | None = None,
) -> int:
    con = connect(path)
    cur = con.execute(
        """
        INSERT INTO fetches(url, title, kind, fetched_at, note)
        VALUES (?,?,?,?,?)
        """,
        (url, title, kind, _now(), note),
    )
    fid = int(cur.lastrowid)
    con.commit()
    con.close()
    return fid


def lookup_local(query: str, *, path: Path | str | None = None) -> Optional[dict]:
    """Exact prior ask on the personal shelf (free local hit)."""
    con = connect(path)
    row = con.execute(
        """
        SELECT * FROM asks
        WHERE lower(trim(query_text)) = lower(trim(?))
        ORDER BY id DESC LIMIT 1
        """,
        (query,),
    ).fetchone()
    con.close()
    return dict(row) if row else None


def recent_asks(*, limit: int = 20, path: Path | str | None = None) -> list[dict]:
    con = connect(path)
    rows = con.execute(
        "SELECT * FROM asks ORDER BY id DESC LIMIT ?", (limit,)
    ).fetchall()
    con.close()
    return [dict(r) for r in rows]


def recent_truths(
    *, kind: str | None = None, limit: int = 20, path: Path | str | None = None
) -> list[dict]:
    con = connect(path)
    if kind:
        rows = con.execute(
            "SELECT * FROM truths WHERE kind=? ORDER BY id DESC LIMIT ?",
            (kind, limit),
        ).fetchall()
    else:
        rows = con.execute(
            "SELECT * FROM truths ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
    con.close()
    return [dict(r) for r in rows]


def stats(path: Path | str | None = None) -> dict[str, Any]:
    con = connect(path)
    asks_n = con.execute("SELECT COUNT(*) FROM asks").fetchone()[0]
    truths_n = con.execute("SELECT COUNT(*) FROM truths").fetchone()[0]
    skills_n = con.execute(
        "SELECT COUNT(*) FROM truths WHERE kind='skill'"
    ).fetchone()[0]
    fetches_n = con.execute("SELECT COUNT(*) FROM fetches").fetchone()[0]
    con.close()
    return {
        "db": str(db_path(path)),
        "asks": asks_n,
        "truths": truths_n,
        "skills": skills_n,
        "fetches": fetches_n,
    }


def ingest_field_signals(path: Path | str | None = None) -> dict:
    """Pull shared field-signals.json URLs into personal fetches (new material)."""
    root = Path(__file__).resolve().parent.parent
    signals = root / "truth-dictionary" / "field-signals.json"
    if not signals.exists():
        return {"ok": False, "error": "no field-signals.json"}
    data = json.loads(signals.read_text())
    n = 0
    for g in data.get("github") or []:
        record_fetch(
            g["url"],
            title=g.get("repo"),
            kind="github",
            note=f"stars={g.get('stars')} · {g.get('why')}",
            path=path,
        )
        n += 1
    for b in data.get("blogs_and_docs") or []:
        record_fetch(
            b["url"],
            title=b.get("title"),
            kind=b.get("kind") or "blog",
            note=b.get("when"),
            path=path,
        )
        n += 1
    return {"ok": True, "fetched": n, **stats(path)}
