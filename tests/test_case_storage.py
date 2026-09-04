"""Durable workspace behavior against real local files and a GCS transport double."""
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from cloud.case_storage import Conflict, GCSBackend, LocalBackend, StorageLimit, WorkspaceStore


def fill(path, value):
    con = sqlite3.connect(path)
    try:
        con.execute('CREATE TABLE IF NOT EXISTS values_seen(value TEXT)')
        con.execute('INSERT INTO values_seen VALUES(?)', (value,))
        con.commit()
    finally:
        con.close()


def values(path):
    con = sqlite3.connect(path)
    try:
        return [r[0] for r in con.execute('SELECT value FROM values_seen')]
    finally:
        con.close()


class LocalWorkspaceTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.store = WorkspaceStore(LocalBackend(self.root))

    def test_commit_persists_across_store_instances_and_tenants_are_isolated(self):
        with self.store.workspace('tenant_a') as session:
            first_path = session.db
            fill(session.db, 'private to a')
            session.commit()
        self.assertFalse(first_path.exists())
        other = WorkspaceStore(LocalBackend(self.root))
        with other.workspace('tenant_a') as session:
            self.assertEqual(values(session.db), ['private to a'])
        with other.workspace('tenant_b') as session:
            self.assertFalse(session.db.exists())
            fill(session.db, 'private to b')
            session.commit()
        with other.workspace('tenant_a') as session:
            self.assertEqual(values(session.db), ['private to a'])

    def test_two_stale_writers_cannot_overwrite_each_other(self):
        second_store = WorkspaceStore(LocalBackend(self.root))
        with self.store.workspace('tenant') as first, second_store.workspace('tenant') as second:
            fill(first.db, 'winner')
            fill(second.db, 'stale writer')
            first.commit()
            with self.assertRaises(Conflict):
                second.commit()
            losing_path = second.db
        self.assertFalse(losing_path.exists())
        with self.store.workspace('tenant') as session:
            self.assertEqual(values(session.db), ['winner'])

    def test_separate_process_stale_writer_cannot_replace_parent_commit(self):
        code = r"""
import sqlite3, sys
from cloud.case_storage import WorkspaceStore, LocalBackend, Conflict
store = WorkspaceStore(LocalBackend(sys.argv[1]))
with store.workspace('tenant') as session:
    con = sqlite3.connect(session.db)
    con.execute('CREATE TABLE values_seen(value TEXT)')
    con.execute("INSERT INTO values_seen VALUES('child stale write')")
    con.commit(); con.close()
    print('ready', flush=True)
    sys.stdin.readline()
    try:
        session.commit()
        print('overwritten', flush=True)
    except Conflict:
        print('conflict', flush=True)
"""
        proc = subprocess.Popen([sys.executable, '-c', code, str(self.root)],
            cwd=Path(__file__).resolve().parents[1], stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            self.assertEqual(proc.stdout.readline().strip(), 'ready')
            with self.store.workspace('tenant') as session:
                fill(session.db, 'parent committed')
                session.commit()
            output, error = proc.communicate('commit\n', timeout=10)
            self.assertEqual(proc.returncode, 0, error)
            self.assertEqual(output.strip(), 'conflict')
        finally:
            if proc.poll() is None:
                proc.kill(); proc.wait()
        with self.store.workspace('tenant') as session:
            self.assertEqual(values(session.db), ['parent committed'])

    def test_tenant_names_cannot_collide_with_lock_files(self):
        with self.store.workspace('tenant') as session:
            fill(session.db, 'first'); session.commit()
        with self.store.workspace('tenant_lock') as session:
            self.assertFalse(session.db.exists())
            fill(session.db, 'second'); session.commit()
        with self.store.workspace('tenant') as session:
            self.assertEqual(values(session.db), ['first'])

    def test_read_only_session_and_exception_never_commit(self):
        with self.store.workspace('tenant') as session:
            fill(session.db, 'not committed')
        with self.store.workspace('tenant') as session:
            self.assertFalse(session.db.exists())
        with self.assertRaisesRegex(RuntimeError, 'failed operation'):
            with self.store.workspace('tenant') as session:
                db = session.db
                fill(db, 'also not committed')
                raise RuntimeError('failed operation')
        self.assertFalse(db.exists())
        self.assertFalse((self.root / 'db_tenant').exists())
        with self.assertRaisesRegex(RuntimeError, 'closed'):
            session.commit()

    def test_multiple_commits_update_the_sessions_generation(self):
        with self.store.workspace('tenant') as session:
            fill(session.db, 'one')
            self.assertEqual(session.commit(), 1)
            fill(session.db, 'two')
            self.assertEqual(session.commit(), 2)
        with self.store.workspace('tenant') as session:
            self.assertEqual(values(session.db), ['one', 'two'])

    def test_backup_includes_committed_wal_while_writer_handle_is_open(self):
        with self.store.workspace('tenant') as session:
            con = sqlite3.connect(session.db)
            try:
                con.execute('PRAGMA journal_mode=WAL')
                con.execute('CREATE TABLE values_seen(value TEXT)')
                con.execute("INSERT INTO values_seen VALUES('committed WAL')")
                con.commit()
                self.assertTrue(Path(str(session.db) + '-wal').exists())
                session.commit()
            finally:
                con.close()
        with self.store.workspace('tenant') as session:
            self.assertEqual(values(session.db), ['committed WAL'])

    def test_snapshot_limit_does_not_store_partial_database(self):
        small = WorkspaceStore(LocalBackend(self.root), max_bytes=4096)
        with small.workspace('tenant') as session:
            fill(session.db, 'requires more than one sqlite page')
            with self.assertRaises(StorageLimit):
                session.commit()
        self.assertFalse((self.root / 'db_tenant').exists())

    def test_existing_oversized_object_is_rejected_on_read(self):
        self.store.backend.write('db_tenant', b'x' * 100, 0, 100, 1)
        small = WorkspaceStore(LocalBackend(self.root), max_bytes=50)
        with self.assertRaises(StorageLimit):
            with small.workspace('tenant'):
                self.fail('must reject before exposing a workspace')

    def test_identifiers_cannot_escape_storage_or_cross_namespaces(self):
        for value in ['', '../other', 'a/b', '/tmp/db', 'a.b', 'a\\b', 'é', 'a' * 129]:
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    self.store.read_json(value)
                with self.assertRaises(ValueError):
                    with self.store.workspace(value):
                        pass
        self.store.atomic_json('same', lambda d: ({'ok': True}, None))
        with self.store.workspace('same') as session:
            self.assertFalse(session.db.exists())

    def test_atomic_json_retries_pure_callback_without_lost_updates(self):
        parties = 6
        barrier = threading.Barrier(parties)
        calls = []
        def update(worker):
            first = True
            def callback(current):
                nonlocal first
                calls.append(worker)
                if first:
                    first = False
                    barrier.wait(timeout=5)
                count = current.get('count', 0) + 1
                return {'count': count}, count
            return self.store.atomic_json('budget_tenant', callback, max_attempts=32)
        with ThreadPoolExecutor(max_workers=parties) as pool:
            results = list(pool.map(update, range(parties)))
        self.assertEqual(sorted(results), list(range(1, parties + 1)))
        self.assertEqual(self.store.read_json('budget_tenant'), {'count': parties})
        self.assertGreater(len(calls), parties)

    def test_metadata_reads_do_not_create_objects_and_invalid_updates_fail(self):
        self.assertEqual(self.store.read_json('absent'), {})
        self.assertFalse((self.root / 'json_absent').exists())
        with self.assertRaises(ValueError):
            self.store.atomic_json('bad', lambda d: ([], None))
        with self.assertRaises(ValueError):
            self.store.atomic_json('bad', lambda d: ({'bad': float('nan')}, None))
        with self.assertRaises(StorageLimit):
            WorkspaceStore(LocalBackend(self.root), json_max_bytes=10).atomic_json(
                'large', lambda d: ({'text': 'x' * 100}, None))
        self.assertFalse((self.root / 'json_large').exists())

    def test_callback_exceptions_are_not_retried(self):
        calls = []
        def failed(current):
            calls.append(current)
            raise Conflict('caller failure')
        with self.assertRaisesRegex(Conflict, 'caller failure'):
            self.store.atomic_json('budget', failed)
        self.assertEqual(len(calls), 1)

    def test_hosted_env_fails_closed_without_bucket_and_local_env_is_explicit(self):
        with patch.dict(os.environ, {'K_SERVICE': 'cloud-run',
                                    'AGENT_SCIENCE_WORKSPACE_DIR': str(self.root)}, clear=True):
            with self.assertRaisesRegex(ValueError, 'require.*BUCKET'):
                WorkspaceStore.from_env()
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError):
                WorkspaceStore.from_env()
        with patch.dict(os.environ, {'AGENT_SCIENCE_WORKSPACE_DIR': str(self.root)}, clear=True):
            self.assertIsInstance(WorkspaceStore.from_env().backend, LocalBackend)


