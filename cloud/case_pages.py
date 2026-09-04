"""Hosted research cases: native forms, escaped text, version-bound source reading."""
from __future__ import annotations

import html
import uuid
from urllib.parse import quote, urlsplit


CSS = """
:root{--paper:#e9ecef;--card:#f7f8fa;--ink:#14161c;--muted:#61656e;--rule:#c5cad3;--stamp:#b42318;--wash:#f1e5e5}
*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:17px/1.6 Georgia,'Times New Roman',serif}
a{color:inherit;text-underline-offset:4px}a:hover{color:var(--stamp)}button,input,textarea,select{font:inherit}button,a.button{min-height:46px;padding:10px 19px;border:1px solid var(--ink);background:var(--ink);color:var(--card);cursor:pointer;text-decoration:none;display:inline-flex;align-items:center;justify-content:center;gap:8px}button:hover,a.button:hover{background:var(--stamp);border-color:var(--stamp)}button.secondary,a.secondary{background:transparent;color:var(--ink)}button:disabled{opacity:.45;cursor:not-allowed}input:not([type=checkbox]),textarea,select{display:block;width:100%;border:1px solid var(--rule);border-radius:0;background:var(--card);padding:12px;color:var(--ink)}select{max-width:100%;min-height:46px}textarea{resize:vertical;min-height:100px}input[type=checkbox]{width:20px;height:20px;accent-color:var(--stamp);flex-shrink:0}label{display:block;font-weight:bold;margin-top:18px}label.check{display:flex;align-items:flex-start;gap:12px;font-weight:normal;margin:16px 0}.check input{margin-top:5px}small,.small{font-size:.87rem}.meta,.eyebrow,.badge,.step{font:12px/1.6 ui-monospace,SFMono-Regular,Consolas,monospace;letter-spacing:.035em}.muted,.meta{color:var(--muted)}.eyebrow{text-transform:uppercase;letter-spacing:.13em;color:var(--stamp);margin:0 0 12px}.badge{display:inline-block;border:1px solid var(--rule);padding:3px 8px;color:var(--ink)}.badge.alert{border-color:var(--stamp);color:var(--stamp)}header{border-bottom:1px solid var(--rule)}.top{max-width:1160px;margin:auto;padding:20px 28px;display:flex;align-items:center;justify-content:space-between;gap:20px}.brand{font-size:21px;text-decoration:none;font-weight:bold;letter-spacing:-.04em}.brand span{font-style:italic;font-weight:normal}nav,.actions{display:flex;align-items:center;flex-wrap:wrap;gap:12px}nav a{font-size:.85rem}nav form{margin:0}nav button{min-height:42px;padding:6px 12px;font-size:.85rem;background:transparent;color:var(--ink);border-color:var(--rule)}main{max-width:1160px;padding:48px 28px 80px;margin:auto}.hero{max-width:800px;margin-bottom:35px}h1{font-size:clamp(34px,5vw,58px);line-height:1.08;letter-spacing:-.045em;font-weight:normal;margin:0 0 18px;overflow-wrap:anywhere}h2{font-size:27px;line-height:1.2;font-weight:normal;margin:0 0 16px;letter-spacing:-.025em}h3{font-size:21px;line-height:1.3;font-weight:normal;margin:0 0 12px}p{margin:0 0 14px}.lede{font-size:20px;line-height:1.5;max-width:720px}.layout{display:grid;grid-template-columns:minmax(0,1.35fr) minmax(280px,.85fr);gap:28px;align-items:start}.panel{border:1px solid var(--rule);background:var(--card);padding:26px;margin:0 0 24px}.panel.stamp{border-top:3px solid var(--stamp)}.panel.dark{background:var(--ink);color:var(--card)}.panel.dark .meta{color:#c5cad3}.panel.dark a{color:inherit}.section{margin-top:42px}.section-head{display:flex;justify-content:space-between;align-items:baseline;gap:18px;border-bottom:1px solid var(--rule);padding-bottom:12px;margin-bottom:22px}.section-head h2{margin:0}.step{color:var(--stamp);margin-right:10px}.notice{padding:16px 20px;border-left:3px solid var(--stamp);background:var(--wash);margin:20px 0}.notice p:last-child{margin:0}.error{border:1px solid var(--stamp);color:var(--stamp);padding:16px;margin:0 0 24px}.tiles{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:1px;background:var(--rule);border:1px solid var(--rule);margin-bottom:24px}.tile{background:var(--card);padding:16px}.tile strong{display:block;font-size:25px;font-weight:normal;line-height:1.2}.tile .meta{font-size:11px}.case-row{display:block;text-decoration:none;padding:21px 0;border-bottom:1px solid var(--rule)}.case-row h3{margin:8px 0}.case-row .badge{margin:0 0 3px}.empty{border:1px dashed var(--rule);padding:24px}.source-title{overflow-wrap:anywhere}.quote{border-left:2px solid var(--ink);padding:0 0 0 17px;margin:20px 0;font-size:20px;white-space:pre-wrap;overflow-wrap:anywhere}.details-grid{display:grid;grid-template-columns:1fr 1fr;gap:20px}.change{padding:18px 0;border-bottom:1px solid var(--rule)}.change:last-child{border:0}.change .quote{font-size:16px;margin:8px 0}.source-text{font:15px/1.8 ui-monospace,SFMono-Regular,Consolas,monospace;white-space:pre-wrap;overflow-wrap:anywhere;margin:24px 0;padding:26px;border:1px solid var(--rule);background:var(--card)}.trace{list-style:none;padding:0;margin:0}.trace li{padding:15px 0;border-bottom:1px solid var(--rule);overflow-wrap:anywhere}.trace li:last-child{border:0}.trace .meta{display:block;margin-top:5px}details{margin:18px 0}summary{cursor:pointer;min-height:44px;padding:8px 0}fieldset{padding:0;border:0;margin:20px 0}legend{font-weight:bold}.evidence-choice{border-top:1px solid var(--rule);padding-top:12px}footer{border-top:1px solid var(--rule);max-width:1104px;margin:0 auto;padding:20px 0 35px;color:var(--muted);font-size:13px}.login{max-width:640px;margin:25px auto}.login h1{font-size:52px}.anchor-nav{margin:22px 0;gap:20px}.anchor-nav a{font:12px ui-monospace,monospace}.wrap{overflow-wrap:anywhere}.quiet{margin-top:12px;color:var(--muted);font-size:14px}:focus-visible{outline:3px solid var(--stamp);outline-offset:4px}.skip{position:absolute;left:-9999px}.skip:focus{left:20px;top:8px;background:var(--card);padding:10px;z-index:2}
@media(max-width:760px){.top{padding:16px 18px}.top nav{gap:8px}.brand{font-size:19px}main{padding:30px 18px 50px}.layout,.details-grid{grid-template-columns:1fr;gap:0}.panel{padding:21px}.hero{margin-bottom:24px}.lede{font-size:18px}.section{margin-top:30px}.section-head{align-items:flex-start;flex-direction:column;gap:8px}.tiles{grid-template-columns:repeat(3,minmax(0,1fr))}.tile{padding:12px 9px}.tile strong{font-size:22px}.tile .meta{font-size:10px}.source-text{padding:17px;font-size:13px}.login{margin:10px auto}.login h1{font-size:40px}footer{margin:0 18px}.actions>*{flex:1 1 auto}.quote{font-size:18px}h1{font-size:36px}.anchor-nav{gap:15px}}
@media(prefers-reduced-motion:reduce){*{scroll-behavior:auto}}@media print{nav,form,.anchor-nav{display:none}body{background:white}main{padding:0}.panel{break-inside:avoid}a{color:black}}
"""


