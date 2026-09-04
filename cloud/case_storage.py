"""Tenant workspaces with optimistic, generation-conditional persistence.

A workspace is a fresh private temporary database, never a copy of the operator's
local case store. Call commit explicitly after a successful mutation. A conflict
requires the caller to reload; this module never reruns research or other work.

atomic_json callbacks are different: they MUST be pure because a generation
conflict reruns the callback. Their signature is callback(current_dict) ->
(updated_dict, result). The result is returned only after its update commits.
"""
from __future__ import annotations

from contextlib import closing, contextmanager
import fcntl
import json
import os
from pathlib import Path
import re
import sqlite3
import tempfile
import time

DEFAULT_MAX_BYTES = 64 * 1024 * 1024
DEFAULT_JSON_MAX_BYTES = 1024 * 1024
DEFAULT_TIMEOUT = 30
_MAGIC = b"ASWS1\n"
_SLUG = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]*\Z")


class Conflict(RuntimeError):
    """The object changed since it was read. Nothing was overwritten."""


class StorageLimit(ValueError):
    """A workspace or metadata object exceeds its configured byte limit."""


def _name(value, *, maximum=128):
    if not isinstance(value, str) or len(value) > maximum or not _SLUG.fullmatch(value):
        raise ValueError("storage identifiers must be ASCII letters, digits, '_' or '-', starting with a letter or digit")
    return value


def _positive(value, name):
    value = int(value)
    if value <= 0:
        raise ValueError(f"{name} must be positive")
    return value


def _bounded(data, maximum):
    if len(data) > maximum:
        raise StorageLimit(f"stored object exceeds {maximum} bytes")
    return data


class LocalBackend:
    """Process-safe local CAS. Generation and bytes share one atomic file."""
    def __init__(self, root):
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True, mode=0o700)
        self.locks = self.root / ".locks"
        self.locks.mkdir(exist_ok=True, mode=0o700)

    def _path(self, key):
        return self.root / _name(key, maximum=256)

    @contextmanager
    def _lock(self, key, timeout):
        path = self.locks / _name(key, maximum=256)
        # Locks are separate, stable inodes: never replace or unlink a lock file.
        with path.open("a+b") as lock:
            deadline = time.monotonic() + timeout
            while True:
                try:
                    fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                    break
                except BlockingIOError:
                    if time.monotonic() >= deadline:
                        raise TimeoutError("workspace storage lock timed out")
                    time.sleep(min(0.01, max(0, deadline - time.monotonic())))
            try:
                yield
            finally:
                fcntl.flock(lock.fileno(), fcntl.LOCK_UN)

    def _read(self, key, maximum):
        try:
            stream = self._path(key).open("rb")
        except FileNotFoundError:
            return None, 0
        with stream:
            if stream.read(len(_MAGIC)) != _MAGIC:
                raise ValueError("invalid workspace storage header")
            line = stream.readline(40)
            if not line.endswith(b"\n") or not line.strip().isdigit():
                raise ValueError("invalid workspace generation")
            generation = int(line)
            return _bounded(stream.read(maximum + 1), maximum), generation

    def read(self, key, maximum, timeout):
        with self._lock(key, timeout):
            return self._read(key, maximum)

    def write(self, key, data, generation, maximum, timeout):
        _bounded(data, maximum)
        with self._lock(key, timeout):
            _, actual = self._read(key, maximum)
            if generation != actual:
                raise Conflict("workspace changed; reload before writing")
            next_generation = actual + 1
            fd, temporary = tempfile.mkstemp(prefix=".workspace-", dir=self.root)
            try:
                with os.fdopen(fd, "wb") as stream:
                    stream.write(_MAGIC + str(next_generation).encode("ascii") + b"\n" + data)
                    stream.flush()
                    os.fsync(stream.fileno())
                os.replace(temporary, self._path(key))
                # Preserve the rename across a system crash as well as process exit.
                directory = os.open(self.root, os.O_RDONLY)
                try:
                    os.fsync(directory)
                finally:
                    os.close(directory)
            finally:
                if os.path.exists(temporary):
                    os.unlink(temporary)
            return next_generation


class GCSBackend:
    """The bucket object may be injected in tests; policy stays in this class."""
    def __init__(self, bucket):
        self.bucket = bucket

    def _blob(self, key):
        return self.bucket.blob("agent-science-workspaces/" + _name(key, maximum=256))

    @staticmethod
    def _status(exc):
        return getattr(exc, "code", None)

    def read(self, key, maximum, timeout):
        blob = self._blob(key)
        try:
            blob.reload(timeout=timeout, retry=None)
        except Exception as exc:
            if self._status(exc) == 404:
                return None, 0
            raise
        generation = int(blob.generation)
        if blob.size is None or int(blob.size) > maximum:
            raise StorageLimit(f"stored object exceeds {maximum} bytes")
        try:
            # A bounded range protects memory even if metadata is stale or corrupt.
            # The generation condition binds bytes to exactly the metadata just read.
            data = blob.download_as_bytes(start=0, end=maximum,
                if_generation_match=generation, timeout=timeout, retry=None)
        except Exception as exc:
            if self._status(exc) in (404, 412):
                raise Conflict("workspace changed during download; reload") from exc
            raise
        return _bounded(data, maximum), generation

    def write(self, key, data, generation, maximum, timeout):
        _bounded(data, maximum)
        blob = self._blob(key)
        try:
            blob.upload_from_string(data, content_type="application/octet-stream",
                if_generation_match=generation, timeout=timeout, retry=None)
        except Exception as exc:
            if self._status(exc) == 412:
                raise Conflict("workspace changed; reload before writing") from exc
            raise
        return int(blob.generation)


