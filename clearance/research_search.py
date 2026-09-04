"""Explainable local retrieval. Topic matches are navigation, never verdicts."""
from contextlib import closing
import json
from pathlib import Path
import re
import shlex

from clearance import cases, research

STOP = set('a an the and or for to of in on is are do does how what when where which should my our it we can same keep more than use using agent agents repo repository'.split())
# Explicit navigation vocabulary; deliberately separate from scientific claims.
TOPICS = {
    'retrieval': ('rag', 'retrieval', 'embedding', 'embeddings', 'obsidian', 'repository search', 'lexical search', 'bm25'),
    'memory': ('memory', 'context engineering', 'persistent context', 'agents.md', 'context files', 'context file'),
    'interaction': ('ux', 'user experience', 'human intervention', 'human-ai collaboration', 'agent interface', 'progress display'),
    'coordination': ('multi-agent', 'multi agent', 'multiagent', 'coordination', 'delegation', 'delegated agents', 'parallel agents', 'multiple agents'),
    'evaluation': ('evaluation', 'benchmark', 'benchmarks', 'acceptance test', 'acceptance script', 'ablation'),
}


def tokens(text):
    return set(re.findall(r'[\w]+', text.casefold())) - STOP


def topics(text):
    text = text.casefold()
    return {name for name, phrases in TOPICS.items()
            if any(re.search(r'(?<!\w)' + re.escape(p) + r'(?!\w)', text) for p in phrases)}


def find(query, *, db=None, root=None, limit=5, offset=0):
    if not isinstance(query, str) or not query.strip() or len(query) > 1500:
        raise ValueError('find requires a query of 1–1500 characters')
    if type(limit) is not int or not 1 <= limit <= 100 or type(offset) is not int or offset < 0:
        raise ValueError('limit must be 1–100; offset must be nonnegative')
    if root is not None and not Path(root).is_dir():
        raise ValueError('root must be an existing directory')
    root = str(Path(root).resolve()) if root is not None else None
    terms, query_topics = tokens(query), topics(query)
    if not terms and not query_topics:
        raise ValueError('query needs a specific topic or keyword')
    hits = []
    with closing(cases.connect(db)) as con:
        records = con.execute('''SELECT r.body FROM revisions r
            WHERE r.version=(SELECT MAX(version) FROM revisions WHERE case_id=r.case_id)
            AND (? IS NULL OR json_extract(r.body,'$.repo.root')=?)''', (root, root)).fetchall()
    for record in records:
        data = json.loads(record[0])
        brief = research.brief(data)
        fields = [('question', data['question'])]
        for claim in brief['claims']:
            fields.append(('claim', claim['statement']))
            fields.extend(('assessment', a['rationale']) for a in claim['assessments'] if a['state'] != 'SUPERSEDED')
        matched_terms, matched_topics, matched_fields = set(), set(), set()
        for field, text in fields:
            literal = terms & tokens(text)
            expanded = query_topics & topics(text)
            if literal or expanded:
                matched_fields.add(field)
                matched_terms |= literal
                matched_topics |= expanded
        # Count unique matches: repeating the same claim cannot boost a case.
        score = len(matched_terms) * 2 + len(matched_topics)
        if not score:
            continue
        def claim_score(claim):
            text = claim['statement'] + ' ' + ' '.join(
                a['rationale'] for a in claim['assessments'] if a['state'] != 'SUPERSEDED')
            return len(terms & tokens(text)) * 2 + len(query_topics & topics(text))

        selected = [{**c, 'assessments': [a for a in c['assessments'] if a['state'] != 'SUPERSEDED']}
                    for c in sorted(brief['claims'], key=lambda c: (-claim_score(c), c['id']))[:5]]
        row = {'case_id': data['id'], 'version': data['version'], 'question': data['question'],
               'root': (data.get('repo') or {}).get('root'), 'checked_at': data['checked_at'],
               'match': {'terms': sorted(matched_terms), 'topics': sorted(matched_topics), 'fields': sorted(matched_fields)},
               'claims': selected, 'claim_count': len(brief['claims']),
               'unread_report_citations': brief['unread_report_citations'],
               'inspect': {'action': 'brief', 'case_id': data['id'], 'version': data['version'],
                           **({'db': str(db)} if db is not None else {})}}
        hits.append((score, row))
    hits.sort(key=lambda pair: (-pair[0], pair[1]['case_id']))
    return {'query': query, 'root': root, 'cases': [row for _, row in hits[offset:offset + limit]],
            'offset': offset, 'limit': limit, 'has_more': len(hits) > offset + limit,
            'next_offset': offset + limit if len(hits) > offset + limit else None,
            'basis': 'Local saved questions, claims and active assessment rationales. Explicit topic vocabulary expands matches. Ranking is relevance, not evidence strength.',
            'limits': ['Saved research retrieval made no web or model call.', 'Assessments are authored interpretations; inspect task and budget limits before applying them.',
                       'Full source snapshots and original report bodies are not searched; selected assessment quotes can appear in results. Up to five claims are shown per case; brief shows all.']}


def render(result, *, db=None):
    if 'error' in result:
        return 'Saved research unavailable: ' + result['error'] + '\n'
    flag = ' --db ' + shlex.quote(str(db)) if db is not None else ''
    lines = ['SAVED RESEARCH', result['basis']]
    if result.get('root'):
        lines.append('Search scope: cases attached to ' + result['root'])
    if not result['cases']:
        lines.append('No matching saved research. Investigate an explicit public query to add evidence.')
    for row in result['cases']:
        lines.extend(['', f"{row['case_id']} · v{row['version']} · {row['question']}",
                      'Matched terms: ' + (', '.join(row['match']['terms']) or 'none') +
                      '; related topics: ' + (', '.join(row['match']['topics']) or 'none'),
                      'Saved scope: ' + (row['root'] or 'general research; no repository attached')])
        for claim in row['claims']:
            lines.append(f"  [{claim['state']}] {claim['statement']}")
            for assessment in claim['assessments']:
                if assessment['state'] == 'SUPERSEDED':
                    continue
                lines.append(f"    {assessment['relation']} · {assessment['state']}: {assessment['rationale']}")
                if assessment['anchor']:
                    lines.append('    ' + assessment['anchor']['url'])
        lines.append(f"Inspect: agent-science case brief {row['case_id']} --version {row['version']}{flag}")
    if result['has_more']:
        lines.append(f"More matches: repeat with --offset {result['next_offset']}")
    return '\n'.join(lines + [''] + result['limits']) + '\n'