def esc(value):
    return html.escape(str(value if value is not None else ''), quote=True)


def segment(value):
    return quote(str(value), safe='')


def safe_url(value):
    value = str(value or '')
    if any(ord(c) < 33 or c == '\\' for c in value):
        return None
    try:
        u = urlsplit(value)
        if u.scheme.lower() not in ('http', 'https') or not u.hostname or u.username is not None or u.password is not None:
            return None
        _ = u.port
    except ValueError:
        return None
    return value


def external(url, label='Open original source'):
    good = safe_url(url)
    return (f'<a href="{esc(good)}" target="_blank" rel="noreferrer noopener">{esc(label)} ↗</a>'
            if good else '<span class="muted">Source link unavailable</span>')


def hidden(name, value):
    return f'<input type="hidden" name="{esc(name)}" value="{esc(value)}">'


def mutation(csrf):
    return hidden('csrf', csrf) + hidden('request_id', str(uuid.uuid4()))


def _error(message):
    return f'<div class="error" role="alert">{esc(message)}</div>' if message else ''


def shell(title, body, csrf='', authenticated=True):
    nav = ('<nav aria-label="Account"><a href="/cases">Cases</a>'
           f'<form method="post" action="/logout">{hidden("csrf", csrf)}<button>Sign out</button></form></nav>') if authenticated else ''
    return ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            '<meta name="referrer" content="same-origin">'
            f'<title>{esc(title)} · Agent Science</title><style>{CSS}</style></head><body>'
            '<a class="skip" href="#main">Skip to content</a><header><div class="top">'
            '<a class="brand" href="/cases">Agent <span>Science</span></a>' + nav + '</div></header>'
            f'<main id="main">{body}</main><footer>Agent Science · Sources, decisions, and what changed between them.</footer></body></html>')


