"""Authored, source-anchored conclusions over immutable case revisions.

Controls establish occurrence and provenance, never semantic entailment.
"""
import copy
import json
import re
import uuid
from contextlib import closing
from clearance import cases, research, studies

RELATIONS = {'supports', 'contradicts', 'context', 'unresolved', 'different_scope'}
MEANING = 'Authored interpretation. Exact quote occurrence is checked; entailment is not mechanically established.'


def _text(value, name, minimum=1):
    if not isinstance(value, str) or not minimum <= len(value.strip()) <= 5000:
        raise ValueError(f'{name} needs {minimum}–5000 characters')
    return value.strip()


def _anchor(data, item):
    evidence = next((e for e in data['evidence'] if e['id'] == item.get('evidence_id')), None)
    quote = item.get('quote')
    if (not evidence or evidence.get('status') == 'UNAVAILABLE' or evidence.get('retracted') or evidence.get('superseded_by') or not evidence.get('snapshot_hash')
            or not isinstance(quote, str) or not 20 <= len(quote) <= 4000
            or quote not in evidence.get('snapshot_text', '')):
        raise ValueError('anchor requires an available source and exact 20–4000 character snapshot quote')
    return {'evidence_id':evidence['id'], 'quote':quote, 'snapshot_hash':evidence['snapshot_hash'], 'url':evidence['url']}


def _finding(data, finding, version):
    if not isinstance(finding, dict): raise ValueError('finding must be an object')
    statement = _text(finding.get('statement'), 'statement')
    relation = finding.get('relation')
    if relation not in RELATIONS: raise ValueError('invalid finding relation')
    rationale = _text(finding.get('rationale'), 'rationale')
    challenge = finding.get('strongest_challenge', '')
    reversal = finding.get('what_would_change', '')
    if relation != 'unresolved':
        challenge = _text(challenge, 'strongest_challenge', 20)
        reversal = _text(reversal, 'what_would_change', 20)
    anchor = _anchor(data, finding) if relation != 'unresolved' or finding.get('evidence_id') or finding.get('quote') else {}
    conditions = finding.get('conditions', [])
    if not isinstance(conditions, list): raise ValueError('conditions must be a list')
    checked = []
    for condition in conditions:
        if not isinstance(condition, dict) or condition.get('field') not in studies.FIELDS:
            raise ValueError('invalid condition field')
        value = _text(condition.get('value'), 'condition value')
        condition_anchor = _anchor(data, condition)
        # Conditions are extracted text, not a free paraphrase presented as fact.
        if value not in condition_anchor['quote']:
            raise ValueError('condition value must occur verbatim in its anchored quote')
        checked.append({'field':condition['field'], 'value':value, 'anchor':condition_anchor, 'evidence_version':version})
    # This narrow guard rejects invented numeric results; it does not prove a result.
    if relation != 'unresolved':
        numbers = re.findall(r'(?<![\w])\d+(?:\.\d+)?%?', statement)
        source_numbers = set(re.findall(r'(?<![\w])\d+(?:\.\d+)?%?', anchor['quote']))
        if relation == 'supports' and any(n not in source_numbers for n in numbers):
            raise ValueError('numerical assertion missing from its source quote; leave unresolved')
        designs = ' '.join(c['value'].lower() for c in checked if c['field'] == 'study_design')
        if ('qualitative' in designs or 'interview' in designs) and re.search(r'\b(causes?|causal|increases?|improves?|reduces?)\b', statement, re.I):
            raise ValueError('qualitative study cannot establish causal effectiveness; leave unresolved')
    category = finding.get('category', 'unclassified')
    if category not in ('empirical_findings', 'official_constraints', 'field_adoption', 'unclassified'):
        raise ValueError('invalid finding category; local measurements must come from actual experiments')
    assessment = {'category':category, 'id':uuid.uuid4().hex[:12], 'relation':'context' if relation == 'different_scope' else relation,
        'scope_relationship':relation, 'rationale':rationale, 'anchor':anchor,
        'conditions':checked, 'strongest_challenge':challenge, 'what_would_change':reversal,
        'evidence_version':version, 'supersedes':None, 'at':cases.now(), 'authorship':'user_or_agent', 'meaning':MEANING}
    return statement, assessment


