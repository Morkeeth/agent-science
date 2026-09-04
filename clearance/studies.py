"""Conservative study identity; shared identity is never independent replication."""
import re
from urllib.parse import unquote, urlsplit, urlunsplit
from clearance import cases

DOI = re.compile(r'10\.\d{4,9}/[^\s<>"]+', re.I)
ARXIV = re.compile(r'(\d{4}\.\d{4,5}|[a-z-]+(?:\.[A-Z]{2})?/\d{7})(v\d+)?$', re.I)
FIELDS = ('task', 'population', 'model', 'comparator', 'dataset', 'metric', 'budget', 'study_design', 'limitations')


def _identities(item):
    identities = set(); versions = set(); basis = []
    for field in ('url', 'final_url', 'doi', 'arxiv_id'):
        value = unquote(str(item.get(field) or '')).strip()
        parsed = urlsplit(value)
        host = (parsed.hostname or '').lower()
        if field == 'doi' or host in ('doi.org', 'dx.doi.org'):
            match = DOI.search(value)
            if match:
                doi = match[0].rstrip('.,;')
                # DOI suffixes can contain balanced parentheses. Trim only a
                # surplus closing delimiter from a surrounding prose citation.
                while doi.endswith(')') and doi.count(')') > doi.count('('):
                    doi = doi[:-1].rstrip('.,;')
                identity = 'doi:' + doi.lower()
                identities.add(identity); basis.append({'field':field, 'value':value, 'identity':identity})
        if field == 'arxiv_id' or host in ('arxiv.org', 'www.arxiv.org', 'export.arxiv.org'):
            value = value.removeprefix('arXiv:')
            value = re.sub(r'^/(?:abs|pdf|html)/', '', parsed.path) if host else value
            match = ARXIV.fullmatch(value.removesuffix('.pdf'))
            if match:
                identity = 'arxiv:' + match[1].lower()
                identities.add(identity)
                if match[2]: versions.add(identity + match[2].lower())
                basis.append({'field':field, 'value':str(item.get(field)), 'identity':identity})
    return identities, versions, basis


def group(evidence):
    """Group explicit source identifiers only; citations in prose remain candidates."""
    rows = []
    for item in evidence:
        ids, versions, basis = _identities(item)
        parsed = urlsplit(item.get('final_url') or item.get('url', ''))
        url = urlunsplit((parsed.scheme.lower(), parsed.netloc.lower(), parsed.path, parsed.query, ''))
        key = 'document:' + cases.digest(url or item['id'])[:20]
        rows.append({'ids':ids or {key}, 'versions':versions, 'basis':basis, 'items':[item]})
    merged = []
    for row in rows:
        overlaps = [r for r in merged if r['ids'] & row['ids']]
        for other in overlaps:
            row['ids'] |= other['ids']; row['versions'] |= other['versions']
            row['basis'] += other['basis']; row['items'] += other['items']; merged.remove(other)
        merged.append(row)
    result = []
    for row in merged:
        items = sorted(row['items'], key=lambda e:e['id'])
        result.append({'id':sorted(row['ids'])[0], 'identities':sorted(row['ids']),
            'versions':sorted(row['versions']), 'evidence_ids':[e['id'] for e in items],
            'identity_basis':row['basis'], 'documents':[{'evidence_id':e['id'], 'url':e.get('url'),
                'snapshot_hash':e.get('snapshot_hash'), 'status':e.get('status')} for e in items],
            'identity_candidates':sorted(set(i for e in items for i in DOI.findall(e.get('snapshot_text','')))),
            'conditions':{field:[] for field in FIELDS},
            'independence':'Unknown. Distinct identifiers do not establish independent replication.'})
    return sorted(result, key=lambda r:r['id'])
