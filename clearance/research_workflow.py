"""Local research actions shared by the terminal and MCP; no code execution."""
from contextlib import closing
import json

from clearance import cases


def _connect(db):
    con = cases.connect(db)
    con.execute('CREATE TABLE IF NOT EXISTS night_follows(case_id TEXT PRIMARY KEY, version INTEGER NOT NULL, followed_at TEXT NOT NULL)')
    con.commit()
    return con


def follow(case_id, *, db=None):
    case = cases.get(case_id, db=db)
    record = {'case_id': case_id, 'version': case['version'], 'followed_at': cases.now()}
    with closing(_connect(db)) as con, con:
        con.execute('INSERT OR REPLACE INTO night_follows VALUES(?,?,?)', tuple(record.values()))
    return record


def updates(*, db=None):
    from clearance import synthesis
    with closing(_connect(db)) as con:
        followed = [dict(row) for row in con.execute('SELECT * FROM night_follows ORDER BY followed_at')]
    changes = []
    for item in followed:
        current = cases.get(item['case_id'], db=db)
        if current['version'] == item['version']:
            continue
        report = synthesis.compare(item['case_id'], item['version'], db=db)
        affected = [d['id'] for d in current['decisions'] if d.get('review', {}).get('state') not in (None, 'CURRENT', 'SUPERSEDED')]
        changes.append({'case_id': item['case_id'], 'from_version': item['version'],
                        'version': current['version'], 'affected_decisions': affected, 'changes': report})
    changes.sort(key=lambda x: (-len(x['affected_decisions']), x['case_id']))
    return {'updates': changes, 'followed_count': len(followed), 'checked_online': False,
            'message': 'Saved changes since follow; no web check performed.' if changes else 'No saved changes since the followed versions. No web check performed.'}


def handle(arguments):
    if not isinstance(arguments, dict):
        raise ValueError('arguments must be an object')
    action = arguments.get('action', 'start')
    db = arguments.get('db')
    if action == 'execute-protocol':
        raise ValueError('Protocol execution is CLI-only; select a trusted script in the terminal.')
    if action == 'follow':
        return follow(arguments['case_id'], db=db)
    if action == 'updates':
        return updates(db=db)
    if action == 'experiment-plan':
        from clearance import research_protocols
        return research_protocols.create(arguments['case_id'], arguments.get('protocol', {}),
                                         root=arguments.get('root'), protocol_id=arguments.get('protocol_id'), db=db)
    if action == 'compare':
        from clearance import synthesis
        return synthesis.compare(arguments['case_id'], int(arguments['from_version']), db=db)
    if action == 'show' and arguments.get('case_id'):
        from clearance import synthesis
        return synthesis.build(cases.get(arguments['case_id'], db=db, version=arguments.get('version')))
    from clearance import night_runs
    if action in ('start', 'challenge', 'update'):
        case_id = arguments.get('case_id')
        case = cases.get(case_id, db=db) if case_id else None
        if action != 'start' and not case:
            raise ValueError('case_id is required')
        return night_runs.start(arguments.get('question') or (case or {}).get('question', ''),
                                root=arguments.get('root'), case_id=case_id,
                                challenge=action == 'challenge', policy=arguments.get('policy'), db=db)
    if action in ('show', 'context', 'cancel'):
        fn = {'show': night_runs.get, 'context': night_runs.context, 'cancel': night_runs.cancel}[action]
        return fn(arguments['run_id'], db=db)
    if action == 'resume':
        return night_runs.resume(arguments['run_id'], proposal=arguments.get('proposal'),
                                 live=bool(arguments.get('live', False)), db=db)
    raise ValueError(f'Unknown research action: {action}')
