"""User-visible traces describe executed operations, not a decorative route list."""
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from clearance import visibility,refusal_log

class TransparencyTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        self.env=patch.dict(os.environ,{'REFUSAL_LOG_DB':str(self.root/'log.db')});self.env.start()
    def tearDown(self):self.env.stop();self.temp.cleanup()
    def test_exact_replay_does_not_claim_unexecuted_routes(self):
        q='A genuine document describes a specific experiment with independent observations.'
        with refusal_log.connect() as con:
            refusal_log.record(con,term='experiment',assertion=q,verdict='GREEN',production='test',citation_url='https://example.org',quoted_terms=q)
        visibility.panel(q,personal=False)
        data=visibility.panel(q,personal=False)
        routes=[r['route'] for r in data['transparency']['angles_searched']]
        self.assertEqual(routes,['dictionary_exact'])
        self.assertEqual(data['transparency']['angles_searched'][0]['hit'],'hit')
        self.assertTrue(data['transparency']['shallow_route'])
    def test_no_catalog_fillers_for_unrelated_query(self):
        data=visibility.panel('tomato photosynthesis fertilizer',full=True,personal=False)
        self.assertEqual(data['field']['github'],[])
        self.assertEqual(data['field']['blogs_and_docs'],[])
        self.assertEqual(data['agentic_practices'],[])
        self.assertTrue(data['transparency']['shallow_route'])
        self.assertNotEqual(data['primary']['label'],'CONTRARY_TO_RESEARCH')
    def test_no_server_repo_fit(self):
        data=visibility.panel('science mcp',full=True,personal=False)
        self.assertEqual(data['stack_fit']['fit'],'unassessed')
        self.assertEqual(data['stack_fit']['stack'],{})
        user_repo=self.root/'client';user_repo.mkdir();(user_repo/'package.json').write_text('{}')
        data=visibility.panel('science mcp',full=True,personal=False,root=user_repo)
        self.assertEqual(data['stack_fit']['stack']['root'],str(user_repo.resolve()))
        self.assertEqual(data['stack_fit']['stack']['stack'],['node'])
    def test_form_exposes_fresh_search_and_unverified_context(self):
        data=visibility.panel('tomato photosynthesis',full=True,personal=False)
        page=visibility.render_html(data)
        self.assertIn('name="live"',page)
        self.assertIn('Related sources',page)
        self.assertIn('context, not verified support',page)
        self.assertNotIn('Full route',page)
        self.assertNotIn('Paste a script',page)
    def test_form_escapes_user_query(self):
        q='<script>alert(1)</script>'
        data=visibility.panel(q,personal=False)
        self.assertNotIn(q,visibility.render_html(data,query=q))

if __name__=='__main__':unittest.main()
