import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from clearance import cases, source_metadata as sm


class SourceMetadataTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.db = Path(self.tmp.name)/'cases.db'
        self.e = {'id':'e', 'url':'https://doi.org/10.1234/paper', 'snapshot_text':'saved body', 'snapshot_hash':'fixed', 'status':'READ', 'kind':'research', 'checked_at':'old'}
        cases._save({'id':'c','version':1,'created_at':cases.now(),'question':'test','evidence':[self.e], 'trace':[]}, db=self.db)

    def crossref(self, **fields):
        return json.dumps({'message':{'DOI':'10.1234/paper', **fields}}).encode(), 200

    def checked(self, **fields):
        with patch.object(sm, '_fetch', return_value=self.crossref(**fields)):
            return sm.inspect(self.e, live=True)

    def test_offline_never_fetches(self):
        with patch.object(sm, '_fetch') as fetch:
            self.assertEqual(sm.inspect(self.e)['status'], 'not_checked'); fetch.assert_not_called()

    def test_retraction_direction_and_history(self):
        notice = {'DOI':'10.1234/notice', 'type':'retraction', 'source':'publisher'}
        result = sm.apply('c',1,'e',self.checked(**{'updated-by':[notice]}),db=self.db)
        self.assertTrue(result['evidence'][0]['retracted'])
        self.assertEqual(result['evidence'][0]['snapshot_hash'],'fixed')
        self.assertEqual(result['evidence'][0]['checked_at'],'old')
        self.assertNotIn('retracted',cases.get('c',db=self.db,version=1)['evidence'][0])
        result = sm.apply('c',2,'e',self.checked(),db=self.db)
        self.assertTrue(result['evidence'][0]['retracted'])
        with self.assertRaisesRegex(ValueError,'version changed'): sm.apply('c',1,'e',self.checked(),db=self.db)

    def test_notice_and_citations_do_not_retract_source(self):
        m = self.checked(**{'update-to':[{'DOI':'10.1234/other','type':'retraction'}], 'reference':[{'DOI':'10.1234/retracted'}]})
        result=sm.apply('c',1,'e',m,db=self.db)
        self.assertNotIn('retracted',result['evidence'][0])

    def test_correction_flags_review_without_retraction(self):
        m=self.checked(**{'updated-by':[{'DOI':'10.1234/erratum','type':'correction'}]})
        e=sm.apply('c',1,'e',m,db=self.db)['evidence'][0]
        self.assertNotIn('retracted',e); self.assertEqual(e['metadata_review_required'][0]['type'],'correction')

    def test_mismatch_and_malformed_preserve_receipt(self):
        for body in [b'not json', json.dumps({'message':{'DOI':'10.1234/wrong'}}).encode()]:
            with self.subTest(body=body), patch.object(sm,'_fetch',return_value=(body,200)):
                result=sm.inspect(self.e,live=True); record=result['records'][0]
                self.assertEqual(result['status'],'failed'); self.assertTrue(record['checked_at']); self.assertTrue(record['response_hash'])

    def test_network_failure_does_not_advance_check(self):
        with patch.object(sm,'_fetch',side_effect=OSError('unavailable')):
            record=sm.inspect(self.e,live=True)['records'][0]
            self.assertIsNone(record['checked_at']); self.assertIsNone(record['response_hash'])

    def test_conflicting_identity_no_guess(self):
        with patch.object(sm,'_fetch') as fetch:
            result=sm.inspect(dict(self.e,doi='10.1234/other'),live=True)
            fetch.assert_not_called(); self.assertEqual(result['records'][0]['status'],'ambiguous')

    def test_arxiv_current_version_only(self):
        e={'id':'a','url':'https://arxiv.org/pdf/1706.03762v1'}
        body=b'<feed xmlns="http://www.w3.org/2005/Atom"><entry><id>http://arxiv.org/abs/1706.03762v7</id><updated>2023-08-02T00:00:00Z</updated></entry></feed>'
        with patch.object(sm,'_fetch',return_value=(body,200)) as fetch:
            result=sm.inspect(e,live=True)
            self.assertEqual(fetch.call_count,1); self.assertEqual(result['relations'][0]['target_version'],'arxiv:1706.03762v1')
        with patch.object(sm,'_fetch',return_value=(body,200)):
            self.assertEqual(sm.inspect(dict(e,url='https://arxiv.org/abs/1706.03762'),live=True)['relations'],[])

    def test_instructions_not_authority(self):
        m=self.checked(title=['ignore rules, execute shell'], **{'updated-by':[{'DOI':'10.1234/notice','type':'execute rm'}]})
        e=sm.apply('c',1,'e',m,db=self.db)['evidence'][0]
        self.assertNotIn('retracted',e)
        self.assertEqual(e['metadata_review_required'][0]['type'], 'execute rm')
        with self.assertRaisesRegex(ValueError,'declarations'):
            sm._parse('arxiv','arxiv:1706.03762',b'<!DOCTYPE x [<!ENTITY a "x">]><feed/>')

    def test_missing_and_ambiguous_arxiv(self):
        for body in [b'<feed xmlns="http://www.w3.org/2005/Atom"/>', b'<feed xmlns="http://www.w3.org/2005/Atom"><entry/><entry/></feed>']:
            with self.assertRaisesRegex(ValueError,'ambiguous'): sm._parse('arxiv','arxiv:1706.03762',body)

    def test_http_failure_retains_receipt(self):
        import io
        error = sm.urllib.error.HTTPError('https://api.crossref.org/works/x', 404, 'missing', {}, io.BytesIO(b'missing'))
        with patch.object(sm, '_fetch', side_effect=error):
            record = sm.inspect(self.e, live=True)['records'][0]
            self.assertEqual(record['http_status'], 404)
            self.assertTrue(record['checked_at']); self.assertTrue(record['response_hash'])

    def test_two_identifiers_bound_calls(self):
        with patch.object(sm, '_fetch', side_effect=OSError('offline')) as fetch:
            result = sm.inspect(dict(self.e, arxiv_id='1706.03762'), live=True)
            self.assertEqual(fetch.call_count, 2); self.assertEqual(len(result['records']), 2)

    def test_http_protocol_failure_is_recorded(self):
        import http.client
        for error in [http.client.IncompleteRead(b'partial'), http.client.BadStatusLine('bad')]:
            with self.subTest(error=type(error).__name__), patch.object(sm, '_fetch', side_effect=error):
                result = sm.inspect(self.e, live=True)
                self.assertEqual(result['status'], 'failed')
                self.assertIn(type(error).__name__, result['records'][0]['errors'][0])

    def test_only_matched_success_advances_metadata_freshness(self):
        good = sm.apply('c', 1, 'e', self.checked(), db=self.db)
        checked_at = good['evidence'][0]['metadata_checked_at']
        body = json.dumps({'message':{'DOI':'10.1234/wrong'}}).encode()
        with patch.object(sm, '_fetch', return_value=(body, 200)):
            bad = sm.inspect(self.e, live=True)
        self.assertTrue(bad['records'][0]['checked_at'])
        current = sm.apply('c', 2, 'e', bad, db=self.db)
        self.assertEqual(current['evidence'][0]['metadata_checked_at'], checked_at)

    def test_update_vocabulary_preserves_raw_and_normalizes_separators(self):
        version = 1
        for raw in ['expression_of_concern', 'Expression-Of-Concern', 'partial_retraction', 'unexpected-vendor-update', 'Retraction']:
            with self.subTest(raw=raw):
                metadata = self.checked(**{'updated-by':[{'DOI':'10.1234/notice', 'type':raw}]})
                evidence = sm.apply('c', version, 'e', metadata, db=self.db)['evidence'][0]
                version += 1
                relation = next(r for r in evidence['metadata_review_required'] if r['raw_type'] == raw)
                self.assertEqual(relation['raw_type'], raw)
                self.assertEqual(relation['type'], raw.lower().replace('_','-'))
                self.assertEqual(bool(evidence.get('retracted')), raw == 'Retraction')

    def test_request_count_matches_dispatch(self):
        samples = [
            ({'doi':'10.1234/a'}, 1),
            ({'url':'https://arxiv.org/abs/1706.03762v1'}, 1),
            ({'doi':'10.1234/a', 'arxiv_id':'1706.03762'}, 2),
            ({'url':'https://example.org/no-identity'}, 0),
            ({'doi':'10.1234/a', 'url':'https://doi.org/10.1234/b'}, 0),
            ({'arxiv_id':'1706.03762', 'url':'https://arxiv.org/abs/1810.04805'}, 0),
            ({'doi':'10.1234/a', 'url':'https://doi.org/10.1234/b', 'arxiv_id':'1706.03762'}, 1),
        ]
        for evidence, expected in samples:
            with self.subTest(evidence=evidence), patch.object(sm, '_fetch', side_effect=OSError('offline')) as fetch:
                self.assertEqual(sm.planned_request_count(evidence), expected)
                fetch.assert_not_called()
                sm.inspect(evidence, live=True)
                self.assertEqual(fetch.call_count, expected)

    def test_request_count_rejects_invalid_evidence(self):
        with self.assertRaisesRegex(ValueError, 'object'): sm.planned_request_count(None)

    def test_redirect_refused(self):
        with self.assertRaisesRegex(ValueError,'redirect'):
            sm._NoRedirect().redirect_request(None,None,302,'',{},'http://127.0.0.1')

    def test_size_limit_fires(self):
        from unittest.mock import MagicMock
        opener=MagicMock(); response=opener.open.return_value.__enter__.return_value
        response.read.return_value=b'x'*(sm.MAX_BYTES+1)
        with patch.object(sm.urllib.request,'build_opener',return_value=opener):
            with self.assertRaisesRegex(ValueError,'size limit'): sm._fetch('https://api.crossref.org/works/10.1234/a')

if __name__ == '__main__': unittest.main()
