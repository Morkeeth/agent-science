"""Read-only public case, isolated from all workspace state and provider calls."""
import json
from pathlib import Path
from cloud.case_pages import shell, esc, external


def render(source=''):
    case = json.loads(Path(__file__).with_name('public_demo.json').read_text())
    sources = {s['id']: s for s in case['sources']}
    selected = sources.get(source)
    if selected:
        content = f'''<section class="panel"><p class="eyebrow">Source snapshot · document occurrence</p><h2>{esc(selected['title'])}</h2><p class="quote">{esc(selected['quote'])}</p><p>{esc(selected['scope'])}</p>{external(selected['url'])}<p class="quiet wrap">Fetched {esc(selected['fetched_at'])}<br>Document SHA-256: {esc(selected['document_sha256'])}</p><p>No source was re-fetched by opening this page. Authorship and claim support are not established by the hash.</p></section><a class="button" href="/judge/demo">Compare the evidence</a>'''
    else:
        links = ''.join(f'<a class="case-row" href="/judge/demo?source={esc(s["id"])}"><h3>{esc(s["title"])}</h3><p>Inspect exact quote, scope and captured source identity →</p></a>' for s in case['sources'])
        content = f'''<div class="layout"><section class="panel"><h2>Two documents. Different scopes.</h2>{links}</section><aside><section class="panel stamp"><h2>What can we conclude?</h2><p>{esc(case['assessment'])}</p><p class="quiet">Authored interpretation of the displayed evidence, not an automated verdict.</p><p>{esc(case['unknown'])}</p></section><section class="panel"><h2>What would change this?</h2><p>A language specification imposing a universal maximum would challenge this reading. These style documents do not establish one.</p><a href="/judge/demo">Revisit this public case</a></section></aside></div>'''
    body = f'''<section class="hero"><p class="eyebrow">Public read-only research example · Claim under review</p><h1>{esc(case['claim'])}</h1><p class="lede">Follow the claim to its exact evidence, then inspect the limit of the conclusion.</p><p class="notice">{esc(case['kind'])}. No private workspace is read or changed.</p></section>{content}<p class="section"><a href="/judge">Back to the source method</a> · <a href="/login">Use a private research workspace</a></p>'''
    return shell('Agent Science · public evidence case', body, authenticated=False)