def login(error='', secure=True):
    transport = ('<p class="quiet">Your access token is exchanged for a session. Keep the token private.</p>' if secure else
                 '<div class="notice"><strong>Local connection</strong><p>This connection is not encrypted. Use a local development token only.</p></div>')
    body = ('<div class="login"><p class="eyebrow">A decision should have a reason</p>'
            '<h1>Keep the evidence.<br>See what changes.</h1>'
            '<p class="lede">Build a research case, record your decision, and review it when its sources change.</p>'
            '<section class="panel stamp"><h2>Open your workspace</h2>' + _error(error) +
            '<form method="post" action="/login"><label for="token">Access token</label>'
            '<input id="token" name="token" type="password" required autocomplete="current-password" spellcheck="false">'
            '<div class="actions" style="margin-top:20px"><button>Sign in</button></div></form>' + transport + '</section>'
            '<p class="small muted">Hosted research supports public sources and saved decisions. Repository uploads and experiment execution are not available here.</p></div>')
    return shell('Sign in', body, authenticated=False)


def review_count(case):
    return sum(d.get('review', {}).get('state') == 'REVIEW_REQUIRED' for d in case.get('decisions', []))


def live_choice():
    return ('<label class="check"><input type="checkbox" name="live" value="1" checked>'
            '<span><strong>Run live research</strong><br><span class="small muted">Live research sends your question to the search provider and fetches public sources. Uses one research run. Without live research, a new case stays empty; refresh can reread its saved sources.</span></span></label>')


