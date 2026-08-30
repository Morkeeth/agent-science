"""The corpus — verdicts persist, so the second production costs less than the first.

This is not a cache. It is the product's memory, and the compounding claim in the
pitch is only true if it exists from day one.

When CORPUS_GCS_URI=gs://bucket/object is set, the sqlite file is pulled from GCS on
connect (if missing locally) and pushed after every remember — so Cloud Run instances
can share one shelf. /tmp alone is not a product.
"""
from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from typing import Iterable, Optional

from . import corpus_gcs
from .verdict import Verdict

# CORPUS_DB was set in the Dockerfile and in deploy.sh and read by NOTHING - the seam
# existing without the service being called, this time in our own deployment config. On
# Cloud Run the filesystem is read-only except /tmp, so the container would have tried to
# write to /app/cache/corpus.db and died on the first request that stored a verdict. The
# hosted demo would have failed on camera, with every local test green.
DB = Path(os.environ.get("CORPUS_DB")
          or Path(__file__).resolve().parent.parent / "cache" / "corpus.db")

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
    cause         TEXT,
    published_instrument TEXT,
    observed_at   TEXT NOT NULL,
    PRIMARY KEY (subject_id, use)
);
CREATE TABLE IF NOT EXISTS run_stats (
    subject         TEXT PRIMARY KEY,
    parallel_calls  INTEGER NOT NULL,
    observed_at     TEXT NOT NULL
);
"""


def _migrate(con: sqlite3.Connection) -> None:
    have = {r[1] for r in con.execute("PRAGMA table_info(verdicts)")}
    for col in ("cause", "published_instrument"):
        if col not in have:
            con.execute(f"ALTER TABLE verdicts ADD COLUMN {col} TEXT")
    con.commit()


_PATHS: dict[int, Path] = {}


def connect(path: Path | str = DB) -> sqlite3.Connection:
    # In-memory DBs are for controls; never sync them to GCS.
    if path == ":memory:":
        con = sqlite3.connect(":memory:")
        con.row_factory = sqlite3.Row
        con.executescript(_SCHEMA)
        _migrate(con)
        return con
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    uri = corpus_gcs.gcs_uri()
    if uri and not p.exists():
        try:
            corpus_gcs.pull(uri, p)
        except Exception:
            pass  # empty shelf on first boot
    con = sqlite3.connect(p)
    con.row_factory = sqlite3.Row
    con.executescript(_SCHEMA)
    _migrate(con)
    _PATHS[id(con)] = p
    return con


def remember(con: sqlite3.Connection, verdicts: Iterable[Verdict]) -> int:
    rows = [
        (v.subject_id, v.use, v.subject_title, v.noun, v.verdict, v.reason,
         v.citation_url, v.quoted_terms, v.holder, int(v.interpretive),
         v.cause, v.published_instrument, v.observed_at)
        for v in verdicts
    ]
    con.executemany(
        "INSERT OR REPLACE INTO verdicts VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)", rows
    )
    con.commit()
    uri = corpus_gcs.gcs_uri()
    path = _PATHS.get(id(con))
    if uri and path is not None:
        corpus_gcs.push(uri, path)
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
        cause=r["cause"], published_instrument=r["published_instrument"],
        observed_at=r["observed_at"],
    )


def size(con: sqlite3.Connection) -> int:
    return con.execute("SELECT COUNT(*) FROM verdicts").fetchone()[0]


def size_for_use(con: sqlite3.Connection, use: str) -> int:
    return con.execute(
        "SELECT COUNT(*) FROM verdicts WHERE use=?", (use,)
    ).fetchone()[0]


def prior_parallel(con: sqlite3.Connection, subject: str) -> Optional[int]:
    """Last recorded parallel_calls for this subject shelf (before the current run)."""
    r = con.execute(
        "SELECT parallel_calls FROM run_stats WHERE subject=?", (subject,)
    ).fetchone()
    return int(r[0]) if r else None


def remember_parallel(con: sqlite3.Connection, subject: str, parallel_calls: int) -> None:
    """Persist parallel_calls for A-vs-B delta on the next run on the same subject."""
    from datetime import datetime, timezone
    con.execute(
        "INSERT OR REPLACE INTO run_stats VALUES (?,?,?)",
        (subject, parallel_calls, datetime.now(timezone.utc).isoformat()),
    )
    con.commit()
    uri = corpus_gcs.gcs_uri()
    path = _PATHS.get(id(con))
    if uri and path is not None:
        corpus_gcs.push(uri, path)
