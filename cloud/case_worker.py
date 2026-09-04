"""One research job. Private caches die with its request directory."""
import json
import os
from pathlib import Path
import sys

from clearance import cases, instruments, search


def run(payload, db):
    cache = Path(db).parent / 'research-cache'
    cache.mkdir(exist_ok=True)
    search.CACHE = cache / 'searches.json'
    search.RECEIPTS = cache / 'search_receipts.jsonl'
    instruments.DOCS = cache / 'documents.json'
    instruments.CACHE = cache / 'instruments.json'
    # Offline refresh can inspect this workspace's own saved source text.
    documents = {}
    if payload['action'] == 'refresh':
        old = cases.get(payload['case_id'], db=db)
        if len(old['evidence']) > 24:
            raise ValueError('Source limit reached. Start a focused case with selected URLs.')
        for e in old['evidence']:
            if 'snapshot_text' in e:
                documents[instruments.canonical(e['url'])] = {
                    'text': e['snapshot_text'], 'fetched_at': e.get('fetched_at'), 'final_url': e.get('final_url',e['url'])}
    instruments.DOCS.write_text(json.dumps(documents))
    if payload['action'] == 'create':
        result = cases.create(payload['question'], live=payload['live'], sources=payload['sources'],
                              official_domains=payload['official_domains'], db=db, max_documents=24)
    else:
        result = cases.refresh(payload['case_id'], live=payload['live'], db=db, max_documents=24)
    return {'case_id': result['id'], 'version': result['version']}


if __name__ == '__main__':
    try:
        payload = json.load(sys.stdin)
        result = run(payload, Path(sys.argv[1]))
        print(json.dumps(result))
    except Exception:
        # Provider exceptions can contain queries, URLs and credentials.
        print(json.dumps({'error': 'Research did not complete. The attempt remains counted.'}))
        sys.exit(1)
