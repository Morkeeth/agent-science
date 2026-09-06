"""A local return visit: saved questions, changed claims, and their exact source passages."""
from contextlib import closing
import shlex

from clearance import cases, case_review, research, research_workflow, source_reviews

BASIS = 'Saved evidence only. No web check performed. Interpretations are authored, not proven entailment.'


def save(case_id, *, version=None, db=None):
    data = cases.get(case_id, version=version, db=db)
    with closing(research_workflow._connect(db)) as con, con:
        if version is None:
            con.execute('INSERT OR IGNORE INTO night_follows VALUES(?,?,?)',
                        (case_id, data['version'], cases.now()))
        else:
            # Acknowledges only the inspected version, never a newer concurrent revision.
            con.execute('INSERT INTO night_follows VALUES(?,?,?) ON CONFLICT(case_id) DO UPDATE SET '
                        'version=excluded.version,followed_at=excluded.followed_at '
                        'WHERE night_follows.version<=excluded.version', (case_id, version, cases.now()))
        saved = dict(con.execute('SELECT * FROM night_follows WHERE case_id=?', (case_id,)).fetchone())
    return {'object_type': 'investigation_saved', **saved, 'basis': BASIS}


def desk(*, query='', offset=0, db=None):
    result = case_review.index(query=query, offset=offset, limit=20, db=db)
    with closing(research_workflow._connect(db)) as con:
        follows = {row['case_id']: row['version'] for row in con.execute('SELECT * FROM night_follows')}
    for row in result['cases']:
        row['seen_version'] = follows.get(row['id'])
        row['unseen_versions'] = row['version'] - row['seen_version'] if row['seen_version'] is not None else None
    return {'object_type': 'investigation_desk', **result, 'query': query, 'basis': BASIS}


def _passage(data, anchor):
    source = next((e for e in data['evidence'] if e['id'] == anchor.get('evidence_id')), {})
    text = source.get('snapshot_text')
    quote = anchor.get('quote', '')
    intact = isinstance(text, str) and cases.digest(text) == source.get('snapshot_hash')
    offset = text.find(quote) if intact and quote else -1
    start = max(0, offset - 120) if offset >= 0 else 0
    return {'evidence_id': anchor.get('evidence_id'), 'url': source.get('url', anchor.get('url')),
            'version': data['version'], 'snapshot_hash': source.get('snapshot_hash'),
            'matches_anchor': intact and source.get('snapshot_hash') == anchor.get('snapshot_hash') and offset >= 0,
            'quote_present': offset >= 0, 'status': source.get('status', 'MISSING'),
            'offset': start, 'quote_offset': offset if offset >= 0 else None,
            'excerpt': text[start:min(len(text), offset + len(quote) + 120)] if offset >= 0 else None,
            'warnings': source_reviews.effective_source(data, source).get('metadata_review_required', []) if source else [],
            'retracted': source.get('retracted', False), 'superseded_by': source.get('superseded_by')}


def open_case(case_id, *, claim_id=None, version=None, db=None):
    data = cases.get(case_id, version=version, db=db)
    brief = research.brief(data)
    with closing(research_workflow._connect(db)) as con:
        row = con.execute('SELECT version FROM night_follows WHERE case_id=?', (case_id,)).fetchone()
    seen = row['version'] if row else None
    previous = research.brief(cases.get(case_id, version=seen, db=db)) if seen and seen <= data['version'] else None
    old = {c['id']: c for c in (previous or {}).get('claims', [])}
    cards = []
    for claim in brief['claims']:
        if claim_id and claim['id'] != claim_id:
            continue
        card = {'id': claim['id'], 'statement': claim['statement'], 'state': claim['state'],
                'changed_since_seen': previous is not None and old.get(claim['id']) != claim,
                'assessments': []}
        for assessment in claim['assessments']:
            anchors = [('claim', assessment.get('anchor', {}))] + [
                ('scope: ' + c.get('field', 'condition'), c.get('anchor', {})) for c in assessment.get('conditions', [])]
            passages = []
            for role, anchor in anchors:
                if not anchor:
                    continue
                origin_version = assessment['evidence_version']
                origin = cases.get(case_id, version=origin_version, db=db)
                passages.append({'role': role, 'quote': anchor.get('quote'),
                                 'original': _passage(origin, anchor), 'current': _passage(data, anchor)})
            card['assessments'].append({'id': assessment['id'], 'relation': assessment['relation'],
                'state': assessment['state'], 'rationale': assessment['rationale'], 'passages': passages,
                'source_reviews': assessment.get('source_reviews', [])})
        cards.append(card)
    if claim_id and not cards:
        raise ValueError('claim not found in this case version')
    # Opening never advances the cursor or clears an unresolved correction.
    return {'object_type': 'investigation_open', 'case_id': case_id, 'version': data['version'],
            'question': data['question'], 'seen_version': seen, 'claims': cards, 'focused_claim': claim_id,
            'unread_citations': brief['unread_report_citations'], 'source_count': len(data['evidence']),
            'basis': BASIS}