def apply(case_id, version, proposal, *, db=None):
    """Validate all findings before a single locked revision write."""
    if not isinstance(proposal, dict) or not isinstance(proposal.get('findings'), list) or not proposal['findings']:
        raise ValueError('proposal requires a nonempty findings list')
    if len(proposal['findings']) > 100: raise ValueError('at most 100 findings per proposal')
    if 'case_version' in proposal and proposal['case_version'] != version: raise ValueError('proposal version mismatch')
    with closing(cases.connect(db)) as con, con:
        con.execute('BEGIN IMMEDIATE')
        row = con.execute('SELECT body FROM revisions WHERE case_id=? ORDER BY version DESC LIMIT 1', (case_id,)).fetchone()
        if row is None: raise ValueError('case not found')
        data = json.loads(row['body'])
        if type(version) is not int or version != data['version']:
            raise ValueError('case version changed; inspect the latest version before writing')
        prepared = [_finding(data, f, version) for f in proposal['findings']]
        claims = data.setdefault('claims', [])
        for finding, (statement, assessment) in zip(proposal['findings'], prepared):
            claim_id = finding.get('claim_id')
            claim = next((c for c in claims if c['id'] == claim_id), None) if claim_id else next((c for c in claims if c['statement'] == statement), None)
            if claim_id and (claim is None or claim['statement'] != statement):
                raise ValueError('claim_id must identify the same statement in this case')
            if claim is None:
                claim = {'id':uuid.uuid4().hex[:12], 'statement':statement, 'source_urls':[], 'origin':'authored', 'assessments':[]}
                claims.append(claim)
            supersedes = finding.get('supersedes')
            if supersedes:
                superseded = {a.get('supersedes') for a in claim['assessments']}
                if not any(a['id'] == supersedes for a in claim['assessments']) or supersedes in superseded:
                    raise ValueError('supersedes must identify an active assessment on this claim')
                assessment['supersedes'] = supersedes
            claim['assessments'].append(assessment)
            if assessment['anchor'] and assessment['anchor']['url'] not in claim['source_urls']:
                claim['source_urls'].append(assessment['anchor']['url'])
        data.update(version=version + 1, changes=[{'kind':'interpretation_added', 'count':len(prepared)}])
        # Interpretation does not advance the last source check clock.
        data['synthesis_authored_at'] = cases.now()
        con.execute('INSERT INTO revisions VALUES(?,?,?)', (case_id, version + 1, json.dumps(data)))
    return cases.get(case_id, version=version + 1, db=db)


def build(case_data):
    brief = research.brief(case_data)
    grouped = studies.group(case_data['evidence'])
    by_evidence = {eid:s for s in grouped for eid in s['evidence_ids']}
    evidence = {e['id']:e for e in case_data['evidence']}
    conclusions = []; gaps = []
    for claim in brief['claims']:
        for assessment in claim['assessments']:
            if assessment['state'] == 'SUPERSEDED': continue
            conditions = copy.deepcopy(assessment.get('conditions', []))
            stale_condition = False
            for condition in conditions:
                anchor = condition['anchor']; source = evidence.get(anchor['evidence_id'], {})
                current = source.get('snapshot_hash') == anchor['snapshot_hash'] and source.get('status') != 'UNAVAILABLE' and not source.get('retracted') and not source.get('superseded_by')
                condition['state'] = 'CURRENT' if current else 'REVIEW_REQUIRED'
                stale_condition |= not current
                if current and anchor['evidence_id'] in by_evidence:
                    by_evidence[anchor['evidence_id']]['conditions'][condition['field']].append(condition)
            state = 'REVIEW_REQUIRED' if stale_condition else assessment['state']
            anchor = assessment['anchor']; source = evidence.get(anchor.get('evidence_id'), {})
            if source.get('retracted') or source.get('superseded_by'):
                state = 'REVIEW_REQUIRED'
            category = assessment.get('category', 'unclassified')
            conclusion = {'claim_id':claim['id'], 'assessment_id':assessment['id'], 'statement':claim['statement'],
                'relation':assessment.get('scope_relationship', assessment['relation']), 'state':state,
                'claim_state':'REVIEW_REQUIRED' if state == 'REVIEW_REQUIRED' else claim['state'],
                'competing_interpretations':[{'assessment_id':other['id'], 'relation':other.get('scope_relationship', other['relation']),
                    'rationale':other['rationale'], 'anchor':other['anchor']} for other in claim['assessments']
                    if other['id'] != assessment['id'] and other['state'] != 'SUPERSEDED'],
                'category':category, 'rationale':assessment['rationale'], 'anchor':anchor, 'conditions':conditions,
                'strongest_challenge':assessment.get('strongest_challenge'), 'what_would_change':assessment.get('what_would_change'),
                'authorship':assessment['authorship'], 'meaning':MEANING, 'evidence_version':assessment['evidence_version']}
            conclusions.append(conclusion)
            if state != 'CURRENT' or assessment['relation'] == 'unresolved': gaps.append({'claim_id':claim['id'], 'reason':state if state != 'CURRENT' else 'unresolved'})
            if not conclusion['strongest_challenge'] or not conclusion['what_would_change']:
                gaps.append({'claim_id':claim['id'], 'reason':'missing challenge or falsification condition'})
        if not claim['assessments']: gaps.append({'claim_id':claim['id'], 'reason':'unassessed'})
    gaps += [{'url':u, 'reason':'unread citation'} for u in brief['unread_report_citations']]
    gaps += [{'evidence_id':e['id'], 'reason':'source unavailable'} for e in evidence.values() if e.get('status') == 'UNAVAILABLE']
    return {'case_id':case_data['id'], 'version':case_data['version'], 'question':case_data['question'],
        'conclusions':conclusions, 'studies':grouped, 'gaps':gaps,
        'local_measurements':[cases.experiment_summary(e) for e in case_data.get('experiments', [])],
        'limits':brief['limits'] + ['Conditions absent from source anchors remain unknown.',
            'Source classification and interpretations are authored; numeric occurrence is not numerical validity.']}


