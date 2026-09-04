"""The corpus — verdicts persist, so the second production costs less than the first.

This is not a cache. It is the product's memory, and the compounding claim in the
pitch is only true if it exists from day one.

When CORPUS_GCS_URI=gs://bucket/object is set, the sqlite file is pulled from GCS on
connect (if missing locally) and pushed after every remember — so Cloud Run instances
can share one shelf. /tmp alone is not a product.
"""
from __future__ import annotations

import json
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
"""


def _migrate(con: sqlite3.Connection) -> None:
    have = {r[1] for r in con.execute("PRAGMA table_info(verdicts)")}
    for col in ("cause", "published_instrument"):
        if col not in have:
            con.execute(f"ALTER TABLE verdicts ADD COLUMN {col} TEXT")
    con.execute("CREATE TABLE IF NOT EXISTS verdict_observations "
                "(id INTEGER PRIMARY KEY, subject_id TEXT, use TEXT, observed_at TEXT, payload TEXT)")
    con.execute("CREATE INDEX IF NOT EXISTS verdict_observation_idx ON verdict_observations(subject_id, use)")
    for row in con.execute("SELECT * FROM verdicts").fetchall():
        if not con.execute("SELECT 1 FROM verdict_observations WHERE subject_id=? AND use=? LIMIT 1",
                           (row["subject_id"], row["use"])).fetchone():
            con.execute("INSERT INTO verdict_observations (subject_id, use, observed_at, payload) VALUES (?, ?, ?, ?)",
                        (row["subject_id"], row["use"], row["observed_at"], json.dumps(dict(row))))
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
    columns = ("subject_id", "use", "subject_title", "noun", "verdict", "reason",
               "citation_url", "quoted_terms", "holder", "interpretive", "cause",
               "published_instrument", "observed_at")
    updates = ", ".join(f"{name}=excluded.{name}" for name in columns[2:])
    con.executemany(
        f"INSERT INTO verdicts ({','.join(columns)}) VALUES ({','.join('?' for _ in columns)}) "
        f"ON CONFLICT(subject_id, use) DO UPDATE SET {updates} "
        "WHERE julianday(excluded.observed_at) >= julianday(verdicts.observed_at)", rows)
    con.executemany(
        "INSERT INTO verdict_observations (subject_id, use, observed_at, payload) VALUES (?, ?, ?, ?)",
        [(row[0], row[1], row[-1], json.dumps(dict(zip(columns, row)))) for row in rows])
    con.commit()
    uri = corpus_gcs.gcs_uri()
    path = _PATHS.get(id(con))
    if uri and path is not None:
        corpus_gcs.push(uri, path)
    return len(rows)


def recall(con: sqlite3.Connection, subject_id: str, use: str, *,
           assertion: str | None = None) -> Optional[Verdict]:
    r = con.execute(
        "SELECT * FROM verdicts WHERE subject_id=? AND use=?", (subject_id, use)
    ).fetchone()
    if not r:
        return None
    if assertion is not None:
        from .refusal_log import norm_term, is_settled_for_reuse
        if norm_term(assertion) != norm_term(r["subject_title"]):
            return None
        if not is_settled_for_reuse(verdict=r["verdict"], cause=r["cause"]):
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
