"""Adaptive research runs: question maps, challenge investigations, interrupt/resume.

A challenge is a new investigation against a pinned case version. It looks for
observations that could overturn material claims — not agreeing prose.

Without a configured model reasoner, the local planner proposes structured gaps
and searches. Assessments still require exact source quotes. Provider billing is
never inferred from request counts.
"""
from __future__ import annotations

from contextlib import closing
import copy
import json
import re
import sqlite3
import uuid
from urllib.parse import urlsplit

from clearance import cases, discovery, research

STOP_REASONS = (
    'evidence_sufficient',
    'diminishing_new_evidence',
    'missing_access',
    'budget_exhausted',
    'cancelled',
    'max_steps',
    'plan_only',
)

LIMIT_DEFAULTS = {
    'max_discovery_calls': 8,
    'max_document_reads': 20,
    'max_rounds': 3,
    'results_per_provider': 5,
}

LIMITATION_HINT = re.compile(
    r'\b(limitation|limitations|replication|replicate|fail(?:ed|ure)?|contrary|'
    r'however|does not (?:generaliz|apply)|only (?:on|for|when)|cannot|'
    r'unresolved|future work|caveat)\b',
    re.I,
)


def _limits(overrides=None):
    out = dict(LIMIT_DEFAULTS)
    if overrides:
        for key, value in overrides.items():
            if key not in out:
                raise ValueError(f'unknown run limit: {key}')
            if type(value) is not int or value < 0:
                raise ValueError(f'run limit {key} must be a nonnegative integer')
            out[key] = value
    return out


def _ensure_runs(con):
    con.executescript('''
        CREATE TABLE IF NOT EXISTS research_runs(
            id TEXT PRIMARY KEY,
            case_id TEXT NOT NULL,
            body TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS research_runs_case ON research_runs(case_id);
    ''')


def connect(db=None):
    con = cases.connect(db)
    try:
        _ensure_runs(con)
        con.commit()
    except Exception:
        con.close()
        raise
    return con


def _save_run(run, *, db=None):
    run = copy.deepcopy(run)
    run['updated_at'] = cases.now()
    with closing(connect(db)) as con, con:
        con.execute(
            'INSERT INTO research_runs(id,case_id,body,created_at,updated_at) VALUES(?,?,?,?,?) '
            'ON CONFLICT(id) DO UPDATE SET body=excluded.body, updated_at=excluded.updated_at',
            (run['id'], run['case_id'], json.dumps(run), run['created_at'], run['updated_at']),
        )
    return get_run(run['id'], db=db)


def get_run(run_id, *, db=None):
    with closing(connect(db)) as con, con:
        row = con.execute('SELECT body FROM research_runs WHERE id=?', (run_id,)).fetchone()
        if row is None:
            raise ValueError('research run not found')
        return json.loads(row['body'])


def list_runs(*, case_id=None, db=None, limit=20):
    limit = max(1, min(int(limit), 100))
    with closing(connect(db)) as con, con:
        if case_id:
            rows = con.execute(
                'SELECT body FROM research_runs WHERE case_id=? ORDER BY updated_at DESC LIMIT ?',
                (case_id, limit),
            ).fetchall()
        else:
            rows = con.execute(
                'SELECT body FROM research_runs ORDER BY updated_at DESC LIMIT ?', (limit,)
            ).fetchall()
    return [json.loads(r['body']) for r in rows]


def _node(subquestion, *, competing='', importance='high', proposed_search='',
          intent='original', gap='', status='open', source_evidence_id=None):
    return {
        'id': uuid.uuid4().hex[:12],
        'subquestion': subquestion,
        'competing_explanation': competing,
        'importance': importance,
        'proposed_search': proposed_search or subquestion,
        'intent': intent,
        'inspected_evidence_ids': [],
        'gap': gap or subquestion,
        'status': status,
        'source_evidence_id': source_evidence_id,
    }


