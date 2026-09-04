"""Explicit local approval for shared live research capacity; never exposed by MCP."""
from contextlib import closing
import json
from clearance import cases

RESOURCES = ('discovery_calls', 'document_reads', 'reasoning_calls', 'rounds')


def _aggregate(policy):
    aggregate = policy.get('aggregate') if isinstance(policy, dict) else None
    if not isinstance(aggregate, dict) or not isinstance(aggregate.get('id'), str) or not aggregate['id'].strip():
        raise ValueError('approval requires an aggregate id and all resource limits')
    limits = aggregate.get('limits')
    if not isinstance(limits, dict) or set(limits) != set(RESOURCES):
        raise ValueError('approval requires exactly discovery_calls, document_reads, reasoning_calls and rounds')
    if any(type(value) is not int or value < 0 for value in limits.values()):
        raise ValueError('approved limits must be nonnegative integers')
    return {'id': aggregate['id'], 'limits': limits}


def _connect(db):
    con = cases.connect(db)
    con.execute('CREATE TABLE IF NOT EXISTS night_policy_approvals(id TEXT PRIMARY KEY, limits TEXT NOT NULL, approved_at TEXT NOT NULL)')
    con.commit()
    return con


def approve(policy, *, db=None):
    aggregate = _aggregate(policy)
    encoded = json.dumps(aggregate['limits'], sort_keys=True)
    with closing(_connect(db)) as con, con:
        con.execute('BEGIN IMMEDIATE')
        prior = con.execute('SELECT limits FROM night_policy_approvals WHERE id=?', (aggregate['id'],)).fetchone()
        if prior and json.loads(prior['limits']) != aggregate['limits']:
            raise ValueError('approved policy limits are immutable; use a new explicit policy id')
        con.execute('INSERT OR IGNORE INTO night_policy_approvals VALUES(?,?,?)', (aggregate['id'], encoded, cases.now()))
    return {'aggregate': aggregate, 'approved': True, 'live_calls': 0,
        'meaning': 'Local CLI approval only. Capacity is shared within this case store; billing remains unknown. Approval does not start a run.'}


def is_approved(aggregate, *, db=None):
    if not isinstance(aggregate, dict):
        return False
    with closing(_connect(db)) as con:
        row = con.execute('SELECT limits FROM night_policy_approvals WHERE id=?', (aggregate.get('id'),)).fetchone()
    return row is not None and json.loads(row['limits']) == aggregate.get('limits')
