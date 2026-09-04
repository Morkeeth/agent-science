"""Drive real CLI processes over saved source effects; no provider or dashboard."""
import json
from pathlib import Path
import subprocess
import sys
from unittest.mock import patch

from clearance import cases, instruments, case_review
from clearance.mcp_server import handle_tool


URL='https://example.org/terminal-contract'
TEXT='Typed tool inputs constrain the accepted argument shape in the contract.'


def cli(db, cache, *args):
    code="from pathlib import Path; import sys,runpy; from clearance import instruments; instruments.DOCS=Path(sys.argv[1]); sys.argv=['clearance']+sys.argv[2:]; runpy.run_module('clearance',run_name='__main__')"
    result=subprocess.run([sys.executable,'-c',code,str(cache),'case',*args,'--db',str(db),'--json'],capture_output=True,text=True,timeout=20)
    return result.returncode,json.loads(result.stdout)


def test_cli_research_inspect_review_supersede_and_historical_sources(tmp_path):
    db=tmp_path/'private cases.db';cache=tmp_path/'documents.json'
    cache.write_text(json.dumps({URL:{'text':TEXT,'fetched_at':'2026-09-04T00:00:00Z'}}))
    code,case=cli(db,cache,'create','Do typed tool inputs constrain accepted argument shape?','--source',URL)
    assert code==0;cid=case['id'];eid=case['evidence'][0]['id']
    code,source=cli(db,cache,'source',cid,'--evidence',eid,'--version','1')
    assert code==0 and source['text']==TEXT
    code,decided=cli(db,cache,'decide',cid,'--version','1','--statement','Test typed tools','--reason','Fixture motivates a local trial','--evidence',eid)
    assert code==0;did=decided['decisions'][0]['id']
    new_text='Typed tool inputs constrain shape but do not establish task success.'
    cache.write_text(json.dumps({URL:{'text':new_text,'fetched_at':'2026-09-04T01:00:00Z'}}))
    code,refreshed=cli(db,cache,'refresh',cid)
    assert code==0 and refreshed['version']==2
    code,review=cli(db,cache,'review','--query','TYPED TOOL')
    assert code==0 and review['cases'][0]['decisions'][0]['id']==did
    assert review['cases'][0]['review_required']==1
    code,stale=cli(db,cache,'decide',cid,'--version','1','--statement','Stale choice','--reason','Stale reason','--evidence',eid)
    assert code==2 and 'version changed' in stale['error']
    code,revised=cli(db,cache,'decide',cid,'--version','2','--supersedes',did,'--statement','Test quality separately','--reason','The new fixture states a limitation','--evidence',eid)
    assert code==0 and revised['decisions'][0]['review']['state']=='SUPERSEDED'
    assert cli(db,cache,'review')[1]['cases']==[]
    history=cli(db,cache,'show',cid,'--version','1')[1]
    assert len(history['decisions'])==1 and history['decisions'][0]['statement']=='Test typed tools'
    assert cli(db,cache,'source',cid,'--version','1','--evidence',eid)[1]['text']==TEXT
    assert isinstance(cli(db,cache,'list')[1],list) # preserve existing JSON array contract


def test_review_finds_old_unresolved_case_past_recent_page_and_filters_repo(tmp_path):
    db=tmp_path/'cases.db';repo=tmp_path/'repo';repo.mkdir()
    snapshot={'text':TEXT,'sha256':'fixture-snapshot','fetched_at':'2026-09-04T00:00:00Z','cache_hit':True}
    with patch.object(instruments,'document_snapshot',return_value=snapshot):
        old=cases.create('Typed tool inputs',root=repo,sources=[URL],db=db)
    cases.decide(old['id'],'Original decision','A fixture',[old['evidence'][0]['id']],expected_version=1,db=db)
    with patch.object(instruments,'document_snapshot',return_value=None):cases.refresh(old['id'],db=db)
    for n in range(23):cases.create('New uneventful case '+str(n),root=repo,db=db)
    with patch.object(instruments,'document_snapshot',side_effect=AssertionError('review must not fetch')):
        result=case_review.index(db=db,root=repo,review_only=True,limit=1)
    assert [r['id'] for r in result['cases']]==[old['id']]
    assert case_review.index(db=db,root=tmp_path/'other',review_only=True)['cases']==[]
    first=case_review.index(db=db,limit=20);second=case_review.index(db=db,offset=first['next_offset'])
    assert first['has_more'] and len(second['cases'])==4
    assert '--db ' in case_review.render(result,db=db)


