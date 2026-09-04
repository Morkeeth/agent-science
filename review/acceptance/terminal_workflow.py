"""External acceptance: local CLI review + agent protocol, with no hosted account.

Run unchanged in the pinned checkout being measured. It exercises public process
interfaces, not implementation source. Temporary cases have no live providers.
"""
import json
from pathlib import Path
import subprocess
import sys
import tempfile


def cli(db,*args):
    p=subprocess.run([sys.executable,'-m','clearance','case',*args,'--db',str(db),'--json'],capture_output=True,text=True,timeout=15)
    assert p.returncode==0, p.stderr or p.stdout
    return json.loads(p.stdout)


with tempfile.TemporaryDirectory(prefix='terminal-acceptance-') as temporary:
    db=Path(temporary)/'cases.db'
    review=cli(db,'review','--root','.')
    assert review['cases']==[] and review['has_more'] is False
    created=cli(db,'create','Terminal workflow acceptance','--root','.')
    found=cli(db,'list','--query','workflow acceptance','--page-info','--limit','1')
    assert len(found['cases'])==1 and found['cases'][0]['id']==created['id']
    assert Path(created['repo']['root'])==Path.cwd().resolve()
    messages=[
        {'jsonrpc':'2.0','id':1,'method':'initialize','params':{}},
        {'jsonrpc':'2.0','id':2,'method':'tools/list'},
        {'jsonrpc':'2.0','id':3,'method':'tools/call','params':{'name':'science_case','arguments':{'action':'decide','case_id':created['id'],'db':str(db)}}},
        {'jsonrpc':'2.0','id':4,'method':'tools/call','params':{'name':'science_case','arguments':{'action':'review','db':str(db)}}},
    ]
    p=subprocess.run([sys.executable,'-m','clearance.mcp_server'],input=''.join(json.dumps(m)+'\n' for m in messages),capture_output=True,text=True,timeout=15)
    assert p.returncode==0,p.stderr
    out=[json.loads(line) for line in p.stdout.splitlines()]
    schema=next(t for t in out[1]['result']['tools'] if t['name']=='science_case')['inputSchema']
    assert 'review' in schema['properties']['action']['enum']
    assert {'supersedes','experiment_ids'}<=schema['properties'].keys()
    assert out[2]['result']['isError'] is True
    assert out[3]['result']['isError'] is False
print('Terminal acceptance passed: local review, retrieval, repo context, agent errors and continuation.')