def initial_question_map(question):
    """Deterministic first map. Later rounds add gaps from inspected evidence."""
    q = question.strip()
    return [
        _node(q, intent='original', proposed_search=q + ' empirical study methods limitations',
              gap='Need primary empirical evidence with methods and limits', importance='high'),
        _node('Has this finding failed to replicate or been contradicted?',
              competing='The apparent effect is measurement- or task-specific',
              intent='replication', proposed_search=q + ' replication failure contradiction',
              gap='No contrary or replication-failure evidence inspected yet', importance='high'),
        _node('What do official docs constrain about this practice?',
              intent='official', proposed_search=q + ' official documentation constraints',
              gap='Official constraints not yet inspected', importance='medium'),
        _node('What do practitioners report when this fails?',
              intent='practice', proposed_search=q + ' practitioner failure report limitations',
              gap='Field practice failures not yet inspected', importance='medium'),
    ]


def challenge_question_map(data):
    """Build overturn targets from a pinned answer version."""
    brief = research.brief(data)
    nodes = []
    for claim in brief['claims']:
        if claim['state'] in ('UNRESOLVED',):
            continue
        statement = claim['statement']
        nodes.append(_node(
            f'What observation would overturn: {statement[:240]}',
            competing=statement,
            intent='challenge',
            proposed_search=f'replication failure contradiction evidence against: {statement[:180]}',
            gap=f'No overturning evidence inspected for claim {claim["id"]}',
            importance='high' if claim['state'] in ('SUPPORTED_AS_ASSESSED', 'CONTESTED') else 'medium',
        ))
        nodes[-1]['target_claim_id'] = claim['id']
        nodes[-1]['target_state'] = claim['state']
    if not nodes:
        # Still investigate — absence of assessed claims is itself a gap.
        nodes.append(_node(
            f'Find contrary evidence for the open question: {data["question"]}',
            intent='challenge',
            proposed_search=data['question'] + ' contrary evidence limitations failure',
            gap='Pinned version has no assessed claims; seek contrary primary sources',
            importance='high',
        ))
    return nodes


def gaps_from_evidence(data, existing_map):
    """Derive follow-up gaps from inspected sources — not a fixed search list."""
    known = {(n.get('source_evidence_id'), n['proposed_search']) for n in existing_map}
    known_searches = {n['proposed_search'] for n in existing_map}
    added = []
    for e in data.get('evidence', []):
        quote = e.get('quote') or ''
        text = (e.get('snapshot_text') or '')[:8000]
        if e.get('status') == 'UNAVAILABLE':
            node = _node(
                f'Recover or replace inaccessible source {e["url"]}',
                intent='access',
                proposed_search=e['url'],
                gap=f'Source unavailable: {e.get("reason", "missing")}',
                importance='medium',
                source_evidence_id=e['id'],
            )
            node['proposed_url'] = e['url']
            if (e['id'], node['proposed_search']) not in known:
                added.append(node)
            continue
        if LIMITATION_HINT.search(quote) or LIMITATION_HINT.search(text[:1200]):
            # Follow the limitation language into a new public query.
            snippet = quote or next(
                (s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if LIMITATION_HINT.search(s)),
                data['question'],
            )
            terms = ' '.join(re.findall(r'[A-Za-z]{4,}', snippet)[:12])
            proposed = f'{terms} contradictory evidence replication'
            if proposed not in known_searches and (e['id'], proposed) not in known:
                added.append(_node(
                    f'Follow limitation noted in {e["id"]}',
                    competing=snippet[:300],
                    intent='replication',
                    proposed_search=proposed,
                    gap=f'Limitation/contrary hint in source {e["id"]} not yet pursued',
                    importance='high',
                    source_evidence_id=e['id'],
                ))
    cov = cases.coverage(data.get('evidence', []))
    for kind in cov['missing_kinds']:
        label = {
            'research_repository': 'empirical study methods sample limitations',
            'declared_official': 'official documentation constraints',
            'web_source': 'practitioner implementation failure report',
        }[kind]
        proposed = f'{data["question"]} {label}'
        if proposed not in known_searches:
            added.append(_node(
                f'Fill missing source kind: {kind}',
                intent={'research_repository': 'original', 'declared_official': 'official',
                        'web_source': 'practice'}[kind],
                proposed_search=proposed,
                gap=f'Coverage missing {kind}',
                importance='medium',
            ))
    for url in research.brief(data).get('unread_report_citations', [])[:5]:
        proposed = url
        if proposed not in known_searches:
            node = _node(
                f'Read unread citation {urlsplit(url).hostname or url}',
                intent='citation',
                proposed_search=proposed,
                gap=f'Unread report citation: {url}',
                importance='high',
            )
            node['proposed_url'] = url
            added.append(node)
    return added