def test_atomic_decision_rejects_refresh_between_read_and_insert(tmp_path):
    db=tmp_path/'cases.db'
    snapshot={'text':TEXT,'sha256':'fixture-snapshot','fetched_at':None,'cache_hit':True}
    with patch.object(instruments,'document_snapshot',return_value=snapshot):case=cases.create('Typed tool inputs',sources=[URL],db=db)
    original_get=cases.get
    raced=False
    def racing_get(*args,**kwargs):
        nonlocal raced
        data=original_get(*args,**kwargs)
        if not raced:
            raced=True
            with patch.object(instruments,'document_snapshot',return_value=snapshot):cases.refresh(case['id'],db=db)
        return data
    with patch.object(cases,'get',side_effect=racing_get):
        try:cases.decide(case['id'],'Old read','Must fail',[case['evidence'][0]['id']],expected_version=1,db=db)
        except ValueError as exc:assert 'changed while deciding' in str(exc)
        else:raise AssertionError('stale decision committed')
    assert original_get(case['id'],db=db)['decisions']==[]


def test_mcp_rejects_missing_version_and_exposes_review(tmp_path):
    db=str(tmp_path/'cases.db')
    created=json.loads(handle_tool('science_case',{'action':'create','question':'Offline MCP case','db':db}))
    missing=json.loads(handle_tool('science_case',{'action':'decide','case_id':created['id'],'db':db}))
    assert 'requires the evidence version' in missing['error']
    report=json.loads(handle_tool('science_case',{'action':'review','db':db,'page_size':1}))
    assert report['cases']==[] and 'does not check the web' in report['basis']
    assert isinstance(json.loads(handle_tool('science_case',{'action':'list','db':db,'page_size':1})),list)


def test_real_stdio_errors_are_marked_and_server_continues(tmp_path):
    messages=[
        {'jsonrpc':'2.0','id':1,'method':'tools/call','params':{'name':'science_case','arguments':{'action':'decide','db':str(tmp_path/'cases.db')}}},
        {'jsonrpc':'2.0','id':2,'method':'tools/call','params':{'name':'science_case','arguments':[]}},
        {'jsonrpc':'2.0','id':3,'method':'tools/call','params':{'name':'science_case','arguments':{'action':'list','page_info':True,'db':str(tmp_path/'cases.db')}}},
    ]
    response=subprocess.run([sys.executable,'-m','clearance.mcp_server'],input=''.join(json.dumps(m)+'\n' for m in messages),capture_output=True,text=True,timeout=10)
    assert response.returncode==0,response.stderr
    rows=[json.loads(line)['result'] for line in response.stdout.splitlines()]
    assert rows[0]['isError'] and rows[1]['isError'] and not rows[2]['isError']
    assert json.loads(rows[2]['content'][0]['text'])['has_more'] is False


def test_installed_command_preserves_caller_repo_and_refuses_to_replace_files(tmp_path):
    project=Path(__file__).resolve().parents[1]
    bindir=tmp_path/'bin';repo=tmp_path/'user-repo';repo.mkdir()
    installer=project/'scripts/install-cli.py'
    subprocess.run([sys.executable,str(installer),'--bin-dir',str(bindir)],check=True,capture_output=True)
    result=subprocess.run([str(bindir/'agent-science'),'case','create','Local working-directory check','--root','.','--db',str(tmp_path/'cases.db'),'--json'],cwd=repo,capture_output=True,text=True)
    assert result.returncode==0,result.stderr
    assert json.loads(result.stdout)['repo']['root']==str(repo.resolve())
    (bindir/'agent-science').unlink()
    (bindir/'agent-science').write_text('Existing unrelated command')
    refused=subprocess.run([sys.executable,str(installer),'--bin-dir',str(bindir)],capture_output=True,text=True)
    assert refused.returncode!=0
    assert (bindir/'agent-science').read_text()=='Existing unrelated command'