class TransportError(Exception):
    def __init__(self, code):
        self.code = code


class FakeBucket:
    """In-memory external-object effects, including server-side preconditions."""
    def __init__(self):
        self.objects = {}
        self.calls = []
        self.before_download = None
        self.upload_error = None

    def blob(self, key):
        bucket = self
        class Blob:
            def reload(self, **kwargs):
                bucket.calls.append(('reload', key, kwargs))
                if key not in bucket.objects:
                    raise TransportError(404)
                self.generation, data = bucket.objects[key]
                self.size = len(data)

            def download_as_bytes(self, **kwargs):
                bucket.calls.append(('download', key, kwargs))
                if bucket.before_download:
                    bucket.before_download(key)
                generation, data = bucket.objects[key]
                if kwargs['if_generation_match'] != generation:
                    raise TransportError(412)
                return data[kwargs['start']:kwargs['end'] + 1]

            def upload_from_string(self, data, **kwargs):
                bucket.calls.append(('upload', key, kwargs))
                if bucket.upload_error:
                    raise bucket.upload_error
                actual = bucket.objects.get(key, (0, None))[0]
                if kwargs['if_generation_match'] != actual:
                    raise TransportError(412)
                self.generation = actual + 1
                bucket.objects[key] = (self.generation, data)
        return Blob()


