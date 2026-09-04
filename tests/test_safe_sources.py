"""Exercise the actual source boundary with only DNS and HTTP effects replaced."""
import hashlib
import io
import json
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import MagicMock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from clearance import instruments, ingest, safe_fetch as S


def public_dns(*args, **kwargs):
    return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", 443))]


class Response:
    def __init__(self, body=b"document", status=200, headers=None):
        self.status = status
        self.headers = headers or {}
        self.body = io.BytesIO(body)

    def getheader(self, key, default=None):
        return self.headers.get(key, default)

    def read1(self, n):
        return self.body.read(n)

    def close(self):
        self.body.close()


class Connection:
    def __init__(self, response):
        self.response = response
        self.sock = None

    def request(self, *args, **kwargs):
        pass

    def getresponse(self):
        return self.response

    def close(self):
        pass


class SafeFetchTests(unittest.TestCase):
    def test_rejects_non_public_and_non_http_before_transport(self):
        urls = ["file:///tmp/canary", "ftp://example.com/x", "http://localhost/",
                "http://127.0.0.1", "http://127.1", "http://10.0.0.1",
                "http://169.254.169.254", "http://[::1]", "http://[fc00::1]",
                "http://192.168.1.1", "http://0.0.0.0", "http://224.0.0.1",
                "https://user:password@example.com", "http://[::ffff:127.0.0.1]",
                "http://example.com\\@127.0.0.1", "https://example.com\n/x"]
        # Alternative IPv4 spellings go through real DNS-address validation.
        def private_dns(*args, **kwargs):
            return [(2, 1, 6, "", ("127.0.0.1", 80))]
        with patch.object(socket, "getaddrinfo", side_effect=private_dns), \
             patch.object(S, "_connection") as connect:
            for url in urls:
                with self.subTest(url=url), self.assertRaises(S.UnsafeSource):
                    S.fetch_public(url)
            connect.assert_not_called()

    def test_mixed_dns_answers_rejected(self):
        rows = public_dns() + [(2, 1, 6, "", ("10.1.2.3", 443))]
        with patch.object(socket, "getaddrinfo", return_value=rows), \
             patch.object(S, "_connection") as connect:
            with self.assertRaises(S.UnsafeSource):
                S.fetch_public("https://example.com")
            connect.assert_not_called()

    def test_redirect_to_private_host_blocked_before_second_connection(self):
        for location in ["http://127.0.0.1/", "file:///tmp/test", "http://private.example/"]:
            def dns(host, *args, **kwargs):
                return public_dns() if host == "example.com" else [(2, 1, 6, "", ("10.0.0.1", 80))]
            with self.subTest(location=location), \
                 patch.object(socket, "getaddrinfo", side_effect=dns), \
                 patch.object(S, "_connection", return_value=Connection(
                     Response(status=302, headers={"Location": location}))) as connect:
                with self.assertRaises(S.UnsafeSource):
                    S.fetch_public("https://example.com")
                self.assertEqual(connect.call_count, 1)

    def test_public_redirect_and_pinned_address(self):
        connections = [Connection(Response(status=302, headers={"Location": "/v2"})),
                       Connection(Response(b"version two"))]
        with patch.object(socket, "getaddrinfo", side_effect=public_dns), \
             patch.object(S, "_connection", side_effect=connections) as connect:
            self.assertEqual(S.fetch_public("https://example.com/v1"),
                             (b"version two", "https://example.com/v2"))
            self.assertEqual(connect.call_args.args[1], "93.184.216.34")
        with patch.object(socket, "create_connection") as create:
            connection = S._PinnedHTTP("example.com", 80, "93.184.216.34", 3)
            connection.connect()
            create.assert_called_once_with(("93.184.216.34", 80), 3)

    def test_tls_uses_original_hostname_after_ip_pin(self):
        with patch.object(socket, "create_connection") as connect, \
             patch.object(S.ssl, "create_default_context") as context:
            con = S._PinnedHTTPS("example.com", 443, "93.184.216.34", 3)
            con.connect()
            connect.assert_called_once_with(("93.184.216.34", 443), 3)
            context.return_value.wrap_socket.assert_called_once_with(
                connect.return_value, server_hostname="example.com")

    def test_watchdog_closes_socket_when_body_exceeds_total_time(self):
        response = Response()
        def slow_read(n):
            time.sleep(0.04)
            return b"slow body"
        response.read1 = slow_read
        con = Connection(response)
        con.bound_socket = MagicMock()
        with patch.object(socket, "getaddrinfo", side_effect=public_dns), \
             patch.object(S, "_connection", return_value=con):
            with self.assertRaises(TimeoutError):
                S.fetch_public("https://example.com", timeout=0.01)
        con.bound_socket.shutdown.assert_called_once_with(socket.SHUT_RDWR)
        con.bound_socket.close.assert_called_once()

    def test_byte_limit_header_and_stream(self):
        for headers in [{}, {"Content-Length": "5"}]:
            with patch.object(socket, "getaddrinfo", side_effect=public_dns), \
                 patch.object(S, "_connection", return_value=Connection(Response(b"12345", headers=headers))):
                with self.assertRaises(S.UnsafeSource):
                    S.fetch_public("https://example.com", max_bytes=4)

    def test_timeout_and_redirect_limit(self):
        def slow_dns(*args, **kwargs):
            time.sleep(0.08)
            return public_dns()
        with patch.object(socket, "getaddrinfo", side_effect=slow_dns):
            with self.assertRaises(TimeoutError):
                S.fetch_public("https://example.com", timeout=0.01)
        with patch.object(socket, "getaddrinfo", side_effect=public_dns), \
             patch.object(S, "_connection", side_effect=lambda *args: Connection(
                 Response(status=302, headers={"Location": "/again"}))) as connect:
            with self.assertRaises(S.UnsafeSource):
                S.fetch_public("https://example.com")
            self.assertEqual(connect.call_count, S.MAX_REDIRECTS + 1)


class SnapshotTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name) / "documents.json"
        patcher = patch.object(instruments, "DOCS", self.path)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_snapshot_refresh_hash_history_and_failed_refresh(self):
        with patch.object(instruments, "fetch_public", side_effect=[
            (b"<p>First source</p>", "https://example.com/v1"),
            (b"<p>Changed source</p>", "https://example.com/v2"), OSError("offline")]) as fetch:
            first = instruments.document_snapshot("https://example.com")
            cached = instruments.document_snapshot("https://example.com")
            self.assertEqual(fetch.call_count, 1)
            self.assertFalse(first["cache_hit"])
            self.assertTrue(cached["cache_hit"])
            self.assertTrue(first["fetched_at"])
            self.assertEqual(first["sha256"], hashlib.sha256(b"First source").hexdigest())
            second = instruments.document_snapshot("https://example.com", refresh=True)
            self.assertNotEqual(first["sha256"], second["sha256"])
            self.assertEqual(second["final_url"], "https://example.com/v2")
            versions = json.loads(self.path.read_text())["http://example.com"]["versions"]
            self.assertEqual(versions[first["sha256"]]["text"], "First source")
            self.assertIsNone(instruments.document_snapshot("https://example.com", refresh=True))
            self.assertEqual(instruments.document("https://example.com"), "Changed source")

    def test_legacy_cache_has_no_invented_timestamp(self):
        self.path.write_text(json.dumps({"http://example.com": {"text": "legacy"}}))
        with patch.object(instruments, "fetch_public") as fetch:
            snapshot = instruments.document_snapshot("https://example.com")
            self.assertIsNone(snapshot["fetched_at"])
            self.assertEqual(instruments.document("https://example.com"), "legacy")
            fetch.assert_not_called()
        self.assertIsNone(instruments.document("https://other.example", fetch=False))
        self.assertIsNone(instruments.document("file:///tmp/test", fetch=True))


class IngestionTests(unittest.TestCase):
    def test_same_day_claim_files_are_append_only(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(ingest, "_INBOX", Path(directory)):
            first = ingest.append_markdown("one", slug="claim")
            second = ingest.append_markdown("two", slug="claim")
            self.assertNotEqual(first, second)
            self.assertEqual(first.read_text(), "one\n")
            self.assertEqual(second.read_text(), "two\n")

    def test_only_current_markdown_is_backfilled(self):
        import clear_corpus
        with tempfile.TemporaryDirectory() as directory, patch.object(ingest, "_INBOX", Path(directory)):
            ingest.append_markdown("[CLAIM] Old claim\n[URL] https://example.com/old")
            def backfill(path, **kwargs):
                claims = clear_corpus.parse_corpus(path)
                self.assertEqual(len(claims), 1)
                self.assertEqual(claims[0].text, "Current claim")
                return {"total": 1}
            with patch.object(clear_corpus, "backfill_log", side_effect=backfill):
                result = ingest.ingest_markdown("[CLAIM] Current claim\n[URL] https://example.com/current")
                self.assertEqual(result["total"], 1)
                self.assertTrue(Path(result["file"]).exists())

    def test_input_limits_and_unsafe_url(self):
        with self.assertRaises(ValueError):
            ingest.ingest_text("x" * (ingest.MAX_INPUT_BYTES + 1))
        with self.assertRaises(ValueError):
            ingest.ingest_claim("claim", "file:///tmp/test")
        with self.assertRaises(ValueError):
            ingest.ingest_markdown("[CLAIM] claim\n[URL] https://example.com\n" * 21)
        with self.assertRaises(ValueError):
            ingest.ingest_markdown("[CLAIM] claim\n[URL] http://127.0.0.1")

    def test_docker_copy_layout_can_ingest_without_repo_imports(self):
        # Materialize the declared local COPY instructions, then execute elsewhere.
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for line in (ROOT / "Dockerfile").read_text().splitlines():
                if not line.startswith("COPY "):
                    continue
                *sources, target = line.split()[1:]
                dest = root / target
                for source in sources:
                    src = ROOT / source
                    if src.is_dir():
                        shutil.copytree(src, dest, dirs_exist_ok=True,
                                        ignore=shutil.ignore_patterns("__pycache__"))
                    else:
                        output = dest / src.name if target.endswith("/") or target == "." else dest
                        output.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(src, output)
            code = """
from pathlib import Path
from clearance import ingest
assert Path('docs/inspiration/PRACTICES-CORPUS.md').is_file()
result = ingest.ingest_claim('A bounded package test claim', 'https://example.com/source', fetch=False)
assert result['verdict'] == 'UNKNOWN', result
assert Path(result['file']).exists()
"""
            result = subprocess.run([sys.executable, "-c", code], cwd=root,
                                    env={"PATH": "/usr/bin:/bin", "REFUSAL_LOG_DB": str(root / "log.db")},
                                    text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