def test_mcp_string_false_cannot_start_paid_research(tmp_path):
    with patch.object(cases,'create') as create:
        result=json.loads(handle_tool('science_case',{'action':'create','question':'A question','live':'false','db':str(tmp_path/'cases.db')}))
    assert result['error']=='live must be a boolean'
    create.assert_not_called()


def test_stdio_preserves_existing_markdown_visibility_tool(tmp_path):
    import os
    message={'jsonrpc':'2.0','id':1,'method':'tools/call','params':{'name':'science_visibility','arguments':{'query':'Unmatched protocol visibility check','live':False,'full':False,'no_personal':True}}}
    env={**os.environ,'REFUSAL_LOG_DB':str(tmp_path/'refusal.db'),'CORPUS_DB':str(tmp_path/'corpus.db'),'AGENT_SCIENCE_TRUTH_DB':str(tmp_path/'truth.db')}
    response=subprocess.run([sys.executable,'-m','clearance.mcp_server'],input=json.dumps(message)+'\n',capture_output=True,text=True,timeout=20,env=env)
    assert response.returncode==0,response.stderr
    result=json.loads(response.stdout)['result']
    assert result['isError'] is False
    assert result['content'][0]['text'].startswith('# Agent Science')


def test_simultaneous_legacy_database_migration(tmp_path):
    import sqlite3
    import threading
    from concurrent.futures import ThreadPoolExecutor
    db=tmp_path/'legacy.db'
    with sqlite3.connect(db) as con:
        con.execute('CREATE TABLE decisions(id TEXT PRIMARY KEY,case_id TEXT,version INTEGER,statement TEXT,rationale TEXT,evidence_ids TEXT,created_at TEXT)')
    barrier=threading.Barrier(2)
    class ConcurrentConnection(sqlite3.Connection):
        first_columns=True
        def execute(self, sql, *args, **kwargs):
            cursor=super().execute(sql,*args,**kwargs)
            if sql=='PRAGMA table_info(decisions)' and self.first_columns:
                self.first_columns=False
                rows=list(cursor)
                barrier.wait(timeout=5)
                return iter(rows)
            return cursor
    real_connect=sqlite3.connect
    def connect(*args,**kwargs):
        return real_connect(*args,**kwargs,factory=ConcurrentConnection)
    def upgrade(_):
        con=cases.connect(db)
        try:return {r[1] for r in con.execute('PRAGMA table_info(decisions)')}
        finally:con.close()
    with patch.object(cases.sqlite3,'connect',side_effect=connect), ThreadPoolExecutor(2) as pool:
        results=list(pool.map(upgrade,range(2)))
    assert all({'supersedes','experiment_ids'} <= columns for columns in results)


def test_database_failure_is_structured_and_mcp_continues(tmp_path):
    db=tmp_path/'corrupt.db';db.write_bytes(b'not a sqlite database')
    code,result=cli(db,tmp_path/'cache.json','review')
    assert code==2 and 'error' in result
    messages=[{'jsonrpc':'2.0','id':1,'method':'tools/call','params':{'name':'science_case','arguments':{'action':'review','db':str(db)}}},
              {'jsonrpc':'2.0','id':2,'method':'tools/list'}]
    proc=subprocess.run([sys.executable,'-m','clearance.mcp_server'],input=''.join(json.dumps(m)+'\n' for m in messages),text=True,capture_output=True,timeout=20)
    out=[json.loads(line) for line in proc.stdout.splitlines()]
    assert proc.returncode==0 and out[0]['result']['isError'] is True
    assert out[1]['result']['tools']
