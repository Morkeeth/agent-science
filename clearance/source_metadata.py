"""Bounded primary-registry metadata checks; source content is never tool authority.

Crossref update direction matters: a retraction notice is not itself retracted.
An absent relation means unknown coverage, never a clean bill of health.
"""
import hashlib
import http.client
import json
import re
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from contextlib import closing

from clearance import cases, studies

MAX_BYTES = 2_000_000
TIMEOUT = 20
_ARXIV_LOCK = threading.Lock()
_ARXIV_LAST = 0.0
LIMITS = ('Registry metadata can be incomplete or incorrect. Absence is not proof of no updates.',
          'Metadata checks do not fetch or compare the source body.',
          'arXiv API returns the current version, not a complete version history; withdrawal is not inferred from prose.')


class _ResponseTooLarge(ValueError):
    def __init__(self, body, status):
        super().__init__('registry response exceeds size limit')
        self.response_hash = hashlib.sha256(body).hexdigest()
        self.status = status


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ValueError('registry redirect refused')


def _fetch(url):
    global _ARXIV_LAST
    if url.startswith('https://export.arxiv.org/'):
        with _ARXIV_LOCK:
            time.sleep(max(0, 3 - (time.monotonic() - _ARXIV_LAST)))
            _ARXIV_LAST = time.monotonic()
    request = urllib.request.Request(url, headers={'User-Agent':'AgentScience/0.5 (source metadata)', 'Accept':'application/json, application/atom+xml'})
    opener = urllib.request.build_opener(_NoRedirect())
    with opener.open(request, timeout=TIMEOUT) as response:
        body = response.read(MAX_BYTES + 1)
        if len(body) > MAX_BYTES: raise _ResponseTooLarge(body, response.status)
        return body, response.status


def _doi(value):
    if not isinstance(value, str): return None
    value = value.strip().lower()
    return 'doi:' + value if re.fullmatch(r'10\.\d{4,9}/[^\s<>"#?]+', value) else None


def _parse(provider, identity, body):
    relations, versions = [], []
    if provider == 'crossref':
        message = json.loads(body)['message']
        if not isinstance(message, dict) or _doi(message.get('DOI')) != identity:
            raise ValueError('registry identity mismatch')
        for field in ('updated-by', 'update-to'):
            items = message.get(field) or []
            if not isinstance(items, list): raise ValueError('invalid registry relations')
            for item in items:
                if not isinstance(item, dict): raise ValueError('invalid registry relation')
                other = _doi(item.get('DOI'))
                if not other: continue
                kind = item.get('type')
                # Preserve registry vocabulary; unknown incoming updates still need review.
                if not isinstance(kind, str) or len(kind) > 100: continue
                target, notice = (identity, other) if field == 'updated-by' else (other, identity)
                relations.append({'type':kind.strip().lower().replace('_', '-'), 'raw_type':kind, 'target':target, 'notice':notice,
                                  'field':field, 'source':item.get('source'), 'updated':item.get('updated')})
    else:
        if b'<!DOCTYPE' in body.upper() or b'<!ENTITY' in body.upper():
            raise ValueError('XML declarations refused')
        tree = ET.fromstring(body)
        ns = {'a':'http://www.w3.org/2005/Atom'}
        entries = tree.findall('a:entry', ns)
        if len(entries) != 1: raise ValueError('missing or ambiguous arXiv entry')
        entry = entries[0]
        url = entry.findtext('a:id', '', ns)
        ids, found_versions, _ = studies._identities({'url':url})
        if ids != {identity} or len(found_versions) != 1: raise ValueError('registry identity/version mismatch')
        versions.append({'id':next(iter(found_versions)), 'published':entry.findtext('a:published', None, ns),
                         'updated':entry.findtext('a:updated', None, ns)})
    return relations, versions


def _request_plan(evidence):
    if not isinstance(evidence, dict): raise ValueError('evidence must be an object')
    identities, pinned, _ = studies._identities(evidence)
    requests, skipped = [], []
    # Conflicting same-provider identifiers are not merged or guessed.
    for prefix, provider in (('doi:', 'crossref'), ('arxiv:', 'arxiv')):
        selected = sorted(i for i in identities if i.startswith(prefix))
        if len(selected) > 1:
            skipped.append({'provider':provider, 'status':'ambiguous', 'errors':['Conflicting explicit identifiers'], 'checked_at':None})
            continue
        for identity in selected:
            key = identity[len(prefix):]
            url = ('https://api.crossref.org/works/' + urllib.parse.quote(key, safe='') if provider == 'crossref'
                   else 'https://export.arxiv.org/api/query?' + urllib.parse.urlencode({'id_list':key, 'max_results':1}))
            requests.append((provider, identity, url))
    return identities, pinned, requests, skipped


def planned_request_count(evidence):
    """Exact maximum GET count before execution, using the inspector's plan.

    Unsupported or conflicting identities contribute no request. A supported
    identity for the other registry can still be inspected independently.
    """
    return len(_request_plan(evidence)[2])