def _new_run(*, case_id, base_version, question, kind, question_map, limits=None,
             pinned_answer=None, providers=('parallel',)):
    now = cases.now()
    return {
        'id': uuid.uuid4().hex[:12],
        'case_id': case_id,
        'base_case_version': base_version,
        'kind': kind,
        'question': question,
        'question_map': question_map,
        'status': 'planned',
        'cursor': 0,
        'configured_limits': _limits(limits),
        'observed_usage': {
            'discovery_calls': 0,
            'document_reads': 0,
            'rounds': 0,
            'cost': 'unknown',
            'meaning': 'Cost is unknown unless a provider returns billing; request counts are not dollars.',
        },
        'steps': [],
        'stop_reason': None,
        'providers': list(providers),
        'pinned_answer': pinned_answer,
        'answer': None,
        'created_at': now,
        'updated_at': now,
        'reasoner': 'local_planner',
        'limits_note': [
            'Local planner proposes gaps and searches; it does not author scientific verdicts.',
            'Assessments require exact quotes from source snapshots.',
            'Live discovery requires explicit --live and configured providers.',
        ],
    }


def _step(op, *, query='', url='', provider='', state='proposed', response_ref=None,
          resulting_case_version=None, outcome='', gap_id=None):
    return {
        'id': uuid.uuid4().hex[:12],
        'op': op,
        'proposed_query': query,
        'proposed_url': url,
        'provider': provider,
        'state': state,
        'response_ref': response_ref,
        'resulting_case_version': resulting_case_version,
        'outcome': outcome,
        'gap_id': gap_id,
        'at': cases.now(),
    }


def _open_gaps(run):
    order = {'high': 0, 'medium': 1, 'low': 2}
    return sorted(
        (n for n in run['question_map'] if n['status'] == 'open'),
        key=lambda n: (order.get(n.get('importance', 'medium'), 9), n['id']),
    )


def _fingerprint(provider, query, url=''):
    return f'{provider}\0{(query or "").strip()}\0{(url or "").strip()}'


def _completed_discoveries(run):
    out = set()
    for step in run['steps']:
        if step['op'] == 'discover' and step['state'] == 'completed':
            out.add(_fingerprint(step.get('provider', ''), step.get('proposed_query', ''),
                                 step.get('proposed_url', '')))
    return out


def _budget_left(run):
    lim = run['configured_limits']
    use = run['observed_usage']
    if use['discovery_calls'] >= lim['max_discovery_calls']:
        return False, 'budget_exhausted'
    if use['document_reads'] >= lim['max_document_reads']:
        return False, 'budget_exhausted'
    if use['rounds'] >= lim['max_rounds']:
        return False, 'budget_exhausted'
    return True, None


def _choose_gap(run):
    gaps = _open_gaps(run)
    if not gaps:
        return None
    return gaps[0]


def _mark_gap(run, gap_id, status, inspected=None):
    for node in run['question_map']:
        if node['id'] == gap_id:
            node['status'] = status
            if inspected:
                node['inspected_evidence_ids'] = list(dict.fromkeys(
                    node.get('inspected_evidence_ids', []) + list(inspected)
                ))
            return node
    raise ValueError('gap not found in question map')