def dashboard(case_list, csrf, budget, error='', page=1, has_more=False):
    budget = budget or {}
    attention = sum(review_count(c) for c in case_list)
    body = ('<div class="hero"><p class="eyebrow">Your research desk</p><h1>What would change<br>your decision?</h1>'
            '<p class="lede">Ask a question that matters to your work. Keep the sources, make your reasoning explicit, and return when the evidence changes.</p></div>' + _error(error))
    if attention:
        body += f'<div class="notice"><strong>{attention} saved decision{"s" if attention != 1 else ""} {"need" if attention != 1 else "needs"} review.</strong><p>Source snapshots changed. Review the difference before changing your decision.</p><a href="#recent">Open cases needing attention ↓</a></div>'
    body += ('<div class="layout"><section class="panel stamp"><p class="eyebrow">01 / Start a case</p><h2>Give the question a place to live.</h2>'
             f'<form method="post" action="/cases">{mutation(csrf)}<label for="question">Research question</label>'
             '<textarea id="question" name="question" rows="3" maxlength="1500" required placeholder="Should our agents start a fresh session for each task?"></textarea>'
             '<p class="quiet">Name the practice, outcome, or tradeoff you want to understand. Do not include secrets or private repository content.</p>'
             '<details><summary>Start with sources or official domains</summary>'
             '<label for="sources">Public source URLs <span class="muted">· optional</span></label>'
             '<textarea id="sources" name="sources" rows="3" placeholder="https://example.org/research"></textarea>'
             '<p class="quiet">One URL per line, up to 12. Supplied URLs focus the case on those sources.</p>'
             '<label for="official_domains">Domains you identify as official <span class="muted">· optional</span></label>'
             '<textarea id="official_domains" name="official_domains" rows="2" placeholder="docs.example.org"></textarea>'
             '<p class="quiet">One hostname per line. This is your declared source category, not a verification of authority.</p></details>'
             + live_choice() + '<button>Create research case →</button></form></section>'
             '<aside><section class="panel dark"><p class="eyebrow" style="color:#d3a5a5">A useful return visit</p><h2>The decision stays yours.</h2>'
             '<p>Agent Science preserves what a source said. You decide what that evidence means for your work.</p>'
             '<p class="small">On your next visit, refresh a case. A source change marks dependent decisions for review and shows the old and new quotes.</p></section>'
             '<section class="panel"><h3>Research allowance</h3><div class="tiles">')
    for key, label in (('used','Used'), ('limit','Configured limit'), ('remaining','Remaining')):
        body += f'<div class="tile"><strong>{esc(budget.get(key, "—"))}</strong><span class="meta">{label}</span></div>'
    body += ('</div><p class="quiet">Units are research runs under this workspace’s configured limit. They are not dollar costs. Failed attempts count. The allowance resets at 00:00 UTC.</p></section></aside></div>'
             '<section id="recent" class="section"><div class="section-head"><h2>Cases to return to</h2><span class="meta">Review required first on this page</span></div>')
    if not case_list:
        body += '<div class="empty"><h3>Your first case starts with one question.</h3><p>No saved cases yet. Create a case above to collect evidence and record a decision.</p></div>'
    for case in sorted(case_list, key=lambda c: bool(review_count(c)), reverse=True):
        n = review_count(case)
        badge = f'<span class="badge alert">REVIEW REQUIRED · {n}</span>' if n else '<span class="badge">Saved research case</span>'
        body += (f'<a class="case-row" href="/cases/{segment(case["id"])}">{badge}<h3>{esc(case.get("question"))} →</h3>'
                 f'<p class="meta">Version {esc(case.get("version"))} · {len(case.get("evidence", []))} sources · {len(case.get("decisions", []))} decisions<br>Last case revision {esc(case.get("checked_at"))}</p></a>')
    body += '<nav aria-label="Case pages" class="actions">'
    if page > 1:
        body += f'<a href="/cases?page={page-1}">← Newer cases</a>'
    body += f'<span class="meta">Page {page}</span>'
    if has_more:
        body += f'<a href="/cases?page={page+1}">Older cases →</a>'
    return shell('Research cases', body + '</nav></section>', csrf)


KINDS = {'research_repository':'Research repository', 'declared_official':'Declared official source', 'web_source':'Other web source'}