def render(result, *, db=None):
    suffix = ' --db ' + shlex.quote(str(db)) if db is not None else ''
    command = 'agent-science research '
    kind = result['object_type']
    if kind == 'investigation_saved':
        return f"Saved for return · {result['case_id']} · seen through v{result['version']}\n" + BASIS
    if kind == 'investigation_desk':
        lines = ['YOUR INVESTIGATIONS', BASIS, '']
        for row in result['cases']:
            state = 'not saved for return' if row['seen_version'] is None else (
                f"{row['unseen_versions']} unseen versions" if row['unseen_versions'] else 'no unseen saved versions')
            lines += [row['question'], f"  {row['id']} · v{row['version']} · {state}",
                      f"  {row['claim_review_required']} claims need review · {row['evidence_count']} sources",
                      '  Open: ' + command + 'open ' + shlex.quote(row['id']) + suffix, '']
        if not result['cases']:
            lines += ['No matching saved investigations.', 'Start: agent-science research start "Your research question"' + suffix]
        if result['has_more']:
            lines.append('Next page: ' + command + f"desk --offset {result['next_offset']} --query " + shlex.quote(result['query']) + suffix)
        return '\n'.join(lines)
    cid = shlex.quote(result['case_id']); version = result['version']
    lines = [result['question'], f"Investigation {result['case_id']} · v{version} · seen through " +
             (f"v{result['seen_version']}" if result['seen_version'] is not None else 'not saved'), BASIS, '']
    for claim in result['claims']:
        lines += [('CHANGED · ' if claim['changed_since_seen'] else '') + '[' + claim['state'] + '] ' + claim['statement'],
                  'Open claim: ' + command + 'open ' + cid + ' --claim ' + shlex.quote(claim['id']) + f' --version {version}' + suffix]
        if not result.get('focused_claim'):
            lines.append('')
            continue
        for assessment in claim['assessments']:
            lines.append(f"  {assessment['relation']} · {assessment['state']} — {assessment['rationale']}")
            if not assessment['passages']:
                lines.append('  No source passage attached. This is unresolved reasoning, not sourced support.')
            for passage in assessment['passages']:
                before, current = passage['original'], passage['current']
                lines += ['  ' + passage['role'] + ': ' + str(before['url']),
                          '  QUOTED: ' + str(passage['quote']),
                          '  ORIGINAL v' + str(before['version']) + ': ' + (before['excerpt'] if before['matches_anchor'] else 'Original binding unavailable; do not treat the quotation as verified.')]
                status = ('same saved passage' if current['matches_anchor'] else
                          'source changed; quotation still occurs' if current['quote_present'] else 'quoted passage unavailable in current source')
                lines.append(f"  NOW v{version}: {status} · {current['status']}")
                if current['warnings'] or current['retracted'] or current['superseded_by']:
                    lines.append('  SOURCE NOTICE: inspect correction/withdrawal before relying on this claim.')
                if current['status'] != 'MISSING':
                    lines.append('  Inspect current source: agent-science case source ' + cid + ' --evidence ' +
                        shlex.quote(current['evidence_id']) + f" --version {version} --offset {current['offset']}" + suffix)
                if before['matches_anchor']:
                    lines.append('  Inspect full original: agent-science case source ' + cid + ' --evidence ' +
                        shlex.quote(before['evidence_id']) + f" --version {before['version']} --offset {before['offset']}" + suffix)
        lines.append('')
    if not result['claims']:
        lines.append('Inspect saved sources: agent-science case show ' + cid + f' --version {version}' + suffix)
        lines += ['No assessed claims yet. Sources and a saved question alone do not establish an answer.',
                  command + 'start ' + shlex.quote(result['question']) + ' --case-id ' + cid + suffix]
    if result['unread_citations']:
        lines.append(f"Unread cited sources: {len(result['unread_citations'])}")
    lines += ['Save without clearing unseen changes: ' + command + 'save ' + cid + suffix,
              'After inspecting this version: ' + command + 'seen ' + cid + f' --version {version}' + suffix,
              'Inspect source notices: ' + command + 'source-reviews ' + cid + suffix,
              'Research changed evidence: ' + command + 'update ' + cid + suffix]
    return '\n'.join(lines)
