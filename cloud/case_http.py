"""Private hosted research workspace. Legacy public research routes are not exposed.

All cloud writes use generation preconditions; network work is never replayed on
conflict. Completed request receipts and case changes share one durable snapshot.
"""
from __future__ import annotations
import hashlib
from contextlib import contextmanager, closing
import json
import os
from pathlib import Path
import re
import signal
import sqlite3
import subprocess
import sys
from urllib.parse import parse_qs, urlsplit

from clearance import cases
from cloud.case_auth import Auth
from cloud.case_budget import Budget, Rejected
from cloud.case_storage import WorkspaceStore, Conflict
from cloud import case_pages

MAX_BODY = 32768
CASE_ID = r'[a-f0-9]{12}'
EVIDENCE_ID = r'[a-f0-9]{16}'


class HTTPError(Exception):
    def __init__(self, status, message):
        super().__init__(message)
        self.status = status


def required_text(data, key, maximum, *, optional=False):
    value = data.get(key, '')
    if not isinstance(value, str) or len(value) > maximum or (not optional and not value.strip()):
        raise HTTPError(400, f'{key} must be text with {"0" if optional else "1"}–{maximum} characters.')
    return value.strip()


def strings(data, key, limit, max_length):
    values = data.get(key, [])
    if isinstance(values, str):
        values = [v.strip() for v in values.splitlines() if v.strip()]
    if not isinstance(values, list) or len(values) > limit or any(not isinstance(v, str) or len(v) > max_length for v in values):
        raise HTTPError(400, f'{key} must contain at most {limit} short text entries.')
    return values


def integer(value, name, minimum=1, maximum=100000):
    try:
        if isinstance(value, bool):
            raise ValueError()
        n = int(value)
        if str(n) != str(value) or not minimum <= n <= maximum:
            raise ValueError()
        return n
    except (ValueError, TypeError):
        raise HTTPError(400, f'Invalid {name}.') from None


@contextmanager
def receipts(db):
    with closing(sqlite3.connect(db)) as con, con:
        con.execute('CREATE TABLE IF NOT EXISTS hosted_requests(id TEXT PRIMARY KEY, fingerprint TEXT NOT NULL, result TEXT NOT NULL)')
        yield con


def research(payload, db):
    """Bound wall time and process tree; do not forward private provider stderr."""
    timeout = min(210, max(1, int(os.getenv('AGENT_SCIENCE_RESEARCH_TIMEOUT', '180'))))
    env = dict(os.environ)
    # The worker has provider credentials but never workspace access/session keys.
    env.pop('AGENT_SCIENCE_ACCESS_CONFIG', None)
    proc = subprocess.Popen([sys.executable, '-m', 'cloud.case_worker', str(db)],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
        start_new_session=True, env=env, cwd=Path(__file__).resolve().parent.parent)
    try:
        stdout, _ = proc.communicate(json.dumps(payload).encode(), timeout=timeout)
        if proc.returncode or len(stdout) > 8192:
            raise HTTPError(502, 'Research did not complete. The attempt remains counted. Reload before trying again.')
        result = json.loads(stdout)
        if not re.fullmatch(CASE_ID, result.get('case_id', '')):
            raise ValueError('invalid worker result')
        return result
    except subprocess.TimeoutExpired:
        raise HTTPError(504, 'Research reached its time limit. No case change was saved. The attempt remains counted.') from None
    finally:
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        proc.communicate()