def _synthesize(data, run):
    brief = research.brief(data)
    material = [c for c in brief['claims'] if c['state'] != 'UNRESOLVED'] or brief['claims']
    strongest = None
    falsification = None
    for node in run['question_map']:
        if node['intent'] == 'challenge' or node['status'] == 'open':
            strongest = node['subquestion']
            falsification = node['proposed_search']
            if node['intent'] == 'challenge':
                break
    if not strongest and material:
        strongest = f'Find contrary evidence for: {material[0]["statement"][:200]}'
        falsification = strongest
    contested = [c for c in brief['claims'] if c['state'] == 'CONTESTED']
    supported = [c for c in brief['claims'] if c['state'] == 'SUPPORTED_AS_ASSESSED']
    if contested:
        conclusion = 'Material claims are contested after challenge/investigation.'
    elif supported:
        conclusion = 'Some claims are supported as assessed; contrary evidence may still reverse them.'
    else:
        conclusion = 'No claim is settled; evidence was collected under explicit limits.'
    return {
        'case_version': data['version'],
        'conclusion': conclusion,
        'conditions': [
            'Quote occurrence is verified; entailment is authored.',
            f"Run kind={run['kind']}; stop_reason={run.get('stop_reason')}",
        ],
        'evidence_for': [c['id'] for c in supported],
        'evidence_against': [c['id'] for c in contested],
        'unresolved_gaps': [n['gap'] for n in run['question_map'] if n['status'] == 'open'],
        'strongest_challenge': strongest,
        'falsification_condition': falsification,
        'meaning': 'Synthesis summarizes this run; it is not an automatic scientific verdict.',
    }


def start_research(question, *, root=None, sources=(), live=False, db=None,
                   limits=None, providers=('parallel',), official_domains=(),
                   execute=True, max_steps=None):
    if not isinstance(question, str) or not 1 <= len(question.strip()) <= 1500:
        raise ValueError('question must contain 1–1500 characters')
    data = cases.create(question, root=root, live=live, sources=sources,
                        official_domains=official_domains, db=db)
    run = _new_run(case_id=data['id'], base_version=data['version'], question=question.strip(),
                   kind='investigate', question_map=initial_question_map(question),
                   limits=limits, providers=providers)
    # Seed map with gaps visible in the first evidence pass.
    run['question_map'].extend(gaps_from_evidence(data, run['question_map']))
    run = _save_run(run, db=db)
    if execute:
        run = advance(run['id'], live=live, db=db, max_steps=max_steps)
    return run


def start_challenge(case_id, *, version=None, live=False, db=None, limits=None,
                    providers=('parallel',), execute=True, max_steps=None):
    data = cases.get(case_id, version=version, db=db)
    pinned = {
        'case_version': data['version'],
        'claims': [{'id': c['id'], 'statement': c['statement'], 'state': c['state']}
                   for c in research.brief(data)['claims']],
        'meaning': 'Challenge investigates this pinned answer version; it does not rewrite history.',
    }
    run = _new_run(
        case_id=case_id,
        base_version=data['version'],
        question=data['question'],
        kind='challenge',
        question_map=challenge_question_map(data),
        limits=limits,
        pinned_answer=pinned,
        providers=providers,
    )
    run = _save_run(run, db=db)
    if execute:
        run = advance(run['id'], live=live, db=db, max_steps=max_steps)
    return run


def cancel(run_id, *, db=None):
    run = get_run(run_id, db=db)
    if run['status'] in ('completed', 'cancelled'):
        return run
    run['status'] = 'cancelled'
    run['stop_reason'] = 'cancelled'
    run['steps'].append(_step('cancel', state='completed', outcome='cancelled by operator'))
    return _save_run(run, db=db)


