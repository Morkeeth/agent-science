"""Native form navigation in an isolated headless browser, with local test data.

Run explicitly: python3 -m pytest -q tests/test_hosted_browser.py
Requires the optional Playwright test package and its Chromium browser.
"""
import hashlib
from contextlib import ExitStack
import json
import os
import threading
from http.server import HTTPServer
from unittest.mock import patch

import pytest
playwright = pytest.importorskip('playwright.sync_api')
from cloud.service import Handler
from cloud.case_storage import WorkspaceStore
from cloud import case_pages
from clearance import cases, instruments


@pytest.mark.parametrize("referrer_control", [False, True])
def test_native_forms_origin_decision_review_and_mobile(tmp_path, referrer_control):
    token='isolated-browser-test-token-'+'a'*32
    config={'session_key':'test-session-key-'+'b'*48,'users':{'browser-test':hashlib.sha256(token.encode()).hexdigest()}}
    server=HTTPServer(('127.0.0.1',0),Handler)
    origin='http://127.0.0.1:'+str(server.server_port)
    env={'AGENT_SCIENCE_HOSTED':'1','AGENT_SCIENCE_ALLOW_HTTP':'1','AGENT_SCIENCE_PUBLIC_ORIGIN':origin,
         'AGENT_SCIENCE_ACCESS_CONFIG':json.dumps(config),'AGENT_SCIENCE_WORKSPACE_DIR':str(tmp_path/'store')}
    with patch.dict(os.environ,env), ExitStack() as controls:
        if referrer_control:
            original_header=Handler.send_header
            original_shell=case_pages.shell
            def header(handler,key,value):
                return original_header(handler,key,'no-referrer' if key=='Referrer-Policy' else value)
            def shell(*args,**kwargs):
                return original_shell(*args,**kwargs).replace('name="referrer" content="same-origin"','name="referrer" content="no-referrer"')
            controls.enter_context(patch.object(Handler,'send_header',header))
            controls.enter_context(patch.object(case_pages,'shell',shell))
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        try:
            with playwright.sync_playwright() as p:
                browser=p.chromium.launch(headless=True)
                page=browser.new_page(viewport={'width':390,'height':844})
                submitted=[]
                page.on('request',lambda r:submitted.append(r) if r.method=='POST' else None)
                page.goto(origin+'/login')
                page.get_by_label('Access token',exact=True).fill(token)
                with page.expect_navigation(wait_until='domcontentloaded') as login_response:
                    page.get_by_role('button',name='Sign in',exact=True).click()
                if referrer_control:
                    assert submitted[0].headers.get('origin')=='null'
                    assert login_response.value.status==403
                    browser.close()
                    return
                page.wait_for_url(origin+'/cases')
                assert submitted[0].headers.get('origin')==origin
                assert submitted[0].headers.get('origin')!='null'
                page.get_by_label('Research question',exact=True).fill('Browser contract: do typed inputs constrain accepted argument shape?')
                page.locator('summary').filter(has_text='Start with sources or official domains').click()
                page.locator('textarea[name=sources]').fill('https://example.com/spec')
                page.locator('input[name=live]').uncheck()
                with page.expect_navigation(wait_until='domcontentloaded'):
                    page.get_by_role('button',name='Create research case →').click()
                page.wait_for_url('**/cases/*')
                cid=page.url.rsplit('/',1)[1]
                # Substitute the document-fetch effect; real quote selection and
                # revision rules remain in the code under test.
                text='Typed inputs constrain the accepted argument shape in this browser contract.'
                def snapshot(*args,**kwargs):
                    return {'text':text,'sha256':hashlib.sha256(text.encode()).hexdigest(),
                            'fetched_at':'2026-09-04T00:00:00+00:00','final_url':'https://example.com/spec','cache_hit':False}
                with WorkspaceStore.from_env().workspace('browser-test') as ws:
                    with patch.object(instruments,'document_snapshot',side_effect=snapshot):cases.refresh(cid,live=True,db=ws.db)
                    ws.commit()
                page.reload()
                page.get_by_role('link',name='Read full saved source →').click()
                assert text in page.locator('main').inner_text()
                page.go_back()
                page.get_by_label('What will you do?',exact=True).fill('Test typed tool inputs.')
                page.get_by_label('Why this choice? What remains uncertain?',exact=True).fill('This fixture checks the browser flow; it makes no real research claim.')
                page.locator('input[name=evidence_ids]').first.check()
                with page.expect_navigation(wait_until='domcontentloaded'):
                    page.get_by_role('button',name='Save decision and its reasons →').click()
                assert page.get_by_role('heading',name='Test typed tool inputs.',exact=True).is_visible()
                text='Typed inputs constrain accepted argument shape, but do not establish task success.'
                with WorkspaceStore.from_env().workspace('browser-test') as ws:
                    with patch.object(instruments,'document_snapshot',side_effect=snapshot):cases.refresh(cid,live=True,db=ws.db)
                    ws.commit()
                page.reload()
                assert 'REVIEW REQUIRED' in page.locator('main').inner_text()
                page.get_by_label('What will you do?',exact=True).fill('Keep the experiment and assess task success separately.')
                page.get_by_label('Why this choice? What remains uncertain?',exact=True).fill('The changed fixture adds a limit. This decision supersedes the earlier fixture decision.')
                prior=page.locator('select[name=supersedes] option').nth(1).get_attribute('value')
                page.locator('select[name=supersedes]').select_option(prior)
                page.locator('input[name=evidence_ids]').first.check()
                with page.expect_navigation(wait_until='domcontentloaded'):
                    page.get_by_role('button',name='Save decision and its reasons →').click()
                assert 'SUPERSEDED' in page.locator('main').inner_text()
                assert page.locator('.notice strong').filter(has_text='REVIEW REQUIRED').count()==0
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
                page.screenshot(path='/tmp/as-hosted-native-mobile.png',full_page=True)
                with page.expect_navigation(wait_until='domcontentloaded'):
                    page.get_by_role('button',name='Sign out',exact=True).click()
                page.wait_for_url(origin+'/login')
                browser.close()
        finally:
            server.shutdown();server.server_close();thread.join()