class WorkspaceSession:
    def __init__(self, store, key, db, generation):
        self.db = db
        self._store = store
        self._key = key
        self._generation = generation
        self._closed = False

    def commit(self):
        """Persist a consistent SQLite backup, including committed WAL contents."""
        if self._closed:
            raise RuntimeError("workspace session is closed")
        if not self.db.is_file():
            raise ValueError("workspace database has not been initialized")
        if self.db.stat().st_size > self._store.max_bytes:
            raise StorageLimit("workspace database exceeds configured byte limit")
        snapshot = self.db.with_name("snapshot.sqlite")
        # Explicitly close our handles: sqlite's context manager only commits.
        with closing(sqlite3.connect(self.db, timeout=self._store.timeout)) as source, \
             closing(sqlite3.connect(snapshot, timeout=self._store.timeout)) as target:
            page_size = source.execute("PRAGMA page_size").fetchone()[0]
            deadline = time.monotonic() + self._store.timeout
            def progress(status, remaining, total):
                if total * page_size > self._store.max_bytes:
                    raise StorageLimit("workspace snapshot exceeds configured byte limit")
                if time.monotonic() >= deadline:
                    raise TimeoutError("workspace snapshot timed out")
            source.backup(target, pages=128, progress=progress, sleep=0.01)
        with snapshot.open("rb") as stream:
            data = _bounded(stream.read(self._store.max_bytes + 1), self._store.max_bytes)
        generation = self._store.backend.write(self._key, data, self._generation,
                                               self._store.max_bytes, self._store.timeout)
        self._generation = generation
        return generation


class WorkspaceStore:
    def __init__(self, backend, *, max_bytes=DEFAULT_MAX_BYTES,
                 json_max_bytes=DEFAULT_JSON_MAX_BYTES, timeout=DEFAULT_TIMEOUT):
        self.backend = backend
        self.max_bytes = _positive(max_bytes, "workspace byte limit")
        self.json_max_bytes = _positive(json_max_bytes, "metadata byte limit")
        self.timeout = _positive(timeout, "storage timeout")

    @classmethod
    def from_env(cls):
        bucket = os.environ.get("AGENT_SCIENCE_WORKSPACE_BUCKET", "").strip()
        local = os.environ.get("AGENT_SCIENCE_WORKSPACE_DIR", "").strip()
        if os.environ.get("K_SERVICE") and not bucket:
            raise ValueError("hosted workspaces require AGENT_SCIENCE_WORKSPACE_BUCKET")
        if bucket:
            if not re.fullmatch(r"[a-z0-9][a-z0-9._-]{1,220}[a-z0-9]", bucket):
                raise ValueError("invalid workspace bucket name")
            try:
                from google.cloud import storage
            except ImportError as exc:
                raise RuntimeError("hosted workspaces require google-cloud-storage") from exc
            backend = GCSBackend(storage.Client().bucket(bucket))
        elif local:
            backend = LocalBackend(local)
        else:
            raise ValueError("configure AGENT_SCIENCE_WORKSPACE_BUCKET or AGENT_SCIENCE_WORKSPACE_DIR")
        return cls(backend,
            max_bytes=os.environ.get("AGENT_SCIENCE_WORKSPACE_MAX_BYTES", DEFAULT_MAX_BYTES),
            json_max_bytes=os.environ.get("AGENT_SCIENCE_WORKSPACE_JSON_MAX_BYTES", DEFAULT_JSON_MAX_BYTES),
            timeout=os.environ.get("AGENT_SCIENCE_WORKSPACE_TIMEOUT", DEFAULT_TIMEOUT))

    @contextmanager
    def workspace(self, tenant):
        key = "db_" + _name(tenant, maximum=64)
        data, generation = self.backend.read(key, self.max_bytes, self.timeout)
        with tempfile.TemporaryDirectory(prefix="science-workspace-") as directory:
            db = Path(directory) / "cases.sqlite"
            if data is not None:
                db.write_bytes(data)
                data = None
            session = WorkspaceSession(self, key, db, generation)
            try:
                yield session
            finally:
                session._closed = True

    def read_json(self, key):
        """Read metadata without creating or updating its stored object."""
        key = "json_" + _name(key, maximum=128)
        raw, _ = self.backend.read(key, self.json_max_bytes, self.timeout)
        value = json.loads(raw) if raw is not None else {}
        if not isinstance(value, dict):
            raise ValueError("stored metadata must be a JSON object")
        return value

    def atomic_json(self, key, callback, *, max_attempts=8):
        """CAS-update metadata, rerunning only the caller's pure callback on conflict.

        callback(current_dict) -> (updated_dict, result). Missing objects start as
        {}. Errors other than a generation conflict are never retried. Exhausted
        conflicts raise Conflict; there is no unconditional-write fallback.
        """
        key = "json_" + _name(key, maximum=128)
        if not 1 <= max_attempts <= 32:
            raise ValueError("metadata attempts must be between 1 and 32")
        for _ in range(max_attempts):
            try:
                raw, generation = self.backend.read(key, self.json_max_bytes, self.timeout)
            except Conflict:
                continue
            current = json.loads(raw) if raw is not None else {}
            if not isinstance(current, dict):
                raise ValueError("stored metadata must be a JSON object")
            updated, result = callback(current)
            if not isinstance(updated, dict):
                raise ValueError("metadata callback must return (dict, result)")
            data = json.dumps(updated, allow_nan=False, separators=(",", ":")).encode("utf-8")
            _bounded(data, self.json_max_bytes)
            try:
                self.backend.write(key, data, generation, self.json_max_bytes, self.timeout)
            except Conflict:
                continue
            return result
        raise Conflict("metadata changed repeatedly; retry the request")