def advance(run_id, *, live=False, db=None, max_steps=None):
    """Execute the adaptive loop until a stop reason or max_steps (interrupt)."""
    run = get_run(run_id, db=db)
    if run['status'] in ('completed', 'cancelled'):
        return run
    if run['status'] == 'planned':
        run['status'] = 'running'
    elif run['status'] == 'paused':
        run['status'] = 'running'
        run['stop_reason'] = None
    steps_this_call = 0
    new_evidence_streak = 0

    while True:
        if max_steps is not None and steps_this_call >= max_steps:
            run['status'] = 'paused'
            run['stop_reason'] = 'max_steps'
            run['steps'].append(_step('interrupt', state='completed',
                                      outcome=f'paused after {steps_this_call} steps; resume preserves evidence'))
            return _save_run(run, db=db)

        ok, reason = _budget_left(run)
        if not ok:
            run['status'] = 'completed'
            run['stop_reason'] = reason
            data = cases.get(run['case_id'], db=db)
            run['answer'] = _synthesize(data, run)
            return _save_run(run, db=db)

        gap = _choose_gap(run)
        if gap is None:
            run['status'] = 'completed'
            run['stop_reason'] = 'evidence_sufficient'
            data = cases.get(run['case_id'], db=db)
            run['answer'] = _synthesize(data, run)
            return _save_run(run, db=db)

        # 1) retrieve locally — never a paid call
        data = cases.get(run['case_id'], db=db)
        run['steps'].append(_step('retrieve_local', state='completed',
                                  resulting_case_version=data['version'],
                                  outcome=f'version {data["version"]} · {len(data["evidence"])} sources',
                                  gap_id=gap['id']))
        steps_this_call += 1
        run['cursor'] = len(run['steps'])
        run = _save_run(run, db=db)
        if max_steps is not None and steps_this_call >= max_steps:
            run['status'] = 'paused'
            run['stop_reason'] = 'max_steps'
            return _save_run(run, db=db)

        # 2) choose next gap (explicit step for the receipt)
        run['steps'].append(_step('choose_gap', state='completed', query=gap['proposed_search'],
                                  url=gap.get('proposed_url', ''),
                                  outcome=f'intent={gap["intent"]} · {gap["gap"]}',
                                  gap_id=gap['id']))
        steps_this_call += 1
        run['cursor'] = len(run['steps'])
        run = _save_run(run, db=db)
        if max_steps is not None and steps_this_call >= max_steps:
            run['status'] = 'paused'
            run['stop_reason'] = 'max_steps'
            return _save_run(run, db=db)

        before_urls = {e['url'] for e in data['evidence']}
        before_count = len(data['evidence'])
        query = gap.get('proposed_url') and '' or gap['proposed_search']
        sources = [gap['proposed_url']] if gap.get('proposed_url') else ()
        providers = run['providers'] if query else ()

        # 3) discover — skip if this exact paid/public query already completed
        discovered_urls = []
        if query:
            for provider in providers:
                fp = _fingerprint(provider, query)
                if fp in _completed_discoveries(run):
                    prior = next(
                        (s for s in reversed(run['steps'])
                         if s['op'] == 'discover' and s['state'] == 'completed'
                         and _fingerprint(s.get('provider', ''), s.get('proposed_query', ''),
                                          s.get('proposed_url', '')) == fp),
                        None,
                    )
                    reused = list(prior.get('response_ref') or []) if prior else []
                    discovered_urls.extend(reused)
                    run['steps'].append(_step(
                        'discover', query=query, provider=provider, state='skipped',
                        response_ref=reused,
                        outcome='already completed; reusing prior candidates; not repeating provider call',
                        gap_id=gap['id'],
                    ))
                    steps_this_call += 1
                    continue
                event = _step('discover', query=query, provider=provider, state='started',
                              gap_id=gap['id'])
                run['steps'].append(event)
                try:
                    if live:
                        results = discovery.find(
                            provider, query, live=True,
                            limit=run['configured_limits']['results_per_provider'],
                        )
                    else:
                        # Offline: local catalog / cache only through Parallel adapter path.
                        results = discovery.find(
                            provider, query, live=False,
                            limit=run['configured_limits']['results_per_provider'],
                        )
                    run['observed_usage']['discovery_calls'] += 1
                    discovered_urls.extend(c.url for c in results)
                    event['state'] = 'completed'
                    event['response_ref'] = [c.url for c in results]
                    event['outcome'] = f'{len(results)} candidates'
                except (RuntimeError, OSError, ValueError) as exc:
                    event['state'] = 'failed'
                    event['outcome'] = type(exc).__name__
                steps_this_call += 1
                run['cursor'] = len(run['steps'])
                run = _save_run(run, db=db)
                if max_steps is not None and steps_this_call >= max_steps:
                    run['status'] = 'paused'
                    run['stop_reason'] = 'max_steps'
                    return _save_run(run, db=db)

        # 4) read originals via investigate — sources only (discovery already recorded above)
        data = cases.get(run['case_id'], db=db)
        read_sources = list(dict.fromkeys(
            list(sources) + [u for u in discovered_urls if u not in before_urls]
        ))
        discovered_this_round = bool(query)
        if not read_sources and query and not live and not discovered_this_round:
            # Offline catalog path only when this gap never entered discovery.
            read_via_query = query
        else:
            read_via_query = ''
        if not read_sources and not read_via_query:
            _mark_gap(run, gap['id'], 'exhausted' if not discovered_urls else 'pursued',
                      inspected=[e['id'] for e in data['evidence'] if e['url'] in set(discovered_urls)])
            run['steps'].append(_step(
                'read', state='skipped',
                outcome='no new source URL after discovery (candidates already present or empty)',
                gap_id=gap['id'],
            ))
            steps_this_call += 1
            run['observed_usage']['rounds'] += 1
            run = _save_run(run, db=db)
            if all(n['status'] != 'open' for n in run['question_map']):
                run['status'] = 'completed'
                run['stop_reason'] = 'missing_access' if not live and not data['evidence'] else 'diminishing_new_evidence'
                run['answer'] = _synthesize(data, run)
                return _save_run(run, db=db)
            continue

        try:
            remaining = run['configured_limits']['max_document_reads'] - run['observed_usage']['document_reads']
            if remaining <= 0:
                run['status'] = 'completed'
                run['stop_reason'] = 'budget_exhausted'
                run['answer'] = _synthesize(data, run)
                return _save_run(run, db=db)
            limited_sources = tuple(read_sources[:remaining])
            new_data = research.investigate(
                run['case_id'], data['version'],
                query=read_via_query,
                sources=limited_sources,
                providers=run['providers'] if read_via_query else ('parallel',),
                live=live,
                limit=min(run['configured_limits']['results_per_provider'], max(1, remaining)),
                db=db,
            )
            added = len(new_data['evidence']) - before_count
            new_ids = [e['id'] for e in new_data['evidence'] if e['url'] not in before_urls]
            run['observed_usage']['document_reads'] += max(len(new_ids), 1 if limited_sources or read_via_query else 0)
            if read_via_query:
                run['observed_usage']['discovery_calls'] += 1
            run['steps'].append(_step(
                'read', query=read_via_query or query,
                url=limited_sources[0] if limited_sources else '',
                state='completed', resulting_case_version=new_data['version'],
                response_ref=new_ids,
                outcome=f'+{added} sources · case v{new_data["version"]}',
                gap_id=gap['id'],
            ))
            data = new_data
            if added:
                new_evidence_streak = 0
            else:
                new_evidence_streak += 1
        except ValueError as exc:
            run['steps'].append(_step('read', query=query, state='failed', outcome=str(exc)[:180],
                                      gap_id=gap['id']))
            _mark_gap(run, gap['id'], 'exhausted')
            steps_this_call += 1
            run['cursor'] = len(run['steps'])
            run['observed_usage']['rounds'] += 1
            run = _save_run(run, db=db)
            continue

        steps_this_call += 1
        run['cursor'] = len(run['steps'])
        run = _save_run(run, db=db)

        # 5) propose assessments when challenge finds contrary quotes
        if run['kind'] == 'challenge':
            data = _maybe_challenge_assess(run, data, gap, db=db)
        run['steps'].append(_step(
            'assess_proposal', state='completed', resulting_case_version=data['version'],
            outcome='challenge assessments applied where exact contrary quotes exist'
            if run['kind'] == 'challenge' else 'assessments left to user/agent; quotes not auto-entailed',
            gap_id=gap['id'],
        ))
        steps_this_call += 1

        # 6) revise map from new evidence
        inspected = [e['id'] for e in data['evidence'] if e['url'] not in before_urls] or [
            e['id'] for e in data['evidence'][-3:]
        ]
        _mark_gap(run, gap['id'], 'pursued' if inspected else 'exhausted', inspected=inspected)
        # pursued gaps that yielded no new URLs become exhausted
        if not any(e['url'] not in before_urls for e in data['evidence']):
            _mark_gap(run, gap['id'], 'exhausted', inspected=inspected)
        added_gaps = gaps_from_evidence(data, run['question_map'])
        # Challenge runs only keep challenge/replication intents from auto-gaps.
        if run['kind'] == 'challenge':
            added_gaps = [g for g in added_gaps if g['intent'] in ('challenge', 'replication', 'citation', 'access')]
        run['question_map'].extend(added_gaps)
        run['steps'].append(_step(
            'revise_map', state='completed', resulting_case_version=data['version'],
            outcome=f'+{len(added_gaps)} gaps · open={len(_open_gaps(run))}',
            gap_id=gap['id'],
        ))
        steps_this_call += 1
        run['observed_usage']['rounds'] += 1
        run['cursor'] = len(run['steps'])
        run = _save_run(run, db=db)

        # 7) decide next
        if new_evidence_streak >= 2:
            run['status'] = 'completed'
            run['stop_reason'] = 'diminishing_new_evidence'
            run['answer'] = _synthesize(data, run)
            run['steps'].append(_step('decide_next', state='completed',
                                      outcome='stop: diminishing new evidence'))
            return _save_run(run, db=db)
        if not _open_gaps(run):
            run['status'] = 'completed'
            run['stop_reason'] = 'evidence_sufficient'
            run['answer'] = _synthesize(data, run)
            run['steps'].append(_step('decide_next', state='completed',
                                      outcome='stop: no open gaps'))
            return _save_run(run, db=db)
        run['steps'].append(_step('decide_next', state='completed',
                                  outcome=f'continue · next open gaps={len(_open_gaps(run))}'))
        steps_this_call += 1
        run = _save_run(run, db=db)

        # Missing access offline with no cached docs and no new evidence
        if not live and not any(e.get('snapshot_text') for e in data['evidence']):
            unavailable = all(e.get('status') == 'UNAVAILABLE' for e in data['evidence']) if data['evidence'] else True
            if unavailable and run['observed_usage']['rounds'] >= 1:
                run['status'] = 'completed'
                run['stop_reason'] = 'missing_access'
                run['answer'] = _synthesize(data, run)
                return _save_run(run, db=db)


