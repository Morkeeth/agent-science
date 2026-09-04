"""Followed questions — day-two watch list over saved research cases.

Following is local persistence only. It does not schedule paid fetches.
An explicit `updates` run advances checked timestamps when a refresh actually runs.
"""
from __future__ import annotations

from contextlib import closing
import copy
import json
import uuid

from clearance import cases


def _ensure(con):
    con.executescript('''
        CREATE TABLE IF NOT EXISTS followed_questions(
            id TEXT PRIMARY KEY,
            case_id TEXT NOT NULL UNIQUE,
            body TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS followed_questions_case ON followed_questions(case_id);
    ''')


def connect(db=None):
    con = cases.connect(db)
    try:
        _ensure(con)
        con.commit()
    except Exception:
        con.close()
        raise
    return con


def follow(case_id, *, db=None, note=''):
    """Track a saved case as a followed question. Idempotent on the same case_id."""
    if not isinstance(case_id, str) or not case_id.strip():
        raise ValueError('case_id is required')
    if not isinstance(note, str) or len(note) > 2000:
        raise ValueError('note must be text of at most 2000 characters')
    data = cases.get(case_id, db=db)
    now = cases.now()
    with closing(connect(db)) as con:
        con.execute('BEGIN IMMEDIATE')
        row = con.execute('SELECT body FROM followed_questions WHERE case_id=?', (case_id,)).fetchone()
        if row:
            body = json.loads(row['body'])
            body['note'] = note.strip()
            body['question'] = data['question']
            body['case_version_at_follow'] = body.get('case_version_at_follow', data['version'])
            body['active'] = True
            body['updated_at'] = now
            con.execute(
                'UPDATE followed_questions SET body=?, updated_at=? WHERE case_id=?',
                (json.dumps(body), now, case_id),
            )
            con.commit()
            return get(body['id'], db=db)
        fid = uuid.uuid4().hex[:12]
        body = {
            'id': fid,
            'case_id': case_id,
            'question': data['question'],
            'note': note.strip(),
            'followed_at': now,
            'updated_at': now,
            'case_version_at_follow': data['version'],
            'last_case_version': data['version'],
            'last_checked_at': None,
            'last_checked_online': False,
            'last_update_run_id': None,
            'active': True,
        }
        con.execute(
            'INSERT INTO followed_questions(id,case_id,body,created_at,updated_at) VALUES(?,?,?,?,?)',
            (fid, case_id, json.dumps(body), now, now),
        )
        con.commit()
    return get(fid, db=db)


def unfollow(case_id=None, *, follow_id=None, db=None):
    if not case_id and not follow_id:
        raise ValueError('provide case_id or follow_id')
    with closing(connect(db)) as con, con:
        if follow_id:
            row = con.execute('SELECT body FROM followed_questions WHERE id=?', (follow_id,)).fetchone()
        else:
            row = con.execute('SELECT body FROM followed_questions WHERE case_id=?', (case_id,)).fetchone()
        if row is None:
            raise ValueError('followed question not found')
        body = json.loads(row['body'])
        body['active'] = False
        body['updated_at'] = cases.now()
        con.execute(
            'UPDATE followed_questions SET body=?, updated_at=? WHERE id=?',
            (json.dumps(body), body['updated_at'], body['id']),
        )
    return get(body['id'], db=db)


def get(follow_id, *, db=None):
    with closing(connect(db)) as con, con:
        row = con.execute('SELECT body FROM followed_questions WHERE id=?', (follow_id,)).fetchone()
        if row is None:
            raise ValueError('followed question not found')
        return json.loads(row['body'])


def get_by_case(case_id, *, db=None):
    with closing(connect(db)) as con, con:
        row = con.execute('SELECT body FROM followed_questions WHERE case_id=?', (case_id,)).fetchone()
        if row is None:
            raise ValueError('followed question not found for case')
        return json.loads(row['body'])


def list_followed(*, db=None, active_only=True, limit=50):
    if type(limit) is not int or not 1 <= limit <= 200:
        raise ValueError('limit must be 1–200')
    with closing(connect(db)) as con, con:
        rows = [
            json.loads(r['body'])
            for r in con.execute(
                'SELECT body FROM followed_questions ORDER BY updated_at DESC, id DESC'
            )
        ]
    if active_only:
        rows = [r for r in rows if r.get('active', True)]
    return rows[:limit]


def record_check(follow_id, *, case_version, checked_online, update_run_id=None, db=None):
    """Advance follow metadata after an explicit update run.

    `checked_online` must be True only when the update performed actual web fetches
    (freshness.new_fetches > 0). Snapshot reuse alone does not claim online check.
    """
    if type(case_version) is not int or case_version < 1:
        raise ValueError('case_version must be a positive integer')
    if type(checked_online) is not bool:
        raise ValueError('checked_online must be a boolean')
    body = get(follow_id, db=db)
    now = cases.now()
    body['last_case_version'] = case_version
    body['last_checked_at'] = now
    body['last_checked_online'] = checked_online
    body['last_update_run_id'] = update_run_id
    body['updated_at'] = now
    with closing(connect(db)) as con, con:
        con.execute(
            'UPDATE followed_questions SET body=?, updated_at=? WHERE id=?',
            (json.dumps(body), now, follow_id),
        )
    return get(follow_id, db=db)


def render(rows):
    if not rows:
        return (
            'No followed questions.\n'
            'Follow a case after your first useful investigation:\n'
            '  agent-science research follow CASE_ID\n'
        )
    lines = ['FOLLOWED QUESTIONS', '']
    for row in rows:
        status = 'active' if row.get('active', True) else 'inactive'
        checked = row.get('last_checked_at') or 'never'
        online = 'online' if row.get('last_checked_online') else 'snapshot-only / unchecked'
        lines.append(f"{row['id']} · {status} · case {row['case_id']} · v{row.get('last_case_version')}")
        lines.append(f"  {row['question']}")
        lines.append(f"  last check: {checked} ({online})")
        if row.get('note'):
            lines.append(f"  note: {row['note']}")
        lines.append('')
    return '\n'.join(lines).rstrip() + '\n'


def public_follow(row):
    return copy.deepcopy(row)
