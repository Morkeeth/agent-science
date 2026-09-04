"""Exercise decision/version binding and public entry points, without paid APIs."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from clearance import cases, instruments, search
from clearance.mcp_server import handle_tool


class CaseTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        self.db=self.root/'cases.db'
        self.env=patch.dict(os.environ,{'AGENT_SCIENCE_CASES_DB':str(self.db)})
        self.env.start()
        self.cache=patch.object(instruments,'DOCS',self.root/'documents.json');self.cache.start()
        self.search_cache=patch.object(search,'CACHE',self.root/'search.json');self.search_cache.start()
        self.receipts=patch.object(search,'RECEIPTS',self.root/'receipts.jsonl');self.receipts.start()
        self.url='https://example.org/report'
        self.body='Fresh agent sessions reduced the number of repeated errors in our experiment.'
        self.seed(self.body)

    def tearDown(self):
        self.receipts.stop();self.search_cache.stop();self.cache.stop();self.env.stop();self.temp.cleanup()

    def seed(self,text):
        instruments.DOCS.write_text(json.dumps({self.url:{'text':text,'fetched_at':'2026-09-04T00:00:00+00:00'}}))

    def create(self):
        return cases.create('Do fresh agent sessions reduce repeated errors?',sources=[self.url],db=self.db)

    def test_quote_is_a_document_fact_not_an_automatic_recommendation(self):
        data=self.create();e=data['evidence'][0]
        self.assertEqual(e['status'],'QUOTE_VERIFIED');self.assertEqual(e['relation'],'not_assessed')
        self.assertIn(e['quote'],e['snapshot_text']);self.assertEqual(data['decisions'],[])
        self.assertNotIn('snapshot_text',cases.public_view(data)['evidence'][0])

    def test_source_change_flags_bound_decision_and_keeps_original(self):
        data=self.create();eid=data['evidence'][0]['id']
        cases.decide(data['id'],'Try fresh sessions','This source motivates a local test',[eid],db=self.db)
        with patch('clearance.instruments.fetch_public',return_value=(b'Fresh agent sessions increased repeated errors in the replication study.',self.url)):
            new=cases.refresh(data['id'],live=True,db=self.db)
        self.assertEqual(new['version'],2)
        self.assertEqual(new['decisions'][0]['review']['state'],'REVIEW_REQUIRED')
        self.assertEqual(cases.get(data['id'],version=1,db=self.db)['evidence'][0]['snapshot_text'],self.body)
        self.assertEqual(new['decisions'][0]['statement'],'Try fresh sessions')
        self.assertEqual(new['decisions'][0]['review']['changes'][0]['kind'],'source_changed')

    def test_failed_refresh_invalidates_dependency_without_stale_fallback(self):
        data=self.create();cases.decide(data['id'],'Test it','Bound to the quote',[data['evidence'][0]['id']],db=self.db)
        with patch('clearance.instruments.fetch_public',side_effect=TimeoutError):
            new=cases.refresh(data['id'],live=True,db=self.db)
        self.assertEqual(new['evidence'][0]['status'],'UNAVAILABLE')
        self.assertEqual(new['decisions'][0]['review']['state'],'REVIEW_REQUIRED')

    def test_unrelated_source_change_does_not_reopen_decision(self):
        other='https://example.org/other'
        cache=json.loads(instruments.DOCS.read_text());cache[other]={'text':self.body};instruments.DOCS.write_text(json.dumps(cache))
        data=cases.create('Fresh agent sessions',sources=[self.url,other],db=self.db)
        cases.decide(data['id'],'Test','Primary source only',[data['evidence'][0]['id']],db=self.db)
        cache[other]['text']='Fresh agent sessions changed in the separate unrelated study.';instruments.DOCS.write_text(json.dumps(cache))
        new=cases.refresh(data['id'],db=self.db)
        self.assertEqual(new['decisions'][0]['review']['state'],'UNCHANGED_IN_SNAPSHOT')

    def test_cannot_cite_missing_quote_or_other_case(self):
        data=self.create()
        with self.assertRaises(ValueError):cases.decide(data['id'],'Use it','No reason',['unknown'],db=self.db)
        self.seed('This document says nothing about the subject in the question.')
        empty=cases.create('Quantum photocatalysis',sources=[self.url],db=self.db)
        with self.assertRaises(ValueError):cases.decide(empty['id'],'Use it','No quote',[empty['evidence'][0]['id']],db=self.db)

    def test_actual_discovery_attempts_and_no_repo_content_in_queries(self):
        repo=self.root/'repo';repo.mkdir();(repo/'AGENTS.md').write_text('PRIVATE CONTEXT MUST STAY LOCAL')
        def provider(objective,queries,mode):
            self.assertNotIn('PRIVATE',objective)
            return {'results':[{'url':self.url,'title':'A report','excerpts':[self.body]}]},'search-proof'
        with patch.object(search,'_live_search',side_effect=provider) as called:
            data=cases.create('Fresh agent sessions',root=repo,live=True,db=self.db)
        self.assertEqual(called.call_count,3)
        events=[e for e in data['trace'] if e['route']=='parallel']
        self.assertEqual(len(events),3);self.assertTrue(all(e['outcome']=='completed' for e in events))
        self.assertEqual(len(data['evidence']),1) # same source across angles is not three sources
        self.assertEqual(data['repo']['root'],str(repo.resolve()))
        self.assertNotIn('PRIVATE',json.dumps(data))

    def test_mcp_round_trip(self):
        data=json.loads(handle_tool('science_case',{'action':'create','question':'Fresh agent sessions','sources':[self.url]}))
        saved=json.loads(handle_tool('science_case',{'action':'decide','case_id':data['id'],'statement':'Run a local trial','rationale':'Source gives a hypothesis','evidence_ids':[data['evidence'][0]['id']]}))
        self.assertEqual(saved['decisions'][0]['review']['state'],'UNCHANGED_IN_SNAPSHOT')
        self.assertEqual(json.loads(handle_tool('science_case',{'action':'show','case_id':data['id']}))['id'],data['id'])

    def test_cli_reading_saved_case(self):
        data=self.create()
        p=subprocess.run([sys.executable,'-m','clearance','case','show',data['id'],'--db',str(self.db),'--json'],capture_output=True,text=True)
        self.assertEqual(p.returncode,0,p.stderr)
        self.assertEqual(json.loads(p.stdout)['id'],data['id'])

    def test_historical_view_never_contains_future_decisions(self):
        data=self.create();cases.refresh(data['id'],db=self.db)
        cases.decide(data['id'],'Later decision','Version two',[data['evidence'][0]['id']],db=self.db)
        self.assertEqual(cases.get(data['id'],version=1,db=self.db)['decisions'],[])

    def test_long_sentence_quote_survives_refresh(self):
        text=('Unrelated surrounding material '*25)+self.body+(' More context '*30)
        self.seed(text)
        def provider(objective,queries,mode):
            return {'results':[{'url':self.url,'title':'Report','excerpts':[self.body]}]},'search-proof'
        with patch.object(search,'_live_search',side_effect=provider):
            data=cases.create('Fresh agent sessions',live=True,db=self.db)
        cases.decide(data['id'],'Try it','Local test hypothesis',[data['evidence'][0]['id']],db=self.db)
        refreshed=cases.refresh(data['id'],db=self.db)
        self.assertEqual(refreshed['evidence'][0]['quote'],data['evidence'][0]['quote'])
        self.assertEqual(refreshed['decisions'][0]['review']['state'],'UNCHANGED_IN_SNAPSHOT')

    def test_source_drilldown_is_versioned_and_paginated(self):
        data=self.create();eid=data['evidence'][0]['id']
        chunk=cases.source(data['id'],eid,db=self.db,limit=20)
        self.assertEqual(chunk['text'],self.body[:20]);self.assertEqual(chunk['next_offset'],20)
        self.seed('Fresh agent sessions changed in this newer report.')
        cases.refresh(data['id'],db=self.db)
        self.assertEqual(cases.source(data['id'],eid,db=self.db,version=1)['text'],self.body)
        result=json.loads(handle_tool('science_case',{'action':'source','case_id':data['id'],'evidence_id':eid,'version':1,'limit':20}))
        self.assertEqual(result['text'],self.body[:20])
        self.assertEqual(cases.get(data['id'],db=self.db)['freshness']['new_fetches'],0)

    def test_legacy_source_is_not_newly_dated(self):
        instruments.DOCS.write_text(json.dumps({self.url:{'text':self.body}}))
        self.assertIsNone(self.create()['evidence'][0]['fetched_at'])

    def test_offline_case_does_not_fetch(self):
        with patch.object(instruments,'fetch_public',side_effect=AssertionError('network forbidden')):
            data=cases.create('Fresh sessions',sources=['https://example.org/not-cached'],db=self.db)
        self.assertEqual(data['evidence'][0]['status'],'UNAVAILABLE')


class ExperimentTests(unittest.TestCase):
    def test_both_arms_run_pinned_code_under_one_external_acceptance_script(self):
        from clearance.experiments import compare
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);repo=root/'repo';repo.mkdir()
            def git(*args):
                return subprocess.check_output(['git','-C',str(repo),*args],stderr=subprocess.DEVNULL,text=True).strip()
            git('init');git('config','user.name','Test');git('config','user.email','test@example.org')
            (repo/'behavior.py').write_text('def allowed(): return False\n')
            git('add','.');git('commit','-m','baseline');baseline=git('rev-parse','HEAD')
            (repo/'behavior.py').write_text('def allowed(): return True\n')
            git('add','.');git('commit','-m','candidate');candidate=git('rev-parse','HEAD')
            check=root/'check.py';check.write_text('from behavior import allowed\nassert allowed()\n')
            db=root/'cases.db';case=cases.create('Should this behavior be enabled?',root=repo,db=db)
            result=compare(case['id'],repo=repo,baseline=baseline,candidate=candidate,check=check,runs=2,db=db)
            self.assertEqual(result['aggregate']['baseline']['passed'],0)
            self.assertEqual(result['aggregate']['candidate']['passed'],2)
            self.assertEqual(result['pins'],{'baseline':baseline,'candidate':candidate})
            self.assertEqual(git('rev-parse','HEAD'),candidate)
            self.assertEqual(git('status','--porcelain'),'')
            self.assertEqual(len([l for l in git('worktree','list','--porcelain').splitlines() if l.startswith('worktree ')]),1)
            self.assertEqual(len(cases.get(case['id'],db=db)['experiments']),1)
            check.write_text('import pathlib,sys\npathlib.Path(sys.argv[0]).write_text("print(123)\\n")\n')
            mutated=compare(case['id'],repo=repo,baseline=baseline,candidate=candidate,check=check,runs=2,db=db)
            self.assertFalse(mutated['valid'])
            self.assertTrue(all(not r['acceptance_unchanged'] for r in mutated['runs']))
            check.write_text('import subprocess,sys\nsubprocess.Popen([sys.executable,"-c","import time; time.sleep(60)"])\nprint("x"*10000)\n')
            cleaned=compare(case['id'],repo=repo,baseline=baseline,candidate=candidate,check=check,runs=1,db=db)
            self.assertTrue(cleaned['valid'])
            self.assertTrue(all(r['capture_complete'] and r['output_truncated'] for r in cleaned['runs']))
            self.assertTrue(all(len(r['output_tail'])<=2000 for r in cleaned['runs']))
            with self.assertRaises(ValueError):compare(case['id'],repo=repo,baseline=candidate,candidate=candidate,check=check,db=db)


if __name__=='__main__':unittest.main()
