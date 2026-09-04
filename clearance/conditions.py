"""Extract structured study conditions with source spans.

Missing fields stay unknown — never invented. Span must occur verbatim in the source.
"""
from __future__ import annotations

import re

FIELDS = (
    'task',
    'population',
    'model',
    'comparator',
    'dataset',
    'metric',
    'resource_budget',
    'study_design',
    'limitations',
)

# Label-led patterns common in abstracts / structured papers. Span = matched line/sentence.
_PATTERNS = {
    'task': re.compile(
        r'(?im)^(?:task|tasks)\s*[:\-–]\s*(.+)$'
        r'|(?:we (?:study|evaluate|measure|assess)[^.!?]{0,80}?\bon\b[^.!?]{5,200}[.!?])'
        r'|(?:task(?:s)?(?:\s+is|\s+are|:)\s+[^.!?]{5,200}[.!?])'
    ),
    'population': re.compile(
        r'(?im)^(?:population|participants|subjects|sample)\s*[:\-–]\s*(.+)$'
        r'|(?:\b(?:n\s*=\s*\d+|population|participants|subjects)\b[^.!?]{0,160}[.!?])'
    ),
    'model': re.compile(
        r'(?im)^(?:model|models|system)\s*[:\-–]\s*(.+)$'
        r'|(?:\b(?:claude|gpt-?\d|gemini|llama|model(?:s)?)\b[^.!?]{0,160}[.!?])'
    ),
    'comparator': re.compile(
        r'(?im)^(?:comparator|baseline|control)\s*[:\-–]\s*(.+)$'
        r'|(?:\b(?:comparator|baseline|control(?:\s+condition)?|without\b[^.!?]{0,40}memory)\b[^.!?]{0,180}[.!?])'
    ),
    'dataset': re.compile(
        r'(?im)^(?:dataset|benchmark|corpus)\s*[:\-–]\s*(.+)$'
        r'|(?:\b(?:dataset|benchmark|corpus|swe-bench|hotpotqa|humaneval)\b[^.!?]{0,160}[.!?])'
    ),
    'metric': re.compile(
        r'(?im)^(?:metric|metrics|measure|outcome)\s*[:\-–]\s*(.+)$'
        r'|(?:\b(?:metric|resolve rate|exact match|accuracy|pass@|f1)\b[^.!?]{0,160}[.!?])'
    ),
    'resource_budget': re.compile(
        r'(?im)^(?:resource budget|budget|compute)\s*[:\-–]\s*(.+)$'
        r'|(?:\b(?:budget|turns?|tokens?|wall time|seconds|minutes)\b[^.!?]{0,180}[.!?])'
    ),
    'study_design': re.compile(
        r'(?im)^(?:study design|design|methods?)\s*[:\-–]\s*(.+)$'
        r'|(?:\b(?:randomized|controlled comparison|within-subject|between-subject|'
        r'qualitative interview|semi-structured|ablation|case study)\b[^.!?]{0,200}[.!?])'
    ),
    'limitations': re.compile(
        r'(?im)^(?:limitations?|caveats?)\s*[:\-–]\s*(.+)$'
        r'|(?:\b(?:limitation|may not generalize|exploratory|future work|caveat)\b[^.!?]{0,220}[.!?])'
    ),
}

_VALUE_CLEAN = re.compile(r'^(?:task|population|model|comparator|dataset|metric|'
                          r'resource budget|budget|study design|design|limitations?)\s*[:\-–]\s*',
                          re.I)


def _unknown():
    return {'value': None, 'span': None, 'status': 'unknown'}


