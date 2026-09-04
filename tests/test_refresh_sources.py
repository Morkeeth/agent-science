"""A refresh must reach the documents and discovery provider, not just the verdict DB."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from clearance import search,instruments
from clearance.facts import judge_claim,Claim

class RefreshTests(unittest.TestCase):
    def test_named_source_rejudges_new_document(self):
        with tempfile.TemporaryDirectory() as d, patch.object(instruments,'DOCS',Path(d)/'docs.json'):
            url='https://example.org/source';text='The Acme project permits commercial redistribution of its software.'
            instruments.DOCS.write_text(json.dumps({url:{'text':text}}))
            c=Claim('c',text,url,'commercial')
            self.assertEqual(judge_claim(c,fetch=False).verdict,'GREEN')
            with patch.object(instruments,'fetch_public',return_value=(b'The Acme project does not permit commercial redistribution of its software.',url)) as fetched:
                out=judge_claim(c,fetch=True,refresh=True)
            self.assertEqual(fetched.call_count,1)
            self.assertNotEqual(out.verdict,'GREEN')

    def test_discovery_refresh_bypasses_exact_query_cache(self):
        with tempfile.TemporaryDirectory() as d, patch.object(search,'CACHE',Path(d)/'search.json'), patch.object(search,'RECEIPTS',Path(d)/'receipts.jsonl'):
            payload={'results':[{'url':'https://example.org/old','title':'Old'}]}
            with patch.object(search,'_live_search',return_value=(payload,'old-call')) as provider:
                first=search.find_sources('objective',['query'],live=True)
                search.find_sources('objective',['query'],live=True)
                self.assertEqual(provider.call_count,1)
            new={'results':[{'url':'https://example.org/new','title':'New'}]};trace=[]
            with patch.object(search,'_live_search',return_value=(new,'new-call')) as provider:
                updated=search.find_sources('objective',['query'],live=True,refresh=True,trace=trace)
                self.assertEqual(provider.call_count,1)
            self.assertNotEqual(first[0].url,updated[0].url)
            self.assertEqual(trace[0]['search_id'],'new-call')

if __name__=='__main__':unittest.main()
