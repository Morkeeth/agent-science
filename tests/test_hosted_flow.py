"""Real HTTP + SQLite storage checks; provider effects are isolated fixtures."""
import hashlib
import http.client
import json
import os
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import patch
from http.server import HTTPServer

from clearance import cases
from cloud.case_auth import Auth
from cloud.case_budget import Budget, Rejected
from cloud.case_storage import WorkspaceStore
from cloud.service import Handler

TOKEN_A = 'a'*48
TOKEN_B = 'b'*48
CONFIG = {'session_key': 's'*48, 'users': {'alice': hashlib.sha256(TOKEN_A.encode()).hexdigest(), 'bob': hashlib.sha256(TOKEN_B.encode()).hexdigest()}}
ORIGIN = 'http://127.0.0.1:8769'


class HostedFlow(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.env = patch.dict(os.environ, {
            'AGENT_SCIENCE_HOSTED':'1', 'AGENT_SCIENCE_ALLOW_HTTP':'1',
            'AGENT_SCIENCE_PUBLIC_ORIGIN':ORIGIN, 'AGENT_SCIENCE_ACCESS_CONFIG':json.dumps(CONFIG),
            'AGENT_SCIENCE_WORKSPACE_DIR':self.temp.name,
            'AGENT_SCIENCE_DAILY_RESEARCH_LIMIT':'2','AGENT_SCIENCE_GLOBAL_RESEARCH_LIMIT':'3'},clear=False)
        self.env.start()
        self.server = HTTPServer(('127.0.0.1',0), Handler)
        self.thread = threading.Thread(target=self.server.serve_forever,daemon=True)
        self.thread.start()

    def tearDown(self):
        self.server.shutdown(); self.server.server_close(); self.thread.join()
        self.env.stop(); self.temp.cleanup()

    def request(self, method, path, data=None, *, token=TOKEN_A, headers=None, raw=None):
        conn = http.client.HTTPConnection('127.0.0.1',self.server.server_port,timeout=10)
        h = {'Content-Type':'application/json'}
        if token: h['Authorization']='Bearer '+token
        h.update(headers or {})
        body = raw if raw is not None else json.dumps(data).encode() if data is not None else None
        conn.request(method,path,body,h)
        response=conn.getresponse(); code=response.status; fields=dict(response.getheaders()); text=response.read().decode()
        conn.close()
        return code,fields,json.loads(text) if 'application/json' in fields.get('Content-Type','') else text

    def create(self,rid='create-request-0001'):
        return self.request('POST','/api/cases',{'request_id':rid,'question':'What evidence supports typed tool inputs?','live':False})

    def test_anonymous_cannot_read_or_run_legacy_or_new(self):
        for method,path in [('GET','/api/cases'),('POST','/api/cases'),('POST','/search'),('POST','/clear')]:
            self.assertEqual(self.request(method,path,{},token=None)[0],401)
        self.assertEqual(self.request('GET','/stats',token=None)[0],303)
        self.assertEqual(self.request('POST','/search',{},token=TOKEN_A)[0],404)

    def test_real_worker_create_idempotency_and_restart(self):
        code,_,result=self.create(); self.assertEqual(code,201,result)
        self.assertEqual(self.create()[0],200)
        changed=self.request('POST','/api/cases',{'request_id':'create-request-0001','question':'Different question'})
        self.assertEqual(changed[0],409)
        rows=self.request('GET','/api/cases')[2]['cases']; self.assertEqual(len(rows),1)
        self.assertEqual(rows[0]['id'],result['case_id'])
        self.assertEqual(rows[0]['freshness']['new_fetches'],0)
        with WorkspaceStore.from_env().workspace('alice') as ws:
            self.assertEqual(cases.get(result['case_id'],db=ws.db)['version'],1)

    def test_tenant_cannot_read_other_case_or_history(self):
        result=self.create()[2]
        self.assertEqual(self.request('GET','/api/cases',token=TOKEN_B)[2]['cases'],[])
        self.assertEqual(self.request('GET','/api/cases/'+result['case_id'],token=TOKEN_B)[0],400)

    def test_browser_login_csrf_logout_and_no_store(self):
        from urllib.parse import urlencode
        code,headers,_=self.request('POST','/login',token=None,raw=urlencode({'token':TOKEN_A}),
                                    headers={'Content-Type':'application/x-www-form-urlencoded','Origin':ORIGIN})
        self.assertEqual(code,303); cookie=headers['Set-Cookie'].split(';')[0]
        session=cookie.split('=',1)[1]
        self.assertIn('HttpOnly',headers['Set-Cookie']); self.assertEqual(headers['Cache-Control'],'no-store')
        self.assertEqual(self.request('GET','/cases',token=None,headers={'Cookie':cookie})[0],200)
        data={'request_id':'browser-write-00001','question':'test','csrf':'wrong'}
        self.assertEqual(self.request('POST','/cases',data,token=None,headers={'Cookie':cookie,'Origin':ORIGIN})[0],403)
        data['csrf']=Auth(CONFIG).csrf(session)
        self.assertEqual(self.request('POST','/cases',data,token=None,headers={'Cookie':cookie,'Origin':'https://evil.example'})[0],403)
        self.assertEqual(self.request('POST','/cases',data,token=None,headers={'Cookie':cookie,'Origin':ORIGIN})[0],303)
        code,headers,_=self.request('POST','/logout',{'csrf':data['csrf']},token=None,headers={'Cookie':cookie,'Origin':ORIGIN})
        self.assertEqual(code,303);self.assertIn('Max-Age=0',headers['Set-Cookie'])

    def test_limits_reject_before_provider_and_do_not_reset(self):
        store=WorkspaceStore.from_env(); budget=Budget(store)
        budget.reserve('alice','first-request-0001','f',True)
        budget.reserve('alice','second-request-001','g',True)
        with patch('cloud.case_http.research') as run:
            code,_,_=self.request('POST','/api/cases',{'request_id':'third-request-0001','question':'A live question','live':True})
            self.assertEqual(code,429); run.assert_not_called()
        self.assertEqual(Budget(WorkspaceStore.from_env()).status('alice')['remaining'],0)
        with self.assertRaises(Rejected):budget.reserve('alice','first-request-0001','f',True)
        self.assertEqual(budget.status('alice')['used'],2)

    def test_stale_writer_does_not_overwrite_or_replay_research(self):
        def race(payload, db):
            pending=cases.create(payload['question'],db=db)
            with WorkspaceStore.from_env().workspace('alice') as other:
                winner=cases.create('Concurrent saved question',db=other.db)
                other.commit()
            return {'case_id':pending['id'],'version':1}
        with patch('cloud.case_http.research',side_effect=race) as run:
            code,_,_=self.create('race-request-00001')
            self.assertEqual(code,409)
            self.assertEqual(run.call_count,1)
        rows=self.request('GET','/api/cases')[2]['cases']
        self.assertEqual([r['question'] for r in rows],['Concurrent saved question'])
        with patch('cloud.case_http.research') as run:
            self.assertEqual(self.create('race-request-00001')[0],409)
            run.assert_not_called()

    def test_research_timeout_kills_process_and_does_not_save(self):
        import subprocess
        from cloud.case_http import research,HTTPError
        real_popen=subprocess.Popen
        children=[]
        def sleeper(*args,**kwargs):
            import sys
            child=real_popen([sys.executable,'-c','import time; time.sleep(30)'],**kwargs)
            children.append(child)
            return child
        with patch.dict(os.environ,{'AGENT_SCIENCE_RESEARCH_TIMEOUT':'1'}), patch('cloud.case_http.subprocess.Popen',side_effect=sleeper):
            with self.assertRaises(HTTPError) as caught:
                research({'action':'create'},Path(self.temp.name)/'job.sqlite')
        self.assertEqual(caught.exception.status,504)
        self.assertIsNotNone(children[0].poll())
        self.assertFalse((Path(self.temp.name)/'job.sqlite').exists())

    def test_duplicate_reservation_survives_utc_day_rollover(self):
        budget=Budget(WorkspaceStore.from_env())
        with patch.object(Budget,'key',return_value='usage-2026-09-04'):
            budget.reserve('alice','midnight-request-001','same-input',True)
        with patch.object(Budget,'key',return_value='usage-2026-09-05'):
            with self.assertRaises(Rejected) as caught:
                budget.reserve('alice','midnight-request-001','same-input',True)
            self.assertEqual(caught.exception.status,409)
            self.assertEqual(budget.status('alice')['used'],0)

    def test_bad_input_never_reaches_provider(self):
        for data in [[], {'request_id':'x','question':'Q'}, {'request_id':'long-request-0001','question':'x'*1501},
                     {'request_id':'long-request-0002','question':'Q','live':'false'},
                     {'request_id':'long-request-0003','question':'Q','root':'/app'},
                     {'request_id':'long-request-0004','question':'Q','sources':['file:///etc/passwd']}]:
            with patch('cloud.case_http.research') as run:
                self.assertEqual(self.request('POST','/api/cases',data)[0],400)
                run.assert_not_called()
        self.assertEqual(self.request('POST','/api/cases',raw='x'*32769)[0],400)

    def test_decision_source_history_and_stale_version(self):
        result=self.create()[2];cid=result['case_id']
        text='Typed tool inputs constrain the accepted argument shape.'
        with WorkspaceStore.from_env().workspace('alice') as ws:
            original=cases.get(cid,db=ws.db)
            entry={'id':'a'*16,'url':'https://example.com/paper','kind':'web_source','status':'QUOTE_VERIFIED',
                   'quote':text,'snapshot_text':text,'snapshot_hash':hashlib.sha256(text.encode()).hexdigest(),
                   'fetched_at':'2026-09-04T00:00:00+00:00','angle':'provided','relation':'not_assessed'}
            original.update(version=2,evidence=[entry]);cases._save(original,db=ws.db);ws.commit()
        payload={'request_id':'decision-write-001','version':2,'statement':'Test typed tools','rationale':'The documented constraint motivates an experiment, not a proven quality gain.','evidence_ids':['a'*16]}
        self.assertEqual(self.request('POST',f'/api/cases/{cid}/decisions',payload)[0],201)
        source=self.request('GET',f'/api/cases/{cid}/sources/'+('a'*16)+'?version=2')[2]
        self.assertEqual(source['text'],text)
        self.assertEqual(self.request('GET',f'/api/cases/{cid}?version=1')[2]['decisions'],[])
        with WorkspaceStore.from_env().workspace('alice') as ws:
            old=cases.get(cid,db=ws.db);old.update(version=3,evidence=[{**entry,'snapshot_hash':'changed','snapshot_text':'Changed source text'}]);cases._save(old,db=ws.db);ws.commit()
        self.assertEqual(self.request('GET',f'/api/cases/{cid}')[2]['decisions'][0]['review']['state'],'REVIEW_REQUIRED')
        payload['request_id']='decision-write-002'
        self.assertEqual(self.request('POST',f'/api/cases/{cid}/decisions',payload)[0],409)
        previous=self.request('GET',f'/api/cases/{cid}')[2]['decisions'][0]['id']
        payload.update(request_id='decision-write-003',version=3,supersedes=previous)
        self.assertEqual(self.request('POST',f'/api/cases/{cid}/decisions',payload)[0],201)
        latest=self.request('GET',f'/api/cases/{cid}')[2]
        self.assertEqual(latest['decisions'][0]['review']['state'],'SUPERSEDED')
        self.assertEqual(latest['decisions'][1]['supersedes'],previous)
        history=self.request('GET',f'/api/cases/{cid}?version=2')[2]
        self.assertEqual(len(history['decisions']),1)
        self.assertEqual(history['decisions'][0]['review']['state'],'UNCHANGED_IN_SNAPSHOT')


class AuthTests(unittest.TestCase):
    def test_expiry_tamper_and_rotation(self):
        clock=[1000];auth=Auth(CONFIG,clock=lambda:clock[0]);value=auth.session('alice')
        self.assertEqual(auth.session_user(value),'alice')
        self.assertIsNone(auth.session_user(value+'x'))
        clock[0]+=43201;self.assertIsNone(auth.session_user(value))
        rotated=Auth({**CONFIG,'users':{**CONFIG['users'],'alice':'c'*64}},clock=lambda:1000)
        self.assertIsNone(rotated.session_user(value))


if __name__=='__main__':unittest.main()
