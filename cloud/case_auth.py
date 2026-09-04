"""Invite keys and signed, expiring browser sessions. No credentials in URLs."""
from __future__ import annotations
import base64
import hashlib
import hmac
import json
import os
import re
import secrets
import time
from http.cookies import SimpleCookie


class Auth:
    def __init__(self, config=None, *, clock=time.time):
        self.clock = clock
        config = config if config is not None else json.loads(os.environ['AGENT_SCIENCE_ACCESS_CONFIG'])
        self.key = config['session_key'].encode()
        self.users = config['users']
        if len(self.key) < 43 or not isinstance(self.users, dict) or not self.users:
            raise ValueError('access configuration needs a random session key and users')
        for tenant, hashed in self.users.items():
            if not re.fullmatch(r'[a-zA-Z0-9][a-zA-Z0-9_-]{0,63}', tenant) or not re.fullmatch(r'[a-f0-9]{64}', hashed):
                raise ValueError('invalid workspace access configuration')

    def token_user(self, token):
        if not isinstance(token, str) or not 32 <= len(token) <= 200:
            return None
        hashed = hashlib.sha256(token.encode()).hexdigest()
        found = None
        for user, expected in self.users.items():
            if hmac.compare_digest(hashed, expected):
                found = user
        return found

    def sign(self, text):
        return hmac.new(self.key, text.encode(), hashlib.sha256).hexdigest()

    def session(self, tenant):
        data = [tenant, int(self.clock()) + 12*3600, secrets.token_urlsafe(24), self.users[tenant]]
        body = base64.urlsafe_b64encode(json.dumps(data, separators=(',', ':')).encode()).decode().rstrip('=')
        return body + '.' + self.sign(body)

    def session_user(self, value):
        try:
            if len(value) > 1000:
                return None
            body, signature = value.split('.')
            if not hmac.compare_digest(signature, self.sign(body)):
                return None
            tenant, expires, nonce, credential = json.loads(base64.urlsafe_b64decode(body + '='*(-len(body)%4)))
            if (tenant not in self.users or credential != self.users[tenant] or not isinstance(expires, int)
                    or not self.clock() < expires <= self.clock() + 12*3600 or not isinstance(nonce, str)):
                return None
            return tenant
        except (ValueError, TypeError, KeyError):
            return None

    def identify(self, headers):
        bearer = headers.get('Authorization', '')
        if bearer:
            return self.token_user(bearer[7:]) if bearer.startswith('Bearer ') else None, None
        cookie = SimpleCookie()
        try:
            cookie.load(headers.get('Cookie', ''))
            value = cookie['as_session'].value if 'as_session' in cookie else ''
        except Exception:
            return None, None
        return self.session_user(value), value

    def csrf(self, session):
        return self.sign('csrf:' + session)

    def valid_csrf(self, session, value):
        return isinstance(value, str) and hmac.compare_digest(self.csrf(session), value)