def inspect(evidence, *, live=False):
    """Inspect exact identifiers only. No discovery, body reads, or paid calls.

    Callers must serialize/rate-limit repeated arXiv requests per its API terms.
    """
    if type(live) is not bool or not isinstance(evidence, dict): raise ValueError('evidence and boolean live required')
    identities, pinned, requests, skipped = _request_plan(evidence)
    result = {'schema_version':1, 'evidence_id':evidence.get('id'), 'identities':sorted(identities),
              'status':'not_checked', 'records':[], 'relations':[], 'coverage_limits':list(LIMITS)}
    if not live: return result
    if not identities:
        result.update(status='unsupported', errors=['No explicit DOI or arXiv identifier'])
        return result
    result['records'].extend(skipped)
    for provider, identity, url in requests:
        record = {'provider':provider, 'identity':identity, 'requested_url':url, 'checked_at':None,
                  'response_hash':None, 'http_status':None, 'relations':[], 'versions':[], 'errors':[], 'status':'failed'}
        try:
            body, status = _fetch(url)
            record.update(checked_at=cases.now(), response_hash=hashlib.sha256(body).hexdigest(), http_status=status)
            relations, versions = _parse(provider, identity, body)
            record.update(status='checked', relations=relations, versions=versions)
            if provider == 'arxiv':
                latest = versions[0]['id']
                old = [v for v in pinned if v.startswith(identity+'v')]
                if len(old) == 1 and int(latest.rsplit('v',1)[1]) > int(old[0].rsplit('v',1)[1]):
                    relations.append({'type':'new-version', 'target':identity, 'target_version':old[0], 'notice':latest, 'field':'entry.id'})
            result['relations'].extend(relations)
        except _ResponseTooLarge as exc:
            record.update(http_status=exc.status, checked_at=cases.now(), response_hash=exc.response_hash,
                          response_hash_scope='bounded_prefix')
            record['errors'].append(str(exc))
        except urllib.error.HTTPError as exc:
            record.update(http_status=exc.code, checked_at=cases.now())
            try:
                body = exc.read(MAX_BYTES + 1)
                record['response_hash'] = hashlib.sha256(body).hexdigest()
                if len(body) > MAX_BYTES: record['response_hash_scope'] = 'bounded_prefix'
            except (OSError, http.client.HTTPException):
                pass
            finally:
                exc.close()
            record['errors'].append('Registry HTTP ' + str(exc.code))
        except (ValueError, KeyError, TypeError, ET.ParseError, OSError, http.client.HTTPException) as exc:
            record['errors'].append(type(exc).__name__ + ': ' + str(exc)[:300])
        result['records'].append(record)
    checked = sum(r['status'] == 'checked' for r in result['records'])
    result['status'] = 'checked' if checked == len(result['records']) else 'partial' if checked else 'failed'
    return result


def apply(case_id, version, evidence_id, metadata, *, db=None):
    """Commit an inspect result from trusted local code, not a host/model proposal.

    Registry status is not cryptographic proof. Never expose this mutation with
    caller-authored metadata over MCP; expose an inspect-then-apply operation.
    """
    if not isinstance(metadata, dict) or metadata.get('evidence_id') != evidence_id:
        raise ValueError('metadata evidence mismatch')
    with closing(cases.connect(db)) as con, con:
        con.execute('BEGIN IMMEDIATE')
        row = con.execute('SELECT body FROM revisions WHERE case_id=? ORDER BY version DESC LIMIT 1', (case_id,)).fetchone()
        if not row: raise ValueError('case not found')
        data = json.loads(row['body'])
        if type(version) is not int or data['version'] != version: raise ValueError('case version changed')
        evidence = next((e for e in data['evidence'] if e['id'] == evidence_id), None)
        if evidence is None: raise ValueError('evidence not found')
        ids, pinned, _ = studies._identities(evidence)
        if metadata.get('identities') != sorted(ids): raise ValueError('metadata identity mismatch')
        evidence['source_metadata'] = metadata
        times = [r['checked_at'] for r in metadata.get('records', []) if r.get('checked_at') and r.get('status') == 'checked' and r.get('identity') in ids]
        if times: evidence['metadata_checked_at'] = max(times)
        effects = []
        for record in metadata.get('records', []):
            if record.get('status') != 'checked' or record.get('identity') not in ids: continue
            for relation in record.get('relations', []):
                if relation.get('target') != record['identity']: continue
                kind = relation.get('type')
                if record['provider'] == 'crossref' and relation.get('field') == 'updated-by':
                    if kind == 'retraction': evidence['retracted'] = True
                    # Every exact incoming registry update is inspectable, even
                    # when its vocabulary is unfamiliar. Only explicit retraction
                    # has the stronger retracted effect.
                    effects.append(relation)
                if record['provider'] == 'arxiv' and kind == 'new-version' and relation.get('target_version') in pinned:
                    evidence['superseded_by'] = relation['notice']; effects.append(relation)
        # Missing records never clear earlier explicit flags.
        if effects:
            # A partial registry response cannot silently retire an earlier notice.
            retained = list(evidence.get('metadata_review_required') or [])
            for effect in effects:
                if effect not in retained: retained.append(effect)
            evidence['metadata_review_required'] = retained
        data['version'] += 1
        data.setdefault('trace', []).append({'route':'source_metadata', 'outcome':metadata.get('status'),
                                           'evidence_id':evidence_id, 'at':cases.now(), 'source_body_checked':False})
        con.execute('INSERT INTO revisions(case_id,version,body) VALUES(?,?,?)', (case_id,data['version'],json.dumps(data)))
    return cases.get(case_id, db=db)
