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

    def test_completed_model_response_survives_before_action_checkpoint(self):
        run=self.start()
        from unittest.mock import Mock
        reasoner=Mock(return_value=self.proposal(run))
        reasoner.external=False; reasoner.model='controlled-fixture'
        with patch('clearance.night_runs._validate',side_effect=KeyboardInterrupt):
            with self.assertRaises(KeyboardInterrupt):
                night_runs.resume(run['id'],reasoner=reasoner,db=self.db)
        saved=night_runs.get(run['id'],db=self.db)
        self.assertEqual(saved['steps'][-1]['state'],'completed')
        result=night_runs.resume(run['id'],reasoner=reasoner,db=self.db)
        self.assertEqual(result['status'],'completed')
        self.assertEqual(reasoner.call_count,1)
        self.assertEqual(result['usage']['reasoning_calls'],1)

    def test_local_store_routes_do_not_enter_adapter_request(self):
        import io
        from clearance import reasoning
        adapter=reasoning.GeminiReasoner(model='fixture',api_key='fixture')
        context={'db':'PRIVATE_STORE_SENTINEL','evidence':[{'url':'https://example.org/paper',
            'inspect_more':{'db':'PRIVATE_STORE_SENTINEL','evidence_id':'e'}}]}
        def transport(request, **kwargs):
            self.assertNotIn(b'PRIVATE_STORE_SENTINEL',request.data)
            self.assertIn(b'https://example.org/paper',request.data)
            return io.BytesIO(json.dumps({'candidates':[{'content':{'parts':[{'text':'{}'}]}}]}).encode())
        with patch('urllib.request.urlopen',side_effect=transport):adapter(context)
        self.assertEqual(context['db'],'PRIVATE_STORE_SENTINEL')

    def test_malformed_aggregate_has_validation_error(self):
        for limits in (None, 1, [], 'not limits'):
            with self.assertRaises(ValueError):self.start(policy={'aggregate':{'id':'bad','limits':limits}})

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
        from clearance.research_policy import approve
        approve({'aggregate':run['aggregate']},db=self.db)
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

    def test_budget_stopped_run_accepts_only_explicit_host_finish(self):
        run=self.start(policy={'rounds':1})
        with patch('clearance.cases.instruments.document_snapshot',return_value=None):
            run=night_runs.resume(run['id'],proposal=self.proposal(run,'read',urls=['https://fixture.example/a']),db=self.db)
            stopped=night_runs.resume(run['id'],proposal=self.proposal(run,'read',urls=['https://fixture.example/b']),db=self.db)
        self.assertEqual(stopped['status'],'stopped')
        usage=stopped['usage'].copy()
        with patch('clearance.research.investigate',side_effect=AssertionError('no new research')),patch('clearance.reasoning.GeminiReasoner.__call__',side_effect=AssertionError('no model')):
            unchanged=night_runs.resume(run['id'],reasoner=lambda ctx: self.fail('must not reason'),db=self.db)
            self.assertEqual(unchanged['status'],'stopped')
            result=night_runs.resume(run['id'],proposal={**self.proposal(stopped),'findings':[{
                'statement':'The fixture question remains unresolved.','relation':'unresolved','rationale':'No accessible fixture evidence was inspected.'}]},db=self.db)
        self.assertEqual(result['status'],'completed')
        self.assertEqual(result['usage'],usage)
        self.assertEqual(result['stops'][0]['reason'],'budget exhausted')
        self.assertEqual(cases.get(run['case_id'],db=self.db)['claims'][0]['statement'],'The fixture question remains unresolved.')

    def test_diminishing_stop_keeps_map_and_can_finish(self):
        run=self.start()
        proposal=self.proposal(run,'search',query='repeat fixture')
        proposal['question_map']=[{'id':'remaining','question':'Scope?','gap':'Missing failure evidence',
                                  'competing_explanation':'Different task scope','importance':'material'}]
        with patch('clearance.discovery.find',return_value=[]):
            run=night_runs.resume(run['id'],proposal=proposal,db=self.db)
            proposal['case_version']=run['case_version']
            stopped=night_runs.resume(run['id'],proposal=proposal,db=self.db)
        self.assertEqual(stopped['status'],'stopped')
        result=night_runs.resume(run['id'],proposal=self.proposal(stopped),db=self.db)
        self.assertEqual(result['status'],'completed')
        self.assertEqual(result['question_map'],proposal['question_map'])
        self.assertIn('diminishing',result['stops'][0]['reason'])

    def test_cancel_preserves_completed_and_unknown_states(self):
        run=self.start()
        done=night_runs.resume(run['id'],proposal=self.proposal(run),db=self.db)
        self.assertEqual(night_runs.cancel(run['id'],db=self.db),done)
        run=self.start()
        with patch('clearance.research.investigate',side_effect=OSError('fixture interruption')):
            with self.assertRaises(OSError):night_runs.resume(run['id'],proposal=self.proposal(run,'search',query='uncertain fixture'),db=self.db)
        unknown=night_runs.get(run['id'],db=self.db)
        self.assertEqual(night_runs.cancel(run['id'],db=self.db),unknown)
        self.assertEqual(unknown['status'],'needs_reconciliation')

    def test_invalid_model_output_is_saved_rejected_and_not_replayed(self):
        run=self.start()
        with self.assertRaises(ValueError):
            night_runs.resume(run['id'],reasoner=lambda ctx:self.proposal(run,'shell'),db=self.db)
        rejected=night_runs.get(run['id'],db=self.db)
        self.assertEqual(rejected['status'],'awaiting_reasoning')
        self.assertTrue(rejected['steps'][-1]['proposal_rejected'])
        self.assertEqual(rejected['usage']['reasoning_calls'],1)
        self.assertEqual(night_runs.resume(run['id'],db=self.db)['status'],'awaiting_reasoning')
        done=night_runs.resume(run['id'],proposal=self.proposal(run),db=self.db)
        self.assertEqual(done['status'],'completed')
        self.assertEqual(done['usage']['reasoning_calls'],1)

    def test_reconcile_requires_ack_and_current_case_and_never_replays(self):
        from clearance import research
        run=self.start()
        nodes=[{'id':'scope','question':'Scope?','gap':'Large tasks untested',
                'competing_explanation':'Different task scope','importance':'material'}]
        with patch('clearance.cases.instruments.document_snapshot',return_value=None):
            run=night_runs.resume(run['id'],proposal={**self.proposal(run,'read',urls=['https://fixture.example/known']),'question_map':nodes},db=self.db)
        original=research.investigate
        def committed_then_interrupted(*args,**kwargs):
            original(*args,**kwargs)
            raise OSError('fixture response lost after commit')
        with patch('clearance.discovery.find',return_value=[]),patch('clearance.research.investigate',side_effect=committed_then_interrupted):
            with self.assertRaises(OSError):night_runs.resume(run['id'],proposal=self.proposal(run,'search',query='unknown fixture'),db=self.db)
        unknown=night_runs.get(run['id'],db=self.db)
        op=unknown['steps'][-1]['id'];usage=unknown['usage'].copy()
        current=cases.get(run['case_id'],db=self.db)
        ctx=night_runs.context(run['id'],db=self.db)
        self.assertTrue(ctx['reconciliation']['required'])
        self.assertEqual(ctx['reconciliation']['operation_ids'],[op])
        with self.assertRaises(ValueError):night_runs.reconcile(run['id'],operation_id=op,case_version=current['version'],acknowledgement='',db=self.db)
        with self.assertRaises(ValueError):night_runs.reconcile(run['id'],operation_id=op,case_version=run['case_version'],acknowledgement='retain-reservation-and-do-not-retry',db=self.db)
        acknowledged=night_runs.reconcile(run['id'],operation_id=op,case_version=current['version'],acknowledgement='retain-reservation-and-do-not-retry',db=self.db)
        self.assertEqual(acknowledged['steps'][-1]['state'],'unknown')
        self.assertEqual(acknowledged['usage'],usage)
        self.assertEqual(acknowledged['question_map'],nodes)
        self.assertEqual(acknowledged['case_version'],current['version'])
        with patch('clearance.discovery.find',side_effect=AssertionError('unknown replay prohibited')):
            unchanged=night_runs.resume(run['id'],reasoner=lambda ctx:self.fail('fresh host proposal required'),db=self.db)
            self.assertTrue(unchanged['host_proposal_required'])
            replay=self.proposal(acknowledged,'search',query='unknown fixture')
            replay['next_action']['reason']='A changed reason must not bypass the signature.'
            with self.assertRaises(ValueError):night_runs.resume(run['id'],proposal=replay,db=self.db)
            result=night_runs.resume(run['id'],proposal=self.proposal(acknowledged),db=self.db)
        self.assertEqual(result['status'],'completed')
        self.assertEqual(result['usage'],usage)
        self.assertEqual(result['question_map'],nodes)

    def test_reconcile_lost_model_response_requires_fresh_host_proposal(self):
        run=self.start()
        def lost(ctx):raise OSError('fixture missing model response')
        with self.assertRaises(OSError):night_runs.resume(run['id'],reasoner=lost,db=self.db)
        unknown=night_runs.get(run['id'],db=self.db)
        ack=night_runs.reconcile(run['id'],operation_id=unknown['steps'][-1]['id'],case_version=run['case_version'],acknowledgement='retain-reservation-and-do-not-retry',db=self.db)
        night_runs.resume(run['id'],reasoner=lambda ctx:self.fail('must not retry missing model response'),db=self.db)
        done=night_runs.resume(run['id'],proposal=self.proposal(ack),db=self.db)
        self.assertEqual(done['usage']['reasoning_calls'],1)
        self.assertEqual(done['steps'][0]['state'],'unknown')

    def test_unavailable_source_reason_survives_reasoning_context(self):
        run=self.start()
        with patch('clearance.cases.instruments.document_snapshot',return_value=None):
            run=night_runs.resume(run['id'],proposal=self.proposal(run,'read',urls=['https://fixture.example/absent']),db=self.db)
        ctx=night_runs.context(run['id'],db=self.db)
        self.assertEqual(ctx['evidence'][0]['status'],'UNAVAILABLE')
        self.assertIn('absent from local document cache; web was not checked',ctx['evidence'][0]['reason'])

    def test_invalid_start_leaves_no_case_run_or_aggregate_rows(self):
        policy={'aggregate':{'id':'new-policy','limits':dict(discovery_calls=1,document_reads=2,reasoning_calls=1,rounds=1)}}
        for question in ('','How should we do it'):
            with self.assertRaises(ValueError):night_runs.start(question,policy=policy,db=self.db)
        with night_runs._connect(self.db) as con:
            for table in ('cases','night_runs','night_policy'):
                self.assertEqual(con.execute('SELECT COUNT(*) FROM '+table).fetchone()[0],0)
        with self.assertRaises(ValueError):night_runs.start('memory',root=Path(self.tmp.name)/'absent',policy=policy,db=self.db)
        with night_runs._connect(self.db) as con:
            self.assertEqual(con.execute('SELECT COUNT(*) FROM night_policy').fetchone()[0],0)

    def test_confirmed_offline_skip_releases_reservations_with_audit(self):
        policy={'aggregate':{'id':'offline-shared','limits':dict(discovery_calls=1,document_reads=2,reasoning_calls=0,rounds=1)}}
        run=self.start(policy=policy)
        def skipped(provider,query,**kwargs):
            kwargs['trace'].append({'route':provider,'outcome':'skipped','reason':'live search disabled'})
            return []
        with patch('clearance.discovery.find',side_effect=skipped):
            first=night_runs.resume(run['id'],proposal=self.proposal(run,'search',query='first offline fixture'),db=self.db)
            second=night_runs.resume(run['id'],proposal=self.proposal(first,'search',query='second offline fixture'),db=self.db)
        self.assertEqual(first['usage'],dict.fromkeys(night_runs.DEFAULTS,0))
        self.assertEqual(second['usage'],dict.fromkeys(night_runs.DEFAULTS,0))
        self.assertEqual(second['case_version'],3)
        self.assertTrue(second['steps'][0]['reservation_released'])
        self.assertEqual(second['observed_usage']['provider_completed'],0)
        self.assertEqual(second['steps'][1]['observed_events'][0]['outcome'],'skipped')
        with night_runs._connect(self.db) as con:
            usage=json.loads(con.execute('SELECT usage FROM night_policy').fetchone()[0])
        self.assertEqual(usage,dict.fromkeys(night_runs.DEFAULTS,0))

    def test_existing_source_paging_reveals_late_passage_without_fetch(self):
        from clearance import synthesis
        run=self.start()
        text='Memory fixture introduction. '+('Initial source text. '*800)+'Late falsifier: memory fails on larger coding tasks.'
        with patch('clearance.cases.instruments.document_snapshot',return_value={'text':text,'sha256':cases.digest(text),'cache_hit':True}):
            run=night_runs.resume(run['id'],proposal=self.proposal(run,'read',urls=['https://fixture.example/long']),db=self.db)
        self.assertNotIn('Late falsifier',night_runs.context(run['id'],db=self.db)['evidence'][0]['snapshot_text'])
        version=run['case_version'];rounds=run['usage']['rounds']
        with patch('clearance.research.investigate',side_effect=AssertionError('paging must not investigate')),patch('clearance.cases.instruments.document_snapshot',side_effect=AssertionError('paging must not fetch')):
            run=night_runs.resume(run['id'],proposal=self.proposal(run,'read',urls=['https://fixture.example/long'],offset=12000,limit=12000),live=True,db=self.db)
        page=night_runs.context(run['id'],db=self.db)['evidence'][0]
        self.assertIn('Late falsifier',page['snapshot_text'])
        self.assertEqual(page['snapshot_offset'],12000)
        self.assertFalse(page['has_more'])
        self.assertIsNone(page['inspect_more']['offset'])
        self.assertEqual(run['case_version'],version)
        self.assertEqual(run['usage']['rounds'],rounds)
        self.assertEqual(run['observed_usage']['online_fetches'],0)
        self.assertEqual(run['observed_usage']['cached_reads'],2)
        finding={'statement':'The fixture effect fails on larger coding tasks.','relation':'different_scope',
                 'rationale':'The late source passage limits the task scope.',
                 'evidence_id':page['id'],'quote':'Late falsifier: memory fails on larger coding tasks.',
                 'strongest_challenge':'A matched larger-task replication could reverse this observation.',
                 'what_would_change':'A matched success on larger tasks would change this interpretation.'}
        run=night_runs.resume(run['id'],proposal={**self.proposal(run),'findings':[finding]},db=self.db)
        self.assertEqual(run['status'],'completed')
        self.assertTrue(synthesis.build(cases.get(run['case_id'],db=self.db))['conclusions'])

    def test_paging_requires_valid_existing_snapshot_and_bounded_offsets(self):
        run=self.start()
        for args in ({'offset':-1},{'offset':True},{'offset':0,'limit':12001},{'offset':0}):
            with self.assertRaises(ValueError):
                night_runs.resume(run['id'],proposal=self.proposal(run,'read',urls=['https://fixture.example/missing'],**args),db=self.db)
        self.assertEqual(night_runs.get(run['id'],db=self.db)['steps'],[])
        text='A small fixture snapshot with relevant memory text.'
        with patch('clearance.cases.instruments.document_snapshot',return_value={'text':text,'sha256':cases.digest(text),'cache_hit':True}):
            run=night_runs.resume(run['id'],proposal=self.proposal(run,'read',urls=['https://fixture.example/small']),db=self.db)
        with self.assertRaises(ValueError):
            night_runs.resume(run['id'],proposal=self.proposal(run,'read',urls=['https://fixture.example/small'],offset=len(text)+1),db=self.db)
        self.assertEqual(len(night_runs.get(run['id'],db=self.db)['steps']),1)

    def test_canonical_repeat_signature_ignores_reason(self):
        run=self.start()
        with patch('clearance.discovery.find',return_value=[]) as find:
            run=night_runs.resume(run['id'],proposal=self.proposal(run,'search',query='same fixture'),db=self.db)
            proposal=self.proposal(run,'search',query='same fixture',providers=['parallel'])
            proposal['next_action']['reason']='A new reason does not make a new query.'
            run=night_runs.resume(run['id'],proposal=proposal,db=self.db)
        self.assertEqual(find.call_count,1)
        self.assertEqual(run['status'],'stopped')

    def test_stale_sibling_show_has_no_awaiting_reasoning_state(self):
        first=self.start();second=self.start(case_id=first['case_id'])
        with patch('clearance.discovery.find',return_value=[]):
            first=night_runs.resume(first['id'],proposal=self.proposal(first,'search',query='fixture'),db=self.db)
        shown=night_runs.get(second['id'],db=self.db)
        self.assertEqual(shown['status'],'stale')
        self.assertIn('inspect the current case',shown['stop_reason'])
        with self.assertRaises(ValueError):night_runs.resume(second['id'],proposal=self.proposal(second),db=self.db)
        self.assertEqual(night_runs.get(second['id'],db=self.db)['status'],'stale')

    def test_received_invalid_adapter_json_is_recoverable_known_outcome(self):
        import io
        from clearance import reasoning
        from clearance.research_policy import approve
        run=self.start(policy={'aggregate':{'id':'invalid-response','limits':dict(discovery_calls=0,document_reads=0,reasoning_calls=1,rounds=0)}})
        approve({'aggregate':run['aggregate']},db=self.db)
        adapter=reasoning.GeminiReasoner(model='fixture',api_key='fixture')
        with patch('urllib.request.urlopen',return_value=io.BytesIO(b'not valid JSON')):
            with self.assertRaises(reasoning.ReasoningResponseError):night_runs.resume(run['id'],reasoner=adapter,db=self.db)
        saved=night_runs.get(run['id'],db=self.db)
        self.assertEqual(saved['status'],'awaiting_reasoning')
        self.assertEqual(saved['steps'][0]['state'],'completed')
        self.assertTrue(saved['steps'][0]['response_invalid'])
        self.assertEqual(saved['observed_usage']['reasoning_responses'],1)
        with patch('urllib.request.urlopen',side_effect=AssertionError('no implicit retry')):
            done=night_runs.resume(run['id'],proposal=self.proposal(saved),db=self.db)
        self.assertEqual(done['status'],'completed')
        self.assertEqual(done['usage']['reasoning_calls'],1)

    def test_caller_policy_is_not_live_authorization(self):
        from clearance.research_policy import approve
        policy={'aggregate':{'id':'unapproved-policy','limits':dict(discovery_calls=8,document_reads=20,reasoning_calls=12,rounds=3)}}
        run=self.start(policy=policy)
        with patch('clearance.discovery.find',return_value=[]) as find:
            denied=night_runs.resume(run['id'],proposal=self.proposal(run,'search',query='fixture'),live=True,db=self.db)
            self.assertEqual(denied['status'],'paused')
            self.assertIn('operator-approved',denied['stop_reason'])
            self.assertEqual(find.call_count,0)
            self.assertEqual(denied['usage']['discovery_calls'],0)
            approve(policy,db=self.db)
            accepted=night_runs.resume(run['id'],proposal=self.proposal(run,'search',query='fixture'),live=True,db=self.db)
        self.assertEqual(find.call_count,1)
        self.assertEqual(accepted['usage']['discovery_calls'],1)

    def test_paging_selects_source_beyond_initial_context_window(self):
        run=self.start()
        data=cases.get(run['case_id'],db=self.db)
        data['version']+=1
        data['evidence']=[{'id':'fixture-'+str(i),'url':'https://fixture.example/'+str(i),
            'title':'Fixture source','status':'QUOTE_VERIFIED','quote':'Memory fixture source '+str(i)+'.',
            'snapshot_text':'Memory fixture source '+str(i)+'.','snapshot_hash':str(i),
            'relation':'not_assessed','kind':'research','angle':'provided'} for i in range(42)]
        cases._save(data,db=self.db)
        run=self.start(case_id=data['id'])
        before=night_runs.context(run['id'],db=self.db)
        self.assertNotIn('fixture-41',{e['id'] for e in before['evidence']})
        with patch('clearance.research.investigate',side_effect=AssertionError('no fetch for existing source page')):
            run=night_runs.resume(run['id'],proposal=self.proposal(run,'read',urls=['https://fixture.example/41'],offset=0),db=self.db)
        after=night_runs.context(run['id'],db=self.db)
        self.assertEqual(after['evidence'][0]['id'],'fixture-41')
        self.assertEqual(after['truncation']['evidence_total'],42)
        self.assertEqual(after['truncation']['evidence_included'],40)


if __name__=='__main__':unittest.main()