class WorkspaceHTTP:
    def __init__(self, handler, *, store=None, auth=None):
        self.h = handler
        self.store = store
        self.auth = auth
        self.api = urlsplit(handler.path).path.startswith('/api/')
        self.secure = bool(os.getenv('K_SERVICE')) or os.getenv('AGENT_SCIENCE_ALLOW_HTTP') != '1'

    def send(self, code, payload='', *, location=None, cookie=None):
        if isinstance(payload, dict):
            body, content_type = json.dumps(payload).encode(), 'application/json; charset=utf-8'
        else:
            body, content_type = payload.encode(), 'text/html; charset=utf-8'
        h = self.h
        h.send_response(code)
        for key, value in {
            'Content-Type': content_type, 'Content-Length': str(len(body)),
            'Cache-Control': 'no-store', 'Referrer-Policy': 'no-referrer',
            'X-Content-Type-Options': 'nosniff', 'X-Frame-Options': 'DENY',
            'Content-Security-Policy': "default-src 'none'; style-src 'unsafe-inline'; form-action 'self'; base-uri 'none'; frame-ancestors 'none'",
            'Connection': 'close',
        }.items():
            h.send_header(key, value)
        if self.secure:
            h.send_header('Strict-Transport-Security', 'max-age=31536000')
        if location:
            h.send_header('Location', location)
        if cookie is not None:
            h.send_header('Set-Cookie', 'as_session=' + cookie + '; Path=/; HttpOnly; SameSite=Strict' +
                          ('; Secure' if self.secure else '') + ('; Max-Age=43200' if cookie else '; Max-Age=0'))
        h.end_headers()
        h.close_connection = True
        h.wfile.write(body)

    def origin(self):
        expected = os.getenv('AGENT_SCIENCE_PUBLIC_ORIGIN', '').rstrip('/')
        if not expected or self.h.headers.get('Origin') != expected:
            raise HTTPError(403, 'This form must be submitted from the workspace address.')

    def body(self):
        h = self.h
        if h.headers.get('Transfer-Encoding') or len(h.headers.get_all('Content-Length', [])) != 1:
            raise HTTPError(400, 'A single Content-Length header is required.')
        length = integer(h.headers.get('Content-Length'), 'content length', 1, MAX_BODY)
        h.connection.settimeout(10)
        raw = h.rfile.read(length)
        if len(raw) != length:
            raise HTTPError(400, 'Incomplete request body.')
        try:
            kind = h.headers.get('Content-Type', '').split(';')[0]
            if kind == 'application/json':
                data = json.loads(raw)
                if not isinstance(data, dict):
                    raise ValueError()
                return data
            if kind == 'application/x-www-form-urlencoded' and not self.api:
                parsed = parse_qs(raw.decode(), keep_blank_values=True, max_num_fields=60)
                return {k: (v if k == 'evidence_ids' else v[0]) for k, v in parsed.items()}
        except (ValueError, UnicodeError):
            raise HTTPError(400, 'Invalid request body.') from None
        raise HTTPError(415, 'Use JSON for the API or a workspace form.')

    def handle(self):
        try:
            self.route()
        except (HTTPError, Rejected) as exc:
            self.send(exc.status, {'error': str(exc)} if self.api else case_pages.error_page(str(exc), exc.status))
        except Conflict:
            self.send(409, {'error': 'Workspace changed during this request. Reload; no newer data was overwritten.'} if self.api else
                      case_pages.error_page('Workspace changed during this request. Reload; no newer data was overwritten.', 409))
        except ValueError:
            self.send(400, {'error': 'Case, version or evidence was not found, or the input was invalid.'} if self.api else
                      case_pages.error_page('Case, version or evidence was not found, or the input was invalid.', 400))
        except (BrokenPipeError, ConnectionResetError):
            pass
        except Exception as exc:
            # Only exception class; never request body, query, session or provider text.
            sys.stderr.write('workspace failure: ' + type(exc).__name__ + '\n')
            self.send(503, {'error': 'Workspace is temporarily unavailable. No success is claimed; reload before retrying.'} if self.api else
                      case_pages.error_page('Workspace is temporarily unavailable. Reload before retrying.', 503))

    def route(self):
        h = self.h
        if len(h.path) > 4096:
            raise HTTPError(414, 'Request URL is too long.')
        parsed = urlsplit(h.path)
        path = parsed.path.rstrip('/') or '/'
        if h.command == 'GET' and path == '/health':
            return self.send(200, {'ok': True, 'service': 'agent-science', 'mode': 'private-workspaces',
                                   'revision': os.getenv('K_REVISION', 'local')})
        self.auth = self.auth or Auth()
        tenant, session = self.auth.identify(h.headers)
        if path == '/login':
            if h.command == 'GET':
                return self.send(200, case_pages.login(secure=self.secure))
            self.origin()
            data = self.body()
            user = self.auth.token_user(required_text(data, 'token', 200))
            if not user:
                return self.send(401, case_pages.login(error='Access key was not accepted.', secure=self.secure))
            return self.send(303, location='/cases', cookie=self.auth.session(user))
        if not tenant:
            if self.api or h.command != 'GET':
                raise HTTPError(401, 'Workspace access key required.')
            return self.send(303, location='/login')
        if h.command not in ('GET', 'POST'):
            raise HTTPError(405, 'Method not supported.')
        self.store = self.store or WorkspaceStore.from_env()
        budget = Budget(self.store)
        csrf = self.auth.csrf(session) if session else ''
        if h.command == 'POST':
            data = self.body()
            if session:
                self.origin()
                if not self.auth.valid_csrf(session, data.get('csrf')):
                    raise HTTPError(403, 'Form session expired. Reload and submit again.')
            if path == '/logout':
                return self.send(303, location='/login', cookie='')
            return self.mutate(path, data, tenant, budget)
        if path in ('/', '/index.html'):
            return self.send(303, location='/cases')
        query = parse_qs(parsed.query, max_num_fields=10)
        version = integer(query['version'][0], 'version') if 'version' in query else None
        base = path.removeprefix('/api') if self.api else path
        with self.store.workspace(tenant) as ws:
            if base == '/cases':
                page = integer(query.get('page',['1'])[0], 'page', 1, 100000)
                rows = cases.recent(db=ws.db, limit=21, offset=(page-1)*20)
                has_more = len(rows)>20
                rows = rows[:20]
                allowance = budget.status(tenant)
                return self.send(200, {'cases': [cases.public_view(c) for c in rows], 'budget': allowance, 'page': page, 'has_more': has_more} if self.api else
                                 case_pages.dashboard(rows, csrf, allowance, page=page, has_more=has_more))
            match = re.fullmatch('/cases/(' + CASE_ID + ')(?:/sources/(' + EVIDENCE_ID + '))?', base)
            if not match:
                raise HTTPError(404, 'Route not found. Use /cases for private research.')
            cid, eid = match.groups()
            if eid:
                offset = integer(query.get('offset', ['0'])[0], 'offset', 0, 10000000)
                source = cases.source(cid, eid, db=ws.db, version=version, offset=offset)
                return self.send(200, source if self.api else case_pages.source_page(cid, source, csrf))
            case = cases.get(cid, db=ws.db, version=version)
            case['latest_version'] = cases.get(cid, db=ws.db)['version']
            return self.send(200, cases.public_view(case) if self.api else case_pages.detail(case, csrf))

    def mutate(self, path, data, tenant, budget):
        base = path.removeprefix('/api') if self.api else path
        match = re.fullmatch('/cases/(' + CASE_ID + ')/(refresh|decisions)', base)
        if base != '/cases' and not match:
            raise HTTPError(404, 'Mutation route not found.')
        rid = required_text(data, 'request_id', 64)
        if not re.fullmatch(r'[a-zA-Z0-9_-]{16,64}', rid):
            raise HTTPError(400, 'request_id must contain 16–64 letters, digits, underscores or hyphens.')
        live = data.get('live', False)
        if isinstance(live, str) and not self.api:
            live = live in ('on', 'true', '1')
        if not isinstance(live, bool):
            raise HTTPError(400, 'live must be a boolean.')
        payload = {'action': 'create' if not match else match[2], 'live': live}
        if match:
            payload['case_id'] = match[1]
        if payload['action'] == 'create':
            payload.update(question=required_text(data, 'question', 1500),
                           sources=strings(data, 'sources', 12, 2048),
                           official_domains=strings(data, 'official_domains', 12, 253))
            from clearance.safe_fetch import validate_url
            for url in payload['sources']:
                validate_url(url)
            if any(not re.fullmatch(r'[a-zA-Z0-9.-]+', d) or '.' not in d for d in payload['official_domains']):
                raise HTTPError(400, 'Official domains must be hostnames.')
        elif payload['action'] == 'decisions':
            payload.update(statement=required_text(data, 'statement', 2000), rationale=required_text(data, 'rationale', 8000),
                           evidence_ids=strings(data, 'evidence_ids', 24, 16),
                           version=integer(data.get('version'), 'version'), live=False,
                           supersedes=required_text(data,'supersedes',12,optional=True) or None)
        # Reject server filesystem/execution and unknown arguments rather than silently accepting them.
        allowed = {'csrf','request_id','question','sources','official_domains','live'} if not match else (
            {'csrf','request_id','live','version'} if payload['action']=='refresh' else
            {'csrf','request_id','version','statement','rationale','evidence_ids','supersedes'})
        if set(data)-allowed:
            raise HTTPError(400, 'Unsupported request fields.')
        fingerprint = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(',',':')).encode()).hexdigest()
        with self.store.workspace(tenant) as ws:
            with receipts(ws.db) as con:
                row = con.execute('SELECT fingerprint,result FROM hosted_requests WHERE id=?', (rid,)).fetchone()
            if row:
                if row[0] != fingerprint:
                    raise HTTPError(409, 'Request ID was already used for different input.')
                result = json.loads(row[1])
                return self.send(200, result) if self.api else self.send(303, location='/cases/'+result['case_id'])
            if match:
                current = cases.get(payload['case_id'], db=ws.db)
                if payload['action'] == 'decisions':
                    if current['version'] != payload['version']:
                        raise HTTPError(409, 'Evidence changed. Read the latest version before recording a decision.')
                    available = {e['id'] for e in current['evidence'] if e['status']=='QUOTE_VERIFIED'}
                    if not payload['evidence_ids'] or not set(payload['evidence_ids']) <= available:
                        raise HTTPError(400, 'Select at least one verified quote from this version.')
                    if payload['supersedes'] and not any(d['id']==payload['supersedes'] and not d.get('superseded_by') for d in current['decisions']):
                        raise HTTPError(409, 'Decision was already superseded or does not belong to this case.')
            budget.reserve(tenant, rid, fingerprint, payload['live'])
            if payload['action'] == 'decisions':
                result_case = cases.decide(payload['case_id'],payload['statement'],payload['rationale'],payload['evidence_ids'],db=ws.db,supersedes=payload['supersedes'])
                result = {'case_id': result_case['id'], 'version': result_case['version']}
            else:
                result = research(payload, ws.db)
            with receipts(ws.db) as con:
                con.execute('INSERT INTO hosted_requests VALUES(?,?,?)', (rid,fingerprint,json.dumps(result)))
            ws.commit()
        return self.send(201, result) if self.api else self.send(303, location='/cases/'+result['case_id'])
