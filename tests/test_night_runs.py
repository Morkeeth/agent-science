"""Controlled provider fixtures: these tests are not live scientific evidence."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from clearance import cases, night_runs


class RunTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.db=str(Path(self.tmp.name)/'cases.db')

    def start(self, **kw):
        return night_runs.start('When does memory help coding?',db=self.db,**kw)

    def proposal(self, run, kind='finish', **action):
        return {'case_version':run['case_version'],'next_action':{'kind':kind,'reason':'fixture research step',**action}}

    def test_start_offline_and_host_finish(self):
        with patch('clearance.research.investigate',side_effect=AssertionError('must not investigate')):
            run=self.start()
        self.assertEqual(run['status'],'awaiting_reasoning')
        self.assertIsNone(cases.get(run['case_id'],db=self.db)['checked_at'])
        result=night_runs.resume(run['id'],proposal=self.proposal(run),db=self.db)
        self.assertEqual(result['status'],'completed')
        self.assertEqual(result['usage']['reasoning_calls'],0)

    def test_stale_and_no_model_stop(self):
        run=self.start()
        proposal=self.proposal(run);proposal['case_version']=0
        with self.assertRaises(ValueError):night_runs.resume(run['id'],proposal=proposal,db=self.db)
        self.assertEqual(night_runs.resume(run['id'],db=self.db)['status'],'awaiting_reasoning')

    def test_adaptive_fixture_provider_and_original_reads(self):
        queries=[]
        def find(provider,query,**kw):
            queries.append(query)
            if len(queries)==1:
                return [cases.search.Candidate('https://fixture.example/original','Fixture original','Memory helped small tasks; repository scale was not tested.')]
            self.assertIn('repository scale',query)
            return [cases.search.Candidate('https://fixture.example/failure','Fixture follow-up','Memory failed to help repository scale tasks in this fixture.')]
        def snapshot(url,**kw):
            text=('Memory helped small tasks; repository scale was not tested.' if url.endswith('original') else
                  'Memory failed to help repository scale tasks in this fixture.')
            return {'text':text,'sha256':cases.digest(text),'cache_hit':True}
        contexts=[]
        def reasoner(ctx):
            contexts.append(ctx)
            run={'case_version':ctx['case_version']}
            if not ctx['evidence']:return self.proposal(run,'search',query='memory original result')
            if len(ctx['evidence'])==1:
                self.assertIn('repository scale was not tested',ctx['evidence'][0]['snapshot_text'])
                return {**self.proposal(run,'search',query='memory repository scale replication failure'),
                        'question_map':[{'id':'scale','question':'Does memory help at repository scale?',
                                         'gap':'Original fixture did not test repository scale','competing_explanation':'small task effects do not transfer','importance':'material'}]}
            self.assertIn('failed to help',ctx['evidence'][1]['snapshot_text'])
            return self.proposal(run)
        run=self.start()
        with patch('clearance.discovery.find',side_effect=find),patch('clearance.cases.instruments.document_snapshot',side_effect=snapshot):
            result=night_runs.resume(run['id'],reasoner=reasoner,db=self.db)
        self.assertEqual(result['status'],'completed')
        self.assertEqual(result['case_version'],3)
        self.assertEqual(len(queries),2)
        self.assertEqual(result['question_map'][0]['id'],'scale')
        self.assertEqual(result['usage']['reasoning_calls'],3)
        self.assertEqual(len(cases.get(run['case_id'],db=self.db)['evidence']),2)

    def test_aggregate_limit_stops_second_run(self):
        policy={'aggregate':{'id':'fixture-budget','limits':dict(discovery_calls=1,document_reads=2,reasoning_calls=0,rounds=1)}}
        a=self.start(policy=policy);b=self.start(policy=policy)
        with patch('clearance.discovery.find',return_value=[]) as find:
            a=night_runs.resume(a['id'],proposal=self.proposal(a,'search',query='fixture original'),db=self.db)
            b=night_runs.resume(b['id'],proposal=self.proposal(b,'search',query='fixture replication'),db=self.db)
        self.assertEqual(find.call_count,1)
        self.assertEqual(b['stop_reason'],'budget exhausted')
        self.assertEqual(b['usage']['discovery_calls'],0)

    def test_live_requires_shared_policy(self):
        a=self.start()
        with patch('clearance.discovery.find',side_effect=AssertionError('no paid call')):
            result=night_runs.resume(a['id'],proposal=self.proposal(a,'search',query='fixture'),live=True,db=self.db)
        self.assertEqual(result['status'],'paused')
        self.assertEqual(result['usage']['discovery_calls'],0)

    def test_unknown_interrupt_never_retries(self):
        a=self.start()
        with patch('clearance.research.investigate',side_effect=KeyboardInterrupt) as invoke:
            with self.assertRaises(KeyboardInterrupt):
                night_runs.resume(a['id'],proposal=self.proposal(a,'search',query='fixture'),db=self.db)
            result=night_runs.resume(a['id'],proposal=self.proposal(a,'search',query='fixture'),db=self.db)
        self.assertEqual(invoke.call_count,1)
        self.assertEqual(result['status'],'needs_reconciliation')
        self.assertEqual(result['usage']['discovery_calls'],1)

    def test_restart_started_operation_is_unknown(self):
        a=self.start()
        night_runs._reserve(a,{'reasoning_calls':1},'reasoning',{},self.db,False)
        with patch('clearance.research.investigate',side_effect=AssertionError('no replay')):
            result=night_runs.resume(a['id'],db=self.db)
        self.assertEqual(result['steps'][0]['state'],'unknown')
        self.assertEqual(result['status'],'needs_reconciliation')

    def test_cancel_preserves_case(self):
        a=self.start()
        result=night_runs.cancel(a['id'],db=self.db)
        self.assertEqual(result['status'],'cancelled')
        self.assertEqual(night_runs.resume(a['id'],db=self.db)['status'],'cancelled')
        self.assertEqual(cases.get(a['case_id'],db=self.db)['version'],1)

    def test_source_instructions_cannot_select_shell(self):
        a=self.start()
        with self.assertRaises(ValueError):night_runs.resume(a['id'],proposal=self.proposal(a,'shell',command='touch /tmp/no'),db=self.db)
        self.assertEqual(night_runs.get(a['id'],db=self.db)['steps'],[])



    def test_challenge_revises_fixture_answer_from_new_evidence(self):
        from clearance import synthesis
        run=self.start()
        texts={'https://fixture.example/one':'Memory improves outcomes for small coding tasks in this fixture.',
               'https://fixture.example/two':'Memory reduces outcomes for large coding tasks in this fixture.'}
        def snapshot(url,**kw):
            return {'text':texts[url],'sha256':cases.digest(texts[url]),'cache_hit':True}
        with patch('clearance.cases.instruments.document_snapshot',side_effect=snapshot):
            run=night_runs.resume(run['id'],proposal=self.proposal(run,'read',urls=['https://fixture.example/one']),db=self.db)
        data=cases.get(run['case_id'],db=self.db)
        finding={'statement':'Memory helps on the small fixture task.', 'relation':'supports','rationale':'This authored fixture finding applies only to the small task.',
                 'evidence_id':data['evidence'][0]['id'],'quote':texts['https://fixture.example/one'],
                 'strongest_challenge':'The effect may reverse on large coding tasks.',
                 'what_would_change':'A large-task failure would narrow the conclusion.'}
        run=night_runs.resume(run['id'],proposal={**self.proposal(run),'findings':[finding]},db=self.db)
        challenge=night_runs.start('When does memory help coding?',case_id=run['case_id'],challenge=True,db=self.db)
        self.assertEqual(challenge['base_case_version'],run['case_version'])
        self.assertIn('large coding tasks',challenge['challenges'][0])
        with patch('clearance.cases.instruments.document_snapshot',side_effect=snapshot):
            challenge=night_runs.resume(challenge['id'],proposal=self.proposal(challenge,'read',urls=['https://fixture.example/two']),db=self.db)
        data=cases.get(run['case_id'],db=self.db)
        second={**finding,'statement':'The fixture effect does not transfer to large coding tasks.',
                'relation':'different_scope','evidence_id':data['evidence'][1]['id'],'quote':texts['https://fixture.example/two']}
        challenge=night_runs.resume(challenge['id'],proposal={**self.proposal(challenge),'findings':[second]},db=self.db)
        old=synthesis.build(cases.get(run['case_id'],version=run['case_version'],db=self.db))
        new=synthesis.build(cases.get(run['case_id'],db=self.db))
        self.assertEqual(len(old['conclusions']),1)
        self.assertEqual(len(new['conclusions']),2)
        self.assertEqual(challenge['status'],'completed')

    def test_cancel_during_provider_does_not_schedule_next_call(self):
        import threading
        entered=threading.Event();release=threading.Event();out=[]
        run=self.start()
        def find(*a,**kw):
            entered.set()
            self.assertTrue(release.wait(3))
            return []
        def reasoner(ctx):
            return self.proposal({'case_version':ctx['case_version']},'search',query='fixture')
        def worker():
            out.append(night_runs.resume(run['id'],reasoner=reasoner,db=self.db))
        with patch('clearance.discovery.find',side_effect=find) as calls:
            thread=threading.Thread(target=worker);thread.start()
            self.assertTrue(entered.wait(3))
            stopped=night_runs.cancel(run['id'],db=self.db)
            self.assertEqual(stopped['status'],'cancelled')
            release.set();thread.join(3)
        self.assertFalse(thread.is_alive())
        self.assertEqual(calls.call_count,1)
        self.assertEqual(out[0]['status'],'cancelled')
        self.assertEqual(out[0]['steps'][-1]['state'],'completed')

    def test_separate_model_adapter_requires_configuration(self):
        from clearance import reasoning
        with patch.dict('os.environ',{},clear=True),patch('urllib.request.urlopen',side_effect=AssertionError('no implicit paid model')):
            with self.assertRaises(ValueError):reasoning.configured()
        with self.assertRaises(ValueError):reasoning.GeminiReasoner(model='x:runShell',api_key='fixture')

    def test_context_has_prior_claims_and_explicit_truncation(self):
        from clearance import synthesis
        run=self.start()
        data=cases.get(run['case_id'],db=self.db)
        text='Memory improves outcomes on this fixture task. '+('extra source content. '*1000)
        with patch('clearance.cases.instruments.document_snapshot',return_value={'text':text,'sha256':cases.digest(text),'cache_hit':True}):
            run=night_runs.resume(run['id'],proposal=self.proposal(run,'read',urls=['https://fixture.example/source']),db=self.db)
        data=cases.get(run['case_id'],db=self.db)
        synthesis.apply(data['id'],data['version'],{'findings':[{'statement':'Memory improves this fixture task.',
            'relation':'supports','rationale':'This is an authored interpretation of a controlled fixture.',
            'evidence_id':data['evidence'][0]['id'],'quote':'Memory improves outcomes on this fixture task.',
            'strongest_challenge':'Larger coding tasks could fail to benefit.',
            'what_would_change':'A matched experiment could show the opposite result.'}]},db=self.db)
        next_run=self.start(case_id=data['id'])
        ctx=night_runs.context(next_run['id'],db=self.db)
        self.assertTrue(ctx['prior_research'][0]['claims'])
        self.assertTrue(ctx['current_answer']['conclusions'])
        self.assertTrue(ctx['evidence'][0]['snapshot_truncated'])
        self.assertEqual(len(ctx['evidence'][0]['snapshot_text']),12000)
        self.assertEqual(night_runs.get(run['id'],db=self.db)['observed_usage']['online_fetches'],0)
        self.assertEqual(night_runs.get(run['id'],db=self.db)['observed_usage']['cached_reads'],1)

    def test_repeated_query_stops_without_repeat_provider_call(self):
        run=self.start()
        def reasoner(ctx):return self.proposal({'case_version':ctx['case_version']},'search',query='fixture same query')
        with patch('clearance.discovery.find',return_value=[]) as calls:
            result=night_runs.resume(run['id'],reasoner=reasoner,db=self.db)
        self.assertEqual(calls.call_count,1)
        self.assertIn('diminishing new evidence',result['stop_reason'])

    def test_source_url_rejects_private_network_before_operation(self):
        run=self.start()
        with self.assertRaises(ValueError):
            night_runs.resume(run['id'],proposal=self.proposal(run,'read',urls=['http://127.0.0.1/private']),db=self.db)
        self.assertEqual(night_runs.get(run['id'],db=self.db)['steps'],[])

    def test_missing_provider_access_is_visible_to_next_reasoning_step(self):
        run=self.start()
        def find(provider,query,**kw):
            kw['trace'].append({'route':provider,'outcome':'unavailable','reason':'fixture missing credentials'})
            return []
        with patch('clearance.discovery.find',side_effect=find):
            run=night_runs.resume(run['id'],proposal=self.proposal(run,'search',query='fixture missing access'),db=self.db)
        ctx=night_runs.context(run['id'],db=self.db)
        self.assertEqual(ctx['steps'][-1]['observed_events'][0]['outcome'],'unavailable')
        self.assertEqual(ctx['observed_usage']['provider_completed'],0)

    def test_configured_adapter_transport_fixture_and_unknown_cost(self):
        import io
        from clearance import reasoning
        run=self.start(policy={'aggregate':{'id':'adapter-fixture','limits':dict(discovery_calls=0,document_reads=0,reasoning_calls=1,rounds=0)}})
        proposal=self.proposal(run)
        payload={'candidates':[{'content':{'parts':[{'text':json.dumps(proposal)}]}}]}
        adapter=reasoning.GeminiReasoner(model='fixture-model',api_key='fixture-key')
        def urlopen(request,**kwargs):
            sent=json.loads(request.data)
            self.assertEqual(sent['generationConfig']['responseMimeType'],'application/json')
            self.assertNotIn('tools',sent)
            self.assertIn('untrusted data',sent['systemInstruction']['parts'][0]['text'])
            return io.BytesIO(json.dumps(payload).encode())
        with patch('urllib.request.urlopen',side_effect=urlopen) as network:
            result=night_runs.resume(run['id'],reasoner=adapter,db=self.db)
        self.assertEqual(network.call_count,1)
        self.assertEqual(result['status'],'completed')
        self.assertEqual(result['observed_usage']['reasoning_responses'],1)
        self.assertIsNone(result['billing'])

    def test_case_mutations_from_separate_runs_are_serial_and_version_bound(self):
        import threading
        first=self.start();second=self.start(case_id=first['case_id'])
        entered=threading.Event();release=threading.Event();results=[];errors=[]
        def find(*a,**kw):
            entered.set();self.assertTrue(release.wait(3));return []
        def worker(run):
            try:results.append(night_runs.resume(run['id'],proposal=self.proposal(run,'search',query='fixture'),db=self.db))
            except ValueError as exc:errors.append(str(exc))
        with patch('clearance.discovery.find',side_effect=find) as provider:
            one=threading.Thread(target=worker,args=(first,));two=threading.Thread(target=worker,args=(second,))
            one.start();self.assertTrue(entered.wait(3));two.start();release.set();one.join(3);two.join(3)
        self.assertFalse(one.is_alive() or two.is_alive())
        self.assertEqual(provider.call_count,1)
        self.assertEqual(len(results),1)
        self.assertEqual(len(errors),1)
        self.assertIn('case changed outside this run',errors[0])

    def test_invalid_quote_rejects_then_accepts_corrected_proposal(self):
        run=self.start(policy={'aggregate':{'id':'validation-budget','limits':dict(discovery_calls=1,document_reads=3,reasoning_calls=0,rounds=2)}})
        text='Memory improves outcomes on a narrow controlled fixture task.'
        with patch('clearance.cases.instruments.document_snapshot',return_value={'text':text,'sha256':cases.digest(text),'cache_hit':True}):
            run=night_runs.resume(run['id'],proposal=self.proposal(run,'read',urls=['https://fixture.example/one']),db=self.db)
        data=cases.get(run['case_id'],db=self.db)
        finding={'statement':'Memory improves the narrow fixture task.','relation':'supports',
                 'rationale':'Authored fixture interpretation limited to this single task.',
                 'evidence_id':data['evidence'][0]['id'],'quote':'A fabricated quotation that never occurred.',
                 'strongest_challenge':'Other task scales may show the opposite effect.',
                 'what_would_change':'A controlled failure on this task would change the answer.'}
        proposal={**self.proposal(run,'search',query='fixture replication'),'findings':[finding]}
        with patch('clearance.discovery.find',return_value=[]) as call:
            with self.assertRaises(ValueError):night_runs.resume(run['id'],proposal=proposal,db=self.db)
            rejected=night_runs.get(run['id'],db=self.db)
            self.assertEqual(rejected['status'],'awaiting_reasoning')
            self.assertEqual(rejected['steps'][-1]['state'],'rejected')
            self.assertEqual(rejected['usage']['discovery_calls'],0)
            self.assertEqual(cases.get(run['case_id'],db=self.db)['version'],run['case_version'])
            self.assertEqual(call.call_count,0)
            finding['quote']=text
            corrected=night_runs.resume(run['id'],proposal=proposal,db=self.db)
        self.assertEqual(call.call_count,1)
        self.assertEqual(corrected['case_version'],run['case_version']+2)
        self.assertEqual(corrected['steps'][-1]['state'],'completed')

    def test_repo_start_includes_general_and_same_repo_only(self):
        from clearance import research, research_search
        here=Path(self.tmp.name)/'here';other=Path(self.tmp.name)/'other'
        here.mkdir();other.mkdir()
        general=research.import_report('Memory for coding','A general controlled fixture.',db=self.db)
        same=research.import_report('Memory for coding','A repository controlled fixture.',root=here,db=self.db)
        unrelated=research.import_report('Memory for coding','An unrelated controlled fixture.',root=other,db=self.db)
        run=self.start(root=here)
        found={row['case_id'] for row in run['prior_research']['cases']}
        self.assertIn(general['id'],found)
        self.assertIn(same['id'],found)
        self.assertNotIn(unrelated['id'],found)
        explicit=research_search.find('memory coding',root=here,db=self.db)
        self.assertNotIn(general['id'],{row['case_id'] for row in explicit['cases']})
        self.assertIn('engine-dispatched operations only',run['usage_basis'])
        self.assertIn('Excludes host reasoning and separate science_case tool reads',run['usage_basis'])

    def test_repo_start_scans_past_unrelated_high_ranked_page(self):
        import copy
        from clearance import research
        here=Path(self.tmp.name)/'here';other=Path(self.tmp.name)/'other'
        here.mkdir();other.mkdir()
        template=research.import_report('Memory coding help','Memory coding help fixture.',root=other,db=self.db)
        for index in range(105):
            data={k:copy.deepcopy(v) for k,v in template.items() if k not in ('decisions','experiments','coverage','freshness')}
            data['id']='unrelated'+str(index)
            cases._save(data,db=self.db)
        general=research.import_report('Memory','General fixture.',db=self.db)
        same=research.import_report('Memory','Local fixture.',root=here,db=self.db)
        run=self.start(root=here)
        found={row['case_id'] for row in run['prior_research']['cases']}
        self.assertIn(general['id'],found)
        self.assertIn(same['id'],found)
        self.assertTrue(all(row.get('root') in (None,str(here.resolve())) for row in run['prior_research']['cases']))


if __name__=='__main__':unittest.main()