def _known(span, text):
    span = ' '.join(span.split()).strip()
    if not span or span not in text and span not in ' '.join(text.split()):
        # Allow whitespace-normalized membership for line captures.
        compact_text = ' '.join(text.split())
        compact_span = ' '.join(span.split())
        if compact_span not in compact_text:
            return _unknown()
        # Prefer the original multiline span when it literally occurs.
        if span not in text:
            span = compact_span
            text_for_check = compact_text
        else:
            text_for_check = text
    else:
        text_for_check = text
    if len(span) < 8:
        return _unknown()
    value = _VALUE_CLEAN.sub('', span).strip()
    # Prefer a literal substring from the source when whitespace-normalized.
    if span not in text:
        # Find a nearby original sentence containing distinctive tokens.
        tokens = [t for t in re.findall(r'[A-Za-z0-9\-]{4,}', value)[:6]]
        for sent in re.split(r'(?<=[.!?])\s+|\n+', text):
            sent = sent.strip()
            if sent and all(t.lower() in sent.lower() for t in tokens[:2] if tokens):
                span = sent
                break
        if span not in text:
            # Last resort: keep compact form only if it appears compacted.
            if ' '.join(span.split()) not in ' '.join(text.split()):
                return _unknown()
    return {'value': value[:400], 'span': span[:800], 'status': 'known'}


def extract(text, *, url=None):
    """Return per-field conditions. Missing stays unknown with null value/span."""
    if not isinstance(text, str) or not text.strip():
        return {f: _unknown() for f in FIELDS} | {
            'url': url,
            'meaning': 'No source text; all conditions unknown.',
        }
    out = {}
    for field in FIELDS:
        match = _PATTERNS[field].search(text)
        if not match:
            out[field] = _unknown()
            continue
        span = next((g for g in match.groups() if g), match.group(0))
        # Prefer the full matched sentence when group is a short label capture.
        if match.lastindex and match.group(0) and len(match.group(0)) > len(span) + 5:
            # Label line: keep the capture as value, use the line as span if in text.
            line = match.group(0).strip()
            if line in text or line in ' '.join(text.split()):
                known = _known(line if line in text else span, text)
                if known['status'] == 'known':
                    known['value'] = _VALUE_CLEAN.sub('', span).strip()[:400] or known['value']
                    out[field] = known
                    continue
        out[field] = _known(span.strip(), text)
    out['url'] = url
    out['meaning'] = (
        'Condition values are extracted with source spans when present. '
        'Missing fields remain unknown — never inferred.'
    )
    return out


def merge_unknowns(primary, secondary):
    """Fill unknown fields from another extraction of the same study; never overwrite known."""
    out = dict(primary)
    for field in FIELDS:
        if out.get(field, {}).get('status') != 'known' and secondary.get(field, {}).get('status') == 'known':
            out[field] = dict(secondary[field])
    return out


def scope_signature(cond):
    """Comparable scope tokens for claim-graph scope checks."""
    sig = {}
    for field in ('task', 'population', 'dataset', 'metric', 'model', 'study_design'):
        row = cond.get(field) or _unknown()
        if row.get('status') == 'known' and row.get('value'):
            tokens = tuple(sorted(set(re.findall(r'[a-z0-9]+', row['value'].lower()))))
            sig[field] = tokens
        else:
            sig[field] = None
    return sig


def scopes_compatible(a, b, *, require=('task',)):
    """True when known required fields overlap enough to compare effect direction.

    If a required field is known on both sides and shares no token, scopes differ.
    Unknown on either side does not prove compatibility — returns 'unknown'.
    """
    sig_a = scope_signature(a)
    sig_b = scope_signature(b)
    differed = []
    unknown = []
    for field in require:
        ta, tb = sig_a.get(field), sig_b.get(field)
        if ta is None or tb is None:
            unknown.append(field)
            continue
        if not (set(ta) & set(tb)):
            differed.append(field)
    if differed:
        return {'compatible': False, 'scope_fields': differed, 'unknown_fields': unknown}
    if unknown:
        return {'compatible': None, 'scope_fields': [], 'unknown_fields': unknown}
    return {'compatible': True, 'scope_fields': [], 'unknown_fields': []}
