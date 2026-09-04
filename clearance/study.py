"""Study identity: normalize DOI/arXiv and associate HTML/PDF mirrors.

Title resemblance is never enough to merge. Uncertain links stay candidates.
A Study carries identity evidence, document refs, versions and extracted conditions.
"""
from __future__ import annotations

import re
from urllib.parse import urlsplit, urlunsplit

from clearance import conditions as conditions_mod

DOI_RE = re.compile(r'\b10\.\d{4,9}/[-._;()/:A-Z0-9]+\b', re.I)
ARXIV_RE = re.compile(
    r'(?:arxiv\.org/(?:abs|pdf|html)/|ar5iv\.labs\.arxiv\.org/(?:html|abs)/|'
    r'export\.arxiv\.org/(?:abs|pdf)/|arxiv:)(\d{4}\.\d{4,5})(v\d+)?',
    re.I,
)
ARXIV_DOI_RE = re.compile(r'10\.48550/arxiv\.(\d{4}\.\d{4,5})', re.I)
PMC_RE = re.compile(r'\bPMC(\d+)\b', re.I)


def normalize_doi(value):
    if not isinstance(value, str):
        return None
    match = DOI_RE.search(value.strip())
    if not match:
        return None
    return match.group(0).rstrip('.).,').lower()


def normalize_arxiv(value):
    if not isinstance(value, str):
        return None
    match = ARXIV_RE.search(value.strip())
    if match:
        return match.group(1).lower()
    doi_match = ARXIV_DOI_RE.search(value.strip())
    if doi_match:
        return doi_match.group(1).lower()
    return None


def normalize_pmc(value):
    if not isinstance(value, str):
        return None
    match = PMC_RE.search(value.strip())
    if not match:
        return None
    return match.group(1)


def arxiv_version(value):
    if not isinstance(value, str):
        return None
    match = ARXIV_RE.search(value.strip())
    if match and match.group(2):
        return match.group(2).lower()
    return None


def canonical_url(url):
    if not isinstance(url, str) or not url.startswith(('http://', 'https://')):
        return None
    parts = urlsplit(url.strip())
    host = (parts.hostname or '').lower()
    path = parts.path.rstrip('/')
    aid = normalize_arxiv(url)
    if aid and ('arxiv.org' in host or 'ar5iv' in host):
        return f'https://arxiv.org/abs/{aid}'
    if 'doi.org' in host or normalize_doi(url):
        doi = normalize_doi(url)
        if doi:
            # arXiv DOIs collapse to the arXiv abs identity when present.
            arx = normalize_arxiv(doi) or normalize_arxiv(url)
            if arx:
                return f'https://arxiv.org/abs/{arx}'
            return f'https://doi.org/{doi}'
    pmc = normalize_pmc(url)
    if pmc and ('ncbi.nlm.nih.gov' in host or 'europepmc.org' in host):
        return f'https://www.ncbi.nlm.nih.gov/pmc/articles/PMC{pmc}/'
    return urlunsplit((parts.scheme.lower(), host, path, '', ''))


def study_key(url, *, doi=None, arxiv_id=None, pmc_id=None):
    """Stable identity key. Prefer DOI (non-arXiv), then arXiv, then PMC, else URL.

    Never title. Callers that only have a title must leave links as candidates.
    """
    doi = normalize_doi(doi) or normalize_doi(url or '')
    arxiv_id = normalize_arxiv(arxiv_id) or normalize_arxiv(url or '') or (
        normalize_arxiv(doi) if doi else None
    )
    if arxiv_id:
        return ('arxiv', arxiv_id)
    if doi:
        return ('doi', doi)
    pmc_id = normalize_pmc(pmc_id) or normalize_pmc(url or '')
    if pmc_id:
        return ('pmc', pmc_id)
    canon = canonical_url(url) if url else None
    if canon:
        return ('url', canon)
    return None


def group_documents(urls):
    """Group mirror URLs by study identity. Uncertain links remain singleton candidates."""
    groups = {}
    order = []
    for url in urls:
        key = study_key(url)
        if key is None:
            key = ('candidate', url)
        if key not in groups:
            groups[key] = {
                'key': key,
                'urls': [],
                'identity': key[0],
                'id': key[1],
                'versions': [],
            }
            order.append(key)
        groups[key]['urls'].append(url)
        ver = arxiv_version(url)
        if ver and ver not in groups[key]['versions']:
            groups[key]['versions'].append(ver)
    return [groups[k] for k in order]


def merge_by_title(title_a, title_b):
    """Explicit refuse: titles never authorize a merge."""
    return {
        'merged': False,
        'reason': 'title_resemblance_refused',
        'title_a': title_a,
        'title_b': title_b,
        'meaning': 'Study identity requires DOI, arXiv id, PMC id, or exact URL. Titles are not identity.',
    }


def build_studies(evidence):
    """Build Study objects from evidence rows. Mirrors collapse; titles never merge."""
    buckets = {}
    order = []
    for e in evidence:
        key = study_key(e.get('url', ''), doi=e.get('doi'), arxiv_id=e.get('arxiv_id'))
        if key is None:
            key = ('candidate', e.get('url') or e.get('id') or id(e))
        if key not in buckets:
            buckets[key] = {
                'identity': key[0],
                'id': key[1],
                'canonical_key': {'scheme': key[0], 'id': key[1]},
                'versions': [],
                'document_refs': [],
                'identity_evidence': [],
                'conditions': None,
                'titles_seen': [],
            }
            order.append(key)
        study = buckets[key]
        study['document_refs'].append({
            'evidence_id': e.get('id'),
            'url': e.get('url'),
            'kind': e.get('kind'),
            'status': e.get('status'),
            'snapshot_hash': e.get('snapshot_hash'),
        })
        ver = arxiv_version(e.get('url', ''))
        if ver and ver not in study['versions']:
            study['versions'].append(ver)
        if e.get('title'):
            study['titles_seen'].append(e['title'])
        study['identity_evidence'].append({
            'url': e.get('url'),
            'scheme': key[0],
            'id': key[1],
            'basis': 'doi_or_arxiv_or_url' if key[0] != 'candidate' else 'unresolved_candidate',
        })
        text = e.get('snapshot_text') or ''
        if text and study['conditions'] is None:
            study['conditions'] = conditions_mod.extract(text, url=e.get('url'))
        elif text and study['conditions'] is not None:
            # Fill unknowns from later mirrors of the same study; never overwrite known.
            extra = conditions_mod.extract(text, url=e.get('url'))
            study['conditions'] = conditions_mod.merge_unknowns(study['conditions'], extra)
    out = []
    for key in order:
        s = buckets[key]
        # If multiple distinct titles appear under one identity key, keep them as aliases —
        # still one study. Distinct URL keys with similar titles remain separate (by construction).
        s['title_aliases'] = list(dict.fromkeys(s.pop('titles_seen')))
        s['meaning'] = (
            'Study identity is DOI/arXiv/PMC/URL. Title resemblance never merges studies. '
            'Conditions missing from sources remain unknown.'
        )
        out.append(s)
    return out


def annotate_evidence(evidence):
    """Attach study_key to evidence rows without merging by title."""
    out = []
    for e in evidence:
        key = study_key(e.get('url', ''))
        row = dict(e)
        if key:
            row['study_key'] = {'scheme': key[0], 'id': key[1]}
        else:
            row['study_key'] = None
        out.append(row)
    return out
