"""Local research actions shared by the terminal and MCP; no code execution."""
from contextlib import closing

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
        if not report.get('material_change', report.get('changed', False)):
            continue
        affected = [d['id'] for d in report.get('affected_decisions', [])]
        changes.append({'case_id': item['case_id'], 'from_version': item['version'],
                        'version': current['version'], 'affected_decisions': affected,
                        'affected_claim_ids': report.get('affected_claim_ids', []), 'changes': report})
    changes.sort(key=lambda x: (-len(x['affected_decisions']), -len(x['affected_claim_ids']), x['case_id']))
    return {'updates': changes, 'followed_count': len(followed), 'checked_online': False,
            'message': 'Saved changes since follow; no web check performed.' if changes else 'No saved changes since the followed versions. No web check performed.'}


def handle(arguments):
    if not isinstance(arguments, dict):
        raise ValueError('arguments must be an object')
    action = arguments.get('action', 'start')
    db = arguments.get('db')
    allowed = {'start', 'show', 'context', 'resume', 'cancel', 'reconcile', 'challenge', 'compare', 'follow', 'updates', 'update', 'experiment-plan', 'protocol', 'execute-protocol'}
    if not isinstance(action, str) or action not in allowed:
        raise ValueError('Unknown research action')
    for key in ('live',):
        if key in arguments and type(arguments[key]) is not bool:
            raise ValueError(key + ' must be a boolean')
    for key in ('proposal', 'policy', 'protocol'):
        if key in arguments and arguments[key] is not None and not isinstance(arguments[key], dict):
            raise ValueError(key + ' must be an object')
    for key in ('version', 'from_version', 'case_version'):
        if key in arguments and (type(arguments[key]) is not int or arguments[key] < 1):
            raise ValueError(key + ' must be a positive integer')
    required = []
    if action == 'reconcile':
        required = ['run_id', 'operation_id', 'acknowledgement']
        if 'case_version' not in arguments:
            raise ValueError('case_version is required')
    elif action in ('context', 'resume', 'cancel'):
        required = ['run_id']
    elif action in ('challenge', 'compare', 'follow', 'update', 'experiment-plan'):
        required = ['case_id']
    elif action == 'protocol':
        required = ['protocol_id']
    elif action == 'show':
        if bool(arguments.get('case_id')) == bool(arguments.get('run_id')):
            raise ValueError('show requires exactly one case_id or run_id')
        required = ['case_id'] if arguments.get('case_id') else ['run_id']
    for key in required:
        if not isinstance(arguments.get(key), str) or not arguments[key].strip():
            raise ValueError(key + ' is required')
    if action == 'compare' and 'from_version' not in arguments:
        raise ValueError('from_version is required')
    if action == 'execute-protocol':
        raise ValueError('Protocol execution is CLI-only; select a trusted script in the terminal.')
    if action == 'follow':
        return follow(arguments['case_id'], db=db)
    if action == 'updates':
        return updates(db=db)
    if action == 'protocol':
        from clearance import research_protocols
        return research_protocols.get(arguments['protocol_id'], version=arguments.get('version'), db=db)
    if action == 'experiment-plan':
        from clearance import research_protocols
        return research_protocols.create(arguments['case_id'], arguments.get('protocol', {}),
                                         root=arguments.get('root'), protocol_id=arguments.get('protocol_id'), db=db)
    if action == 'compare':
        from clearance import synthesis
        return synthesis.compare(arguments['case_id'], arguments['from_version'], db=db)
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
    if action == 'reconcile':
        return night_runs.reconcile(arguments['run_id'], operation_id=arguments['operation_id'],
            case_version=arguments['case_version'], acknowledgement=arguments['acknowledgement'], db=db)
    if action == 'resume':
        return night_runs.resume(arguments['run_id'], proposal=arguments.get('proposal'),
                                 live=arguments.get('live', False), db=db)
    raise ValueError(f'Unknown research action: {action}')