def compare(case_id, from_version, *, db=None):
    old = cases.get(case_id, version=from_version, db=db); new = cases.get(case_id, db=db)
    before = {e['id']:e for e in old['evidence']}; after = {e['id']:e for e in new['evidence']}
    changes = cases.changes(old, new)
    for eid in before.keys() & after.keys():
        if before[eid].get('status') == 'UNAVAILABLE' and after[eid].get('status') != 'UNAVAILABLE':
            changes = [event for event in changes if event.get('evidence_id') != eid]
            changes.append({'kind':'source_newly_available', 'evidence_id':eid, 'url':after[eid]['url']})
        for field in ('retracted', 'superseded_by'):
            if before[eid].get(field) != after[eid].get(field):
                changes.append({'kind':'source_metadata_changed', 'field':field, 'evidence_id':eid,
                    'before':before[eid].get(field), 'after':after[eid].get(field)})
    old_answer = build(old); answer = build(new)
    old_rows = {c['assessment_id']:c for c in old_answer['conclusions']}
    new_rows = {c['assessment_id']:c for c in answer['conclusions']}
    reasoning = [{'kind':'interpretation_added', 'after':c} for key,c in new_rows.items() if key not in old_rows]
    reasoning += [{'kind':'interpretation_removed', 'before':c} for key,c in old_rows.items() if key not in new_rows]
    reasoning += [{'kind':'interpretation_changed', 'before':old_rows[key], 'after':c} for key,c in new_rows.items() if key in old_rows and c != old_rows[key]]
    touched_evidence = {event.get('evidence_id') for event in changes}
    affected_claims = sorted({c['claim_id'] for c in old_answer['conclusions'] + answer['conclusions']
        if c['anchor'].get('evidence_id') in touched_evidence
        or any(condition['anchor']['evidence_id'] in touched_evidence for condition in c['conditions'])}
        | {event[side]['claim_id'] for event in reasoning for side in ('before', 'after') if side in event})
    affected_evidence = touched_evidence | {c['anchor'].get('evidence_id')
        for c in old_answer['conclusions'] + answer['conclusions'] if c['claim_id'] in affected_claims}
    affected_decisions = []
    for decision in new['decisions']:
        if decision.get('superseded_by'): continue
        if decision.get('review', {}).get('state') == 'REVIEW_REQUIRED' or affected_evidence.intersection(decision['evidence_ids']):
            affected_decisions.append({**decision, 'review':{'state':'REVIEW_REQUIRED',
                'changes':changes, 'affected_claim_ids':affected_claims,
                'meaning':'Cited evidence or an interpretation using it changed. Authored decision review is required.'}})
    return {'case_id':case_id, 'from_version':old['version'], 'version':new['version'],
        'evidence_changes':changes, 'reasoning_changes':reasoning, 'changed':bool(changes or reasoning),
        'material_change':bool(affected_claims or affected_decisions), 'affected_claim_ids':affected_claims,
        'affected_decisions':affected_decisions, 'affected_decision_ids':[d['id'] for d in affected_decisions],
        'before':old_answer, 'after':answer, 'meaning':'Comparison of saved versions; no source was checked online.'}