def detail(case, csrf, error=''):
    cid = segment(case['id'])
    version = int(case.get('version', 1))
    latest = int(case.get('latest_version', version))
    evidence = case.get('evidence', [])
    decisions = case.get('decisions', [])
    coverage = case.get('coverage', {})
    freshness = case.get('freshness', {})
    body = (f'<div class="hero"><p class="eyebrow">Research case / {esc(case["id"])} / version {version}</p><h1>{esc(case.get("question"))}</h1>'
            '<p class="lede">Read the evidence. Record your reasoning. Review the decision when its sources change.</p>'
            f'<p class="meta">Case revision {esc(case.get("checked_at"))}</p></div>' + _error(error))
    if version < latest:
        body += f'<div class="notice"><strong>You are reading saved version {version}.</strong><p>This snapshot is preserved. <a href="/cases/{cid}">Open latest version {latest} to record a decision.</a></p></div>'
    if review_count(case):
        body += f'<div class="notice"><strong>REVIEW REQUIRED · {review_count(case)} decision(s)</strong><p>The cited evidence changed. <a href="#decisions">Read the affected decisions and differences ↓</a> Changes require review, not automatic reversal.</p></div>'
    body += '<nav class="anchor-nav" aria-label="Case sections"><a href="#evidence">01 Evidence</a><a href="#changes">02 Changes</a><a href="#decisions">03 Decisions</a><a href="#trace">04 Search trace</a></nav>'
    body += '<div class="tiles">'
    for val, label in ((coverage.get('verified_quotes',sum(e.get('status')=='QUOTE_VERIFIED' for e in evidence)), 'Quotes located'), (freshness.get('new_fetches',0),'Fresh web fetches'), (freshness.get('cached_reads',0),'Cached reads')):
        body += f'<div class="tile"><strong>{esc(val)}</strong><span class="meta">{label}</span></div>'
    body += ('</div><p class="quiet">A located quote proves its occurrence in a saved source. It does not prove the source supports the question. Cached reads cannot rule out changes on the web.</p>'
             '<div class="layout"><div><section id="evidence" class="section"><div class="section-head"><h2><span class="step">01</span>Evidence to assess</h2></div>')
    missing = coverage.get('missing_kinds', [])
    if missing:
        body += '<div class="notice"><strong>Coverage remains incomplete</strong><p>No located quote in: ' + esc(', '.join(KINDS.get(k,k) for k in missing)) + '.</p><p class="small">Source categories do not establish independence, quality, or support.</p></div>'
    if not evidence:
        body += '<div class="empty"><h3>No sources available in this case.</h3><p>Enable live research or start a case with public source URLs. No answer is established by an empty search.</p></div>'
    for idx, e in enumerate(evidence, 1):
        eid = segment(e['id'])
        status = e.get('status')
        verified = status == 'QUOTE_VERIFIED'
        label = 'Quote located · relationship not assessed' if verified else 'No matching quote' if status == 'NO_MATCHED_QUOTE' else 'Source unavailable'
        body += (f'<article class="panel" id="evidence-{eid}"><p class="eyebrow">Source {idx:02d} / {esc(KINDS.get(e.get("kind"), e.get("kind", "Unclassified")))}</p>'
                 f'<h3 class="source-title">{esc(e.get("title") or e.get("url"))}</h3><span class="badge{ "" if verified else " alert"}">{label}</span>')
        if e.get('quote'):
            body += f'<div class="quote">{esc(e["quote"])}</div>'
        else:
            body += f'<p class="quiet">{esc(e.get("reason") or "This snapshot has no passage selected for the question. It supplies no assessed support.")}</p>'
        body += f'<p class="meta wrap">{esc(e.get("url"))}<br>Fetched {esc(e.get("fetched_at") or "not recorded")} · Discovery angle: {esc(e.get("angle", "not recorded"))}</p><div class="actions">'
        if e.get('snapshot_hash'):
            body += f'<a href="/cases/{cid}/sources/{eid}?version={version}&amp;offset=0">Read full saved source →</a>'
        body += external(e.get('url')) + '</div></article>'
    body += '</section></div><aside><section class="panel stamp"><h2>Check what changed</h2><p>Refresh preserves this version and creates a new snapshot. Dependent decisions are flagged when their evidence changes.</p>'
    body += f'<form method="post" action="/cases/{cid}/refresh">{mutation(csrf)}' + live_choice() + '<button>Refresh case →</button></form>'
    body += '<p class="quiet">Without live research, refresh can compare cached sources but cannot check the web for changes.</p></section><section class="panel"><h3>Saved versions</h3><nav aria-label="Saved case versions">'
    if version > 1:
        body += f'<a href="/cases/{cid}?version={version-1}">← Version {version-1}</a>'
    body += f'<span class="badge">Reading {version}</span>'
    if version < latest:
        body += f'<a href="/cases/{cid}?version={version+1}">Version {version+1} →</a>'
    body += f'</nav><p class="quiet"><a href="/cases/{cid}">Open latest snapshot</a></p></section>'
    body += '<section class="panel"><h3>What this case can establish</h3><p class="small">It preserves public source text and your stated reasoning. It does not infer which practice fits your repository.</p><p class="quiet">Repository uploads and experiment execution are available only through the local workflow, not this hosted workspace.</p></section></aside></div>'
    body += '<section id="changes" class="section"><div class="section-head"><h2><span class="step">02</span>What changed in this version</h2>'
    body += f'<span class="meta">Version {version-1} → {version}</span></div>' if version > 1 else '<span class="meta">Initial snapshot</span></div>'
    body += render_changes(case.get('changes', []))
    body += '<section id="decisions" class="section"><div class="section-head"><h2><span class="step">03</span>Decisions and their reasons</h2><span class="meta">Authored by you · bound to evidence versions</span></div>'
    for d in decisions:
        review = d.get('review', {})
        alert = review.get('state') == 'REVIEW_REQUIRED'
        superseded = review.get('state') == 'SUPERSEDED'
        label = ('REVIEW REQUIRED' if alert else 'SUPERSEDED' if superseded else
                 'Unchanged in saved snapshots' if review.get('state') == 'UNCHANGED_IN_SNAPSHOT' else
                 'Review state unavailable')
        body += (f'<article class="panel{ " stamp" if alert else ""}" id="decision-{segment(d["id"])}"><span class="badge{ " alert" if alert else ""}">{label}</span>'
                 f'<h3 style="margin-top:16px">{esc(d.get("statement"))}</h3><p>{esc(d.get("rationale"))}</p>'
                 f'<p class="meta">Recorded {esc(d.get("created_at"))} · <a href="/cases/{cid}?version={int(d.get("version",1))}">Evidence version {esc(d.get("version"))}</a></p>')
        if d.get('superseded_by'):
            body += f'<p class="small">Replaced by <a href="#decision-{segment(d["superseded_by"])}">a later decision ↓</a>. This earlier reasoning remains in the case history.</p>'
        if d.get('supersedes'):
            body += f'<p class="small">Replaces <a href="#decision-{segment(d["supersedes"])}">an earlier decision ↑</a>.</p>'
        body += '<p class="small">Evidence: '
        for eid in d.get('evidence_ids', []):
            body += f'<a href="/cases/{cid}/sources/{segment(eid)}?version={int(d.get("version",1))}&amp;offset=0">{esc(eid)}</a> '
        body += '</p>'
        if alert:
            body += render_changes(review.get('changes', []), nested=True)
        elif superseded and review.get('changes'):
            body += '<details><summary>Evidence changes at the time of review</summary>' + render_changes(review['changes'], nested=True) + '</details>'
        elif review.get('state') == 'UNCHANGED_IN_SNAPSHOT':
            body += '<p class="quiet">No change in the compared saved evidence. This does not establish that the web is unchanged.</p>'
        body += '</article>'
    if not decisions:
        body += '<p class="muted">No decision recorded yet. A source list becomes useful when you state what you will do and why.</p>'
    usable = [e for e in evidence if e.get('status') == 'QUOTE_VERIFIED']
    if usable and version == latest:
        body += (f'<section class="panel stamp"><h3>Record a decision</h3><p class="small">State your choice and explain how the cited evidence informs it. Saving does not mark the evidence as proof.</p>'
                 f'<form method="post" action="/cases/{cid}/decisions">{mutation(csrf)}{hidden("version", version)}')
        active_decisions = [d for d in decisions if not d.get('superseded_by') and d.get('review', {}).get('state') != 'SUPERSEDED']
        body += '<label for="supersedes">Is this a new choice or a revision?</label><select id="supersedes" name="supersedes"><option value="">New independent decision</option>'
        for d in active_decisions:
            statement = str(d.get('statement', ''))
            label = statement[:90] + ('…' if len(statement) > 90 else '')
            body += f'<option value="{esc(d["id"])}">Replace: {esc(label)}</option>'
        body += ('</select><p class="quiet">Replacing a decision makes your new choice active and keeps the earlier reasoning in history.</p>'
                 '<label for="statement">What will you do?</label><textarea id="statement" name="statement" rows="2" required maxlength="2000"></textarea>'
                 '<label for="rationale">Why this choice? What remains uncertain?</label><textarea id="rationale" name="rationale" rows="3" required maxlength="8000"></textarea>'
                 '<fieldset><legend>Evidence your decision depends on</legend><p class="quiet">Select at least one. Only sources with a located quote can be cited.</p>')
        for e in usable:
            body += (f'<label class="check evidence-choice"><input type="checkbox" name="evidence_ids" value="{esc(e["id"])}">'
                     f'<span>{esc(e.get("title") or e.get("url"))}<br><span class="small muted">{esc(e.get("quote", ""))}</span></span></label>')
        body += '</fieldset><button>Save decision and its reasons →</button></form></section>'
    elif not usable:
        body += '<div class="empty"><strong>Decision recording needs a source quote.</strong><p>Refresh with live research or create a case with public source URLs, then review the full source before citing it.</p></div>'
    body += '</section><section id="trace" class="section"><div class="section-head"><h2><span class="step">04</span>What actually ran</h2><span class="meta">Observed operations · no inferred routes</span></div>'
    trace = case.get('trace', [])
    if not trace:
        body += '<p class="muted">No route events were recorded for this snapshot.</p>'
    body += '<ol class="trace">'
    for i, event in enumerate(trace, 1):
        body += f'<li><span class="step">{i:02d}</span><strong>{esc(event.get("route"))}</strong> · {esc(event.get("outcome"))}'
        for key in ('angle','query','url','reason','cache_hit','sha256'):
            if key in event:
                body += f'<span class="meta">{esc(key.replace("_", " "))}: {esc(event[key])}</span>'
        body += '</li>'
    return shell(case.get('question', 'Research case'), body + '</ol></section>', csrf)


