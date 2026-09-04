"""Study identity: normalize DOI/arXiv and associate HTML/PDF mirrors.

Title resemblance is never enough to merge. Uncertain links stay candidates.
"""
from __future__ import annotations

import re
from urllib.parse import urlsplit, urlunsplit

DOI_RE = re.compile(r'\b10\.\d{4,9}/[-._;()/:A-Z0-9]+\b', re.I)
ARXIV_RE = re.compile(r'(?:arxiv\.org/(?:abs|pdf|html)/|arxiv:)(\d{4}\.\d{4,5})(v\d+)?', re.I)


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
    if not match:
        return None
    return match.group(1).lower()


def canonical_url(url):
    if not isinstance(url, str) or not url.startswith(('http://', 'https://')):
        return None
    parts = urlsplit(url.strip())
    host = (parts.hostname or '').lower()
    path = parts.path.rstrip('/')
    if host.endswith('arxiv.org'):
        aid = normalize_arxiv(url)
        if aid:
            return f'https://arxiv.org/abs/{aid}'
    if 'doi.org' in host:
        doi = normalize_doi(url)
        if doi:
            return f'https://doi.org/{doi}'
    return urlunsplit((parts.scheme.lower(), host, path, '', ''))


def study_key(url, *, doi=None, arxiv_id=None):
    """Stable identity key. Prefer DOI, then arXiv, else canonical URL. Never title."""
    doi = normalize_doi(doi) or normalize_doi(url or '')
    if doi:
        return ('doi', doi)
    arxiv_id = normalize_arxiv(arxiv_id) or normalize_arxiv(url or '')
    if arxiv_id:
        return ('arxiv', arxiv_id)
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
            groups[key] = {'key': key, 'urls': [], 'identity': key[0], 'id': key[1]}
            order.append(key)
        groups[key]['urls'].append(url)
    return [groups[k] for k in order]


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