def _maybe_challenge_assess(run, data, gap, *, db):
    """If a new snapshot contains an explicit contrary cue, record a contradicts assessment."""
    target_claim = gap.get('target_claim_id')
    claims = {c['id']: c for c in data.get('claims', [])}
    claim = claims.get(target_claim)
    if claim is None and data.get('claims'):
        # Fall back to first supported/authored claim when map had a generic challenge node.
        brief = research.brief(data)
        claim = next((c for c in brief['claims'] if c['state'] == 'SUPPORTED_AS_ASSESSED'), None)
        if claim is None:
            claim = brief['claims'][0] if brief['claims'] else None
            if claim:
                claim = next((c for c in data['claims'] if c['id'] == claim['id']), None)
        else:
            claim = next((c for c in data['claims'] if c['id'] == claim['id']), None)
    if not claim:
        # Author a claim from the pinned statement so challenge can attach.
        statement = (run.get('pinned_answer') or {}).get('claims', [{}])
        statement = statement[0].get('statement') if statement else run['question']
        if not statement:
            return data
        try:
            return research.assess(
                data['id'], data['version'], statement=statement, relation='unresolved',
                rationale='Challenge run pinned this claim for overturn investigation.',
                db=db,
            )
        except ValueError:
            return data

    contrary = re.compile(r'\b(increas\w+|worsen\w+|fail\w+|not (?:help|improve)|no (?:benefit|effect)|harm\w+|contradict\w+)\b', re.I)
    for e in data['evidence']:
        text = e.get('snapshot_text') or ''
        quote = e.get('quote') or ''
        candidate = quote if contrary.search(quote or '') else None
        if not candidate:
            for span in re.split(r'(?<=[.!?])\s+', text):
                span = span.strip()
                if 20 <= len(span) <= 400 and contrary.search(span) and span in text:
                    candidate = span
                    break
        if not candidate or e.get('status') != 'QUOTE_VERIFIED' and candidate not in text:
            if candidate and candidate in text:
                pass
            else:
                continue
        # Avoid duplicate contradicts on same evidence.
        if any(a.get('anchor', {}).get('evidence_id') == e['id'] and a['relation'] == 'contradicts'
               for a in claim.get('assessments', [])):
            continue
        try:
            data = research.assess(
                data['id'], data['version'], claim_id=claim['id'], statement=None,
                relation='contradicts',
                rationale='Challenge investigation found a passage that conflicts with the pinned claim direction.',
                evidence_id=e['id'], quote=candidate, db=db,
            )
            claim = next(c for c in data['claims'] if c['id'] == claim['id'])
        except ValueError:
            continue
    return data