def render_changes(changes, nested=False):
    if not changes:
        return '<p class="muted">No source differences recorded for this revision. Cached reads do not check for web changes.</p>' + ('' if nested else '</section>')
    out = ''
    for change in changes:
        out += f'<article class="change"><h3>{esc(str(change.get("kind", "change")).replace("_", " ").capitalize())}</h3>'
        if change.get('url'):
            out += f'<p class="meta wrap">{esc(change["url"])}</p>'
        if change.get('reason'):
            out += f'<p>{esc(change["reason"])}</p>'
        out += '<div class="details-grid"><div><span class="meta">BEFORE</span><div class="quote">' + esc(change.get('before_quote') or 'No saved quote') + '</div></div>'
        out += '<div><span class="meta">AFTER</span><div class="quote">' + esc(change.get('after_quote') or 'No available quote') + '</div></div></div>'
        if change.get('kind') == 'not_returned':
            out += '<p class="quiet">Not returned by discovery does not mean the source was retracted.</p>'
        out += '</article>'
    return out + ('' if nested else '</section>')


def source_page(case_id, source, csrf=''):
    cid = segment(case_id)
    eid = segment(source['evidence_id'])
    version = int(source['version'])
    offset = int(source.get('offset',0))
    text = str(source.get('text',''))
    total = int(source.get('total_characters',len(text)))
    body = (f'<div class="hero"><p class="eyebrow">Saved source / evidence version {version}</p><h1>Read the source in context.</h1>'
            f'<p class="wrap">{external(source.get("url"), source.get("url") or "Original source")}</p>'
            f'<p><a href="/cases/{cid}?version={version}#evidence-{eid}">← Back to this case version</a></p></div>'
            '<div class="notice"><strong>This is saved source text.</strong><p>Its words are preserved for review. Quote occurrence does not establish that the source supports the decision.</p></div>'
            f'<p class="meta wrap">Fetched {esc(source.get("fetched_at") or "not recorded")}<br>SHA-256 {esc(source.get("sha256"))}</p>'
            f'<div class="section-head"><h2>Source text</h2><span class="meta">Characters {offset + 1 if text else offset}–{offset+len(text)} of {total}</span></div>'
            f'<pre class="source-text">{esc(text)}</pre><nav class="actions" aria-label="Source pagination">')
    if offset:
        body += f'<a class="button secondary" href="/cases/{cid}/sources/{eid}?version={version}&amp;offset=0">↑ Start of source</a>'
    nxt = source.get('next_offset')
    if nxt is not None:
        body += f'<a class="button" href="/cases/{cid}/sources/{eid}?version={version}&amp;offset={int(nxt)}">Continue source →</a>'
    else:
        body += '<span class="badge">End of saved source</span>'
    return shell('Saved source', body + '</nav>', csrf)


def error_page(message, code=400):
    return shell('Request could not be completed', f'<div class="login"><p class="eyebrow">Request {esc(code)}</p><h1>That action needs another look.</h1><div class="error" role="alert">{esc(message)}</div><a class="button secondary" href="/cases">Return to cases</a></div>', authenticated=False)