class GCSPolicyTests(unittest.TestCase):
    def setUp(self):
        self.bucket = FakeBucket()
        self.backend = GCSBackend(self.bucket)
        self.store = WorkspaceStore(self.backend)

    def test_missing_object_uses_zero_generation_and_every_write_is_conditional(self):
        self.assertEqual(self.backend.read('db_tenant', 100, 3), (None, 0))
        self.assertEqual(self.backend.write('db_tenant', b'one', 0, 100, 3), 1)
        with self.assertRaises(Conflict):
            self.backend.write('db_tenant', b'lost update', 0, 100, 3)
        self.assertEqual(self.backend.read('db_tenant', 100, 3), (b'one', 1))
        for action, key, kwargs in self.bucket.calls:
            self.assertIsNone(kwargs['retry'])
            self.assertEqual(kwargs['timeout'], 3)
            if action in ('upload', 'download'):
                self.assertIn('if_generation_match', kwargs)
        download = next(c for c in self.bucket.calls if c[0] == 'download')
        self.assertEqual(download[2]['end'], 100)

    def test_metadata_and_document_race_does_not_return_different_generation(self):
        self.backend.write('db_tenant', b'one', 0, 100, 3)
        self.bucket.before_download = lambda key: self.bucket.objects.update({key: (2, b'two')})
        with self.assertRaises(Conflict):
            self.backend.read('db_tenant', 100, 3)

    def test_oversized_remote_object_is_never_downloaded(self):
        self.bucket.objects['agent-science-workspaces/db_tenant'] = (1, b'x' * 100)
        with self.assertRaises(StorageLimit):
            self.backend.read('db_tenant', 20, 3)
        self.assertFalse(any(c[0] == 'download' for c in self.bucket.calls))

    def test_workspace_cas_rejects_second_instance_and_does_not_replay(self):
        with self.store.workspace('tenant') as a, self.store.workspace('tenant') as b:
            fill(a.db, 'a'); fill(b.db, 'b')
            a.commit()
            with self.assertRaises(Conflict):
                b.commit()
        uploads = [c for c in self.bucket.calls if c[0] == 'upload']
        self.assertEqual(len(uploads), 2)
        with self.store.workspace('tenant') as session:
            self.assertEqual(values(session.db), ['a'])

    def test_only_precondition_failures_retry_for_metadata(self):
        self.bucket.upload_error = TransportError(503)
        with self.assertRaises(TransportError):
            self.store.atomic_json('budget', lambda d: ({'count': 1}, 1))
        self.assertEqual(sum(c[0] == 'upload' for c in self.bucket.calls), 1)
        self.bucket.calls.clear()
        self.bucket.upload_error = TransportError(412)
        with self.assertRaises(Conflict):
            self.store.atomic_json('budget', lambda d: ({'count': 1}, 1), max_attempts=3)
        uploads = [c for c in self.bucket.calls if c[0] == 'upload']
        self.assertEqual(len(uploads), 3)
        self.assertTrue(all(c[2]['if_generation_match'] == 0 for c in uploads))


if __name__ == '__main__':
    unittest.main()
