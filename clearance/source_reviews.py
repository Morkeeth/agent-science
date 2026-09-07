"""Assessment-scoped authored review of inspected correction notices.

Registry facts remain untouched. An acknowledgment is not semantic proof and
cannot rehabilitate retracted or superseded source material.
"""
from contextlib import closing
import hashlib
import json
import uuid

from clearance import cases, studies

MEANING = 'Authored correction interpretation; exact quote and identity are checked, not semantic entailment.'


def _hash(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def _warnings(source):
    warnings = source.get('metadata_review_required') or []
    if not isinstance(warnings, list):
        return [{'type':'unrecognized_warning_format', 'raw':warnings}]
    return sorted(warnings, key=lambda value: json.dumps(value, sort_keys=True))



NON_REHABILITABLE = {'retraction', 'partial-retraction', 'withdrawal', 'withdrawn', 'removal', 'removed', 'new-version'}


def effective_source(data, source):
    """Derive warnings across exact identifiers; never merge by prose/title.

    DOI notices apply to that DOI's mirrors. Version-specific arXiv notices only
    apply to their explicit target version, never the current/newer version.
    """
    identities, versions, _ = studies._identities(source)
    warnings = list(_warnings(source))
    inherited = set()
    for sibling in data.get('evidence', []):
        if sibling.get('id') == source.get('id'):
            continue
        sibling_ids, sibling_versions, _ = studies._identities(sibling)
        for warning in _warnings(sibling):
            if not isinstance(warning, dict):
                continue
            target = warning.get('target')
            if target not in identities:
                continue
            if target.startswith('arxiv:'):
                target_version = warning.get('target_version')
                if target_version:
                    if target_version not in versions:
                        continue
                elif not (versions and versions == sibling_versions):
                    continue
            warnings.append(warning); inherited.add(sibling['id'])
        # Older imported records may retain a retraction flag without its notice.
        common = identities & sibling_ids
        exact = any(i.startswith('doi:') for i in common) or (bool(common) and bool(versions) and versions == sibling_versions)
        if exact and sibling.get('retracted'):
            warnings.append({'type':'retraction', 'target':sorted(common)[0], 'notice':None, 'basis':'saved study retraction flag'})
            inherited.add(sibling['id'])
        if common and versions and versions == sibling_versions and sibling.get('superseded_by'):
            warnings.append({'type':'new-version', 'target':sorted(common)[0], 'target_version':sorted(versions)[0],
                             'notice':sibling['superseded_by'], 'basis':'saved version supersession flag'})
            inherited.add(sibling['id'])
    unique = {json.dumps(w, sort_keys=True):w for w in warnings}
    result = dict(source)
    if unique:
        result['metadata_review_required'] = [unique[key] for key in sorted(unique)]
    result['warning_inherited_from'] = sorted(inherited)
    return result


def _non_rehabilitable(source):
    return sorted({str(w.get('type', '')).lower().replace('_', '-') for w in _warnings(source)
                   if isinstance(w, dict) and str(w.get('type', '')).lower().replace('_', '-') in NON_REHABILITABLE})

def _assessment_hash(data, assessment):
    claim = next((c for c in data.get('claims', []) if any(a['id'] == assessment['id'] for a in c['assessments'])), {})
    # Derived presentation fields must not alter the committed assessment binding.
    raw = next((a for a in claim.get('assessments', []) if a['id'] == assessment['id']), assessment)
    raw = {k:v for k,v in raw.items() if k not in ('state', 'source_reviews')}
    return _hash({'statement':claim.get('statement'), 'assessment':raw})


def _available(source):
    text = source.get('snapshot_text')
    return (source.get('status') != 'UNAVAILABLE' and isinstance(text, str) and bool(text)
            and source.get('snapshot_hash') == cases.digest(text)
            and not source.get('retracted') and not source.get('superseded_by') and not _non_rehabilitable(source))


def _notice_failure(data, notice):
    """Return a stable actionable failure code, or None for this exact anchor."""
    source = next((e for e in data.get('evidence', []) if e['id'] == notice['evidence_id']), None)
    if source is None:
        return 'notice_evidence_missing'
    source = effective_source(data, source)
    identities, versions, _ = studies._identities(source)
    for prefix in ('doi:', 'arxiv:'):
        if len([identity for identity in identities if identity.startswith(prefix)]) > 1:
            return 'notice_identity_ambiguous'
    if notice['notice_identity'].startswith('arxiv:') and len(versions) > 1:
        return 'notice_version_ambiguous'
    if notice['notice_identity'] not in identities | versions:
        return 'notice_identity_mismatch'
    if source.get('status') == 'UNAVAILABLE' or not source.get('snapshot_text'):
        return 'notice_unavailable'
    if source.get('retracted'):
        return 'notice_retracted'
    if source.get('superseded_by'):
        return 'notice_superseded'
    if source.get('metadata_review_required'):
        return 'notice_needs_review'
    text = source.get('snapshot_text')
    if not isinstance(text, str) or source.get('snapshot_hash') != cases.digest(text):
        return 'notice_body_hash_mismatch'
    if source['snapshot_hash'] != notice['snapshot_hash']:
        return 'notice_snapshot_stale'
    quote = notice.get('quote')
    if not isinstance(quote, str) or not 20 <= len(quote) <= 4000:
        return 'notice_quote_length_invalid'
    if quote not in text:
        return 'notice_quote_absent'
    return None


def _notice_current(data, notice):
    return _notice_failure(data, notice) is None


def assessment_status(data, assessment):
    """Stable semantic rows used by brief, synthesis and decision review."""
    sources = {e['id']:effective_source(data, e) for e in data.get('evidence', [])}
    anchors = [assessment.get('anchor', {})] + [c.get('anchor', {}) for c in assessment.get('conditions', [])]
    rows = []
    for evidence_id in sorted({a['evidence_id'] for a in anchors if a.get('evidence_id')}):
        source = sources.get(evidence_id, {})
        warnings = _warnings(source)
        if not warnings:
            continue
        fingerprint = _hash(warnings)
        reviews = [r for r in data.get('source_reviews', []) if r['assessment_id'] == assessment['id'] and r['evidence_id'] == evidence_id]
        # The latest authored disposition governs even when an older body or
        # warning fingerprint returns. History is not a fallback resolution.
        latest = reviews[-1] if reviews else None
        binding_current = (latest is not None and latest['warning_fingerprint'] == fingerprint
                           and latest['source_snapshot_hash'] == source.get('snapshot_hash')
                           and latest['assessment_fingerprint'] == _assessment_hash(data, assessment))
        expected_notices = {w.get('notice') for w in warnings if isinstance(w, dict) and isinstance(w.get('notice'), str)}
        resolved = (binding_current and latest['disposition'] == 'unaffected' and _available(source)
                    and bool(expected_notices) and {n['notice_identity'] for n in latest['notices']} == expected_notices
                    and len({n['evidence_id'] for n in latest['notices']}) == len(latest['notices'])
                    and all(isinstance(w, dict) and w.get('notice') in expected_notices for w in warnings)
                    and all(a.get('snapshot_hash') == source.get('snapshot_hash') for a in anchors if a.get('evidence_id') == evidence_id)
                    and all(_notice_current(data, n) for n in latest['notices']))
        rows.append({'assessment_id':assessment['id'], 'evidence_id':evidence_id,
            'source_snapshot_hash':source.get('snapshot_hash'), 'warning_fingerprint':fingerprint,
            'warnings':warnings, 'warning_inherited_from':source.get('warning_inherited_from', []), 'non_rehabilitable':_non_rehabilitable(source), 'notice_identities':sorted({w.get('notice') for w in warnings if isinstance(w, dict) and w.get('notice')}),
            'state':'RESOLVED_AS_AUTHORED' if resolved else 'REVIEW_REQUIRED',
            'review_binding_current':binding_current,
            'notice_failures':[{'notice_identity':n['notice_identity'], 'evidence_id':n['evidence_id'], 'reason':failure}
                for n in (latest['notices'] if latest else []) if (failure := _notice_failure(data, n))],
            'review':({k:v for k,v in latest.items() if k not in ('id','case_version','recorded_version','at')} if latest else None), 'meaning':MEANING})
    return rows


def list_pending(case_id, *, db=None, version=None):
    data = cases.get(case_id, db=db, version=version)
    rows = []
    for claim in data.get('claims', []):
        superseded = {a.get('supersedes') for a in claim['assessments']}
        for assessment in claim['assessments']:
            if assessment['id'] in superseded:
                continue
            rows += [dict(row, claim_id=claim['id'], statement=claim['statement']) for row in assessment_status(data, assessment)]
    return {'object_type':'source_reviews', 'case_id':case_id, 'version':data['version'],
            'pending':[row for row in rows if row['state'] == 'REVIEW_REQUIRED'],
            'resolved':[row for row in rows if row['state'] == 'RESOLVED_AS_AUTHORED'],
            'reviews':data.get('source_reviews', []), 'meaning':MEANING}


def review(case_id, version, proposal, *, db=None):
    required = {'assessment_id', 'evidence_id', 'source_snapshot_hash', 'warning_fingerprint', 'notices', 'rationale', 'disposition'}
    if not isinstance(proposal, dict) or set(proposal) != required:
        raise ValueError('source review requires exact fields: ' + ', '.join(sorted(required)))
    if not isinstance(proposal['disposition'], str) or proposal['disposition'] not in ('unaffected', 'revise', 'unresolved'):
        raise ValueError('disposition must be unaffected, revise or unresolved')
    for field in ('assessment_id', 'evidence_id', 'warning_fingerprint'):
        if not isinstance(proposal[field], str) or not proposal[field]:
            raise ValueError(field + ' must be nonempty text')
    snapshot = proposal['source_snapshot_hash']
    if not (isinstance(snapshot, str) and bool(snapshot)) and not (snapshot is None and proposal['disposition'] == 'unresolved'):
        raise ValueError('source_snapshot_hash must be nonempty text; only unresolved may bind an exact missing snapshot')
    if not isinstance(proposal['rationale'], str) or not 20 <= len(proposal['rationale'].strip()) <= 5000:
        raise ValueError('source review needs a substantive 20–5000 character rationale')
    if not isinstance(proposal['notices'], list) or len(proposal['notices']) > 30:
        raise ValueError('notices must be a list of at most 30 inspected anchors')
    with closing(cases.connect(db)) as con, con:
        con.execute('BEGIN IMMEDIATE')
        row = con.execute('SELECT body FROM revisions WHERE case_id=? ORDER BY version DESC LIMIT 1', (case_id,)).fetchone()
        if not row:
            raise ValueError('case not found')
        data = json.loads(row['body'])
        if type(version) is not int or data['version'] != version:
            raise ValueError('case version changed; inspect the current notices')
        assessments = []
        for claim in data.get('claims', []):
            superseded = {a.get('supersedes') for a in claim['assessments']}
            assessments += [a for a in claim['assessments'] if a['id'] not in superseded]
        assessment = next((a for a in assessments if a['id'] == proposal['assessment_id']), None)
        if not assessment:
            raise ValueError('review must name an active assessment')
        target = next((r for r in assessment_status(data, assessment) if r['evidence_id'] == proposal['evidence_id']), None)
        if not target:
            raise ValueError('assessment does not use this warning source')
        if any(proposal[key] != target[key] for key in ('source_snapshot_hash', 'warning_fingerprint')):
            raise ValueError('source body or warning fingerprint changed')
        source = effective_source(data, next(e for e in data['evidence'] if e['id'] == proposal['evidence_id']))
        if proposal['disposition'] == 'unaffected' and _non_rehabilitable(source):
            raise ValueError('source cannot be rehabilitated: ' + ', '.join(_non_rehabilitable(source)))
        if proposal['disposition'] == 'unaffected' and not _available(source):
            raise ValueError('unavailable, retracted or superseded source cannot be rehabilitated')
        identities = set(target['notice_identities'])
        seen = set()
        seen_evidence = set()
        for notice in proposal['notices']:
            if not isinstance(notice, dict) or set(notice) != {'notice_identity', 'evidence_id', 'quote', 'snapshot_hash'}:
                raise ValueError('notice requires notice_identity, evidence_id, quote and snapshot_hash')
            if any(not isinstance(notice[key], str) or not notice[key] for key in ('notice_identity', 'evidence_id', 'snapshot_hash')):
                raise ValueError('notice identity, evidence_id and snapshot_hash must be nonempty text')
            if notice['notice_identity'] not in identities or notice['notice_identity'] in seen:
                raise ValueError('notice identity is unrelated or duplicated')
            notice_source = next((e for e in data['evidence'] if e['id'] == notice['evidence_id']), {})
            target_ids, _, _ = studies._identities(source)
            notice_ids, _, _ = studies._identities(notice_source)
            if target_ids & notice_ids:
                raise ValueError('notice_same_study: a mirror of the warned study cannot establish an independent correction notice')
            failure = _notice_failure(data, notice)
            if failure:
                raise ValueError(failure + ': inspect the named notice evidence and submit its current exact anchor')
            if proposal['disposition'] == 'unaffected' and notice['evidence_id'] in seen_evidence:
                raise ValueError('notice_evidence_reused: distinct registry notices require distinct unambiguous evidence')
            seen.add(notice['notice_identity'])
            seen_evidence.add(notice['evidence_id'])
        if proposal['disposition'] == 'unaffected':
            if not identities or seen != identities or any(not isinstance(w, dict) or not w.get('notice') for w in target['warnings']):
                raise ValueError('all registry notices must be inspected before an unaffected disposition')
            anchors = [assessment.get('anchor', {})] + [c.get('anchor', {}) for c in assessment.get('conditions', [])]
            if any(a.get('snapshot_hash') != source['snapshot_hash'] for a in anchors if a.get('evidence_id') == source['id']):
                raise ValueError('assessment source body is stale; review cannot repair its anchor')
        elif proposal['disposition'] == 'revise' and not seen:
            raise ValueError('revise requires an inspected notice; use unresolved when unavailable')
        record = {**proposal, 'id':uuid.uuid4().hex[:12], 'assessment_fingerprint':_assessment_hash(data, assessment),
                  'case_version':version, 'recorded_version':version + 1, 'at':cases.now(),
                  'authorship':'user_or_agent', 'meaning':MEANING}
        data.setdefault('source_reviews', []).append(record)
        data.update(version=version + 1, changes=[{'kind':'source_review_added', 'assessment_id':assessment['id'], 'evidence_id':source['id']}])
        con.execute('INSERT INTO revisions VALUES(?,?,?)', (case_id, version + 1, json.dumps(data)))
    return list_pending(case_id, db=db, version=version + 1)
