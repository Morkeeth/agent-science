"""Durable attempt limits and duplicate-request reservations, shared by all instances.

Units are admitted live research runs, not dollars or provider calls. Failed and
interrupted jobs keep their reservation; a client retry must reuse its request ID.
"""
from datetime import datetime, timezone
import os
import hashlib


class Rejected(Exception):
    def __init__(self, message, status=429):
        super().__init__(message)
        self.status = status


class Budget:
    def __init__(self, store):
        self.store = store
        self.user_limit = int(os.getenv('AGENT_SCIENCE_DAILY_RESEARCH_LIMIT', '10'))
        self.global_limit = int(os.getenv('AGENT_SCIENCE_GLOBAL_RESEARCH_LIMIT', '50'))
        self.mutation_limit = int(os.getenv('AGENT_SCIENCE_DAILY_MUTATION_LIMIT', '100'))
        if min(self.user_limit, self.global_limit, self.mutation_limit) < 1:
            raise ValueError('request limits must be positive')

    @staticmethod
    def key():
        return 'usage-' + datetime.now(timezone.utc).strftime('%Y-%m-%d')

    def reserve(self, tenant, request_id, fingerprint, live):
        day = self.key()
        # A quick read prevents rejected floods from creating reservation objects.
        # The atomic daily check below remains the authority under concurrency.
        current = self.store.read_json(day)
        used = current.get('users', {}).get(tenant, {})
        if used.get('mutations', 0) >= self.mutation_limit or len(current.get('requests', {})) >= 1000:
            raise Rejected('Daily write limit reached. Read access remains available.')
        if live and (used.get('research', 0) >= self.user_limit or current.get('research', 0) >= self.global_limit):
            raise Rejected('Daily research limit reached. Read access remains available.')
        request_key = 'request-' + hashlib.sha256((tenant+':'+request_id).encode()).hexdigest()
        def claim(previous):
            if previous:
                if previous.get('fingerprint') != fingerprint:
                    raise Rejected('Request ID was already used for different input.', 409)
                raise Rejected('This request was already admitted. Reload to recover its saved result. If it did not complete, use a new request ID.', 409)
            return {'fingerprint':fingerprint,'day':day}, None
        # This reservation survives day rollover and process failure. A failure in
        # the later budget transaction fails closed; research has not started.
        self.store.atomic_json(request_key, claim)
        def update(data):
            requests = data.setdefault('requests', {})
            key = tenant + ':' + request_id
            if key in requests:
                previous = requests[key]
                if previous['fingerprint'] != fingerprint:
                    raise Rejected('Request ID was already used for different input.', 409)
                raise Rejected('This request was already admitted. Reload the workspace to recover a saved result. If no result was saved, start a new request; the earlier attempt still counts.', 409)
            user = data.setdefault('users', {}).setdefault(tenant, {'research': 0, 'mutations': 0})
            if user['mutations'] >= self.mutation_limit or len(requests) >= 1000:
                raise Rejected('Daily write limit reached. Read access remains available.')
            if live and (user['research'] >= self.user_limit or data.get('research', 0) >= self.global_limit):
                raise Rejected('Daily research limit reached. Read access remains available.')
            requests[key] = {'fingerprint': fingerprint}
            user['mutations'] += 1
            user['research'] += int(live)
            data['research'] = data.get('research', 0) + int(live)
            return data, None
        return self.store.atomic_json(day, update)

    def status(self, tenant):
        # Reading must not move the generation or manufacture activity.
        data = self.store.read_json(self.key())
        used = data.get('users', {}).get(tenant, {}).get('research', 0)
        return {'used': used, 'limit': self.user_limit,
                'remaining': max(0, min(self.user_limit-used, self.global_limit-data.get('research', 0))),
                'units': 'admitted live research runs', 'resets': '00:00 UTC',
                'note': 'Configured request limits; not a measurement of money spent. Failed attempts count.'}
