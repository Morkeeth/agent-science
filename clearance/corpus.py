"""The corpus — verdicts persist, so the second production costs less than the first.

This is not a cache. It is the product's memory, and the compounding claim in the
pitch is only true if it exists from day one.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Iterable, Optional

from .verdict import Verdict

DB = Path(__file__).resolve().parent.parent / "cache" / "corpus.db"

_SCHEMA = """
CREATE TABLE IF NOT EXISTS verdicts (
    subject_id    TEXT NOT NULL,
    use           TEXT NOT NULL,
    subject_title TEXT NOT NULL,
    noun          TEXT NOT NULL,
    verdict       TEXT NOT NULL,
    reason        TEXT NOT NULL,
    citation_url  TEXT,
    quoted_terms  TEXT,
    holder        TEXT,
    interpretive  INTEGER NOT NULL DEFAULT 0,
    observed_at   TEXT NOT NULL,
    PRIMARY KEY (subject_id, use)
);
"""


def connect(path: Path | str = DB) -> sqlite3.Connection:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(p)
    con.row_factory = sqlite3.Row
    con.executescript(_SCHEMA)
    return con


def remember(con: sqlite3.Connection, verdicts: Iterable[Verdict]) -> int:
    rows = [
        (v.subject_id, v.use, v.subject_title, v.noun, v.verdict, v.reason,
         v.citation_url, v.quoted_terms, v.holder, int(v.interpretive), v.observed_at)
        for v in verdicts
    ]
    con.executemany(
        "INSERT OR REPLACE INTO verdicts VALUES (?,?,?,?,?,?,?,?,?,?,?)", rows
    )
    con.commit()
    return len(rows)


def recall(con: sqlite3.Connection, subject_id: str, use: str) -> Optional[Verdict]:
    r = con.execute(
        "SELECT * FROM verdicts WHERE subject_id=? AND use=?", (subject_id, use)
    ).fetchone()
    if not r:
        return None
    return Verdict(
        subject_id=r["subject_id"], subject_title=r["subject_title"], noun=r["noun"],
        use=r["use"], verdict=r["verdict"], reason=r["reason"],
        citation_url=r["citation_url"], quoted_terms=r["quoted_terms"],
        holder=r["holder"], interpretive=bool(r["interpretive"]),
        observed_at=r["observed_at"],
    )


def size(con: sqlite3.Connection) -> int:
    return con.execute("SELECT COUNT(*) FROM verdicts").fetchone()[0]