def resume(run_id, *, live=False, db=None, max_steps=None):
    run = get_run(run_id, db=db)
    if run['status'] == 'cancelled':
        raise ValueError('cancelled runs cannot resume; start a new challenge or research run')
    if run['status'] == 'completed':
        return run
    return advance(run_id, live=live, db=db, max_steps=max_steps)


def public_run(run):
    """Compact tool/CLI view — full step list retained; no private repo file bodies."""
    return copy.deepcopy(run)


def render_run(run):
    lines = [
        f"Research run {run['id']} · {run['kind']} · {run['status']}",
        f"Case {run['case_id']} · base version {run['base_case_version']}",
        run['question'],
        f"Stop: {run.get('stop_reason') or '—'} · cursor {run.get('cursor', 0)}",
        f"Usage: discovery={run['observed_usage']['discovery_calls']} "
        f"reads={run['observed_usage']['document_reads']} "
        f"rounds={run['observed_usage']['rounds']} cost={run['observed_usage']['cost']}",
        '',
        'Question map:',
    ]
    for n in run['question_map']:
        lines.append(f"  [{n['status']}/{n['intent']}/{n['importance']}] {n['id']}")
        lines.append(f"    {n['subquestion']}")
        lines.append(f"    search: {n['proposed_search']}")
        if n.get('gap'):
            lines.append(f"    gap: {n['gap']}")
    lines.append('')
    lines.append('Steps:')
    for s in run['steps']:
        lines.append(
            f"  {s['op']} · {s['state']}"
            + (f" · {s['proposed_query'][:80]}" if s.get('proposed_query') else '')
            + (f" · {s['outcome']}" if s.get('outcome') else '')
        )
    if run.get('answer'):
        a = run['answer']
        lines += ['', 'Answer:', a['conclusion'],
                  f"Strongest challenge: {a.get('strongest_challenge')}",
                  f"Falsification: {a.get('falsification_condition')}"]
        if a.get('unresolved_gaps'):
            lines.append('Unresolved:')
            for g in a['unresolved_gaps'][:8]:
                lines.append(f"  - {g}")
    lines += [''] + run.get('limits_note', [])
    return '\n'.join(lines) + '\n'


def naive_fixed_search_arm(question, *, sources=(), db=None, live=False):
    """Baseline arm any competent team ships in two hours: fixed three-angle create.

    Used to compare against the adaptive challenge loop. Winning against this is
    required for an ambitious claim; losing to it is a finding.
    """
    return cases.create(question, sources=sources, live=live, db=db)
