"""Bounded public HTTP source fetches, with DNS pinned for every redirect hop.

Only the validated addresses are passed to the socket; TLS still authenticates the
original hostname. Environment proxy settings cannot bypass this boundary.
"""
from __future__ import annotations

import http.client
import ipaddress
import queue
import socket
import ssl
import threading
import time
from urllib.parse import urljoin, urlsplit

MAX_BYTES = 2 * 1024 * 1024
MAX_SECONDS = 30
MAX_REDIRECTS = 5
_DNS_SLOTS = threading.BoundedSemaphore(4)


class UnsafeSource(ValueError):
    pass


def validate_url(url: str):
    """Validate URL syntax and literal addresses, without a network operation."""
    if not isinstance(url, str) or not url or len(url) > 8192:
        raise UnsafeSource("source URL is missing or too long")
    if any(ord(c) <= 32 or ord(c) == 127 for c in url) or "\\" in url:
        raise UnsafeSource("source URL contains unsafe characters")
    try:
        parts = urlsplit(url)
        port = parts.port
        host = parts.hostname
    except ValueError as exc:
        raise UnsafeSource("invalid source URL") from exc
    if parts.scheme not in ("http", "https") or not host:
        raise UnsafeSource("source must use public HTTP or HTTPS")
    if parts.username is not None or parts.password is not None:
        raise UnsafeSource("source URL must not contain credentials")
    if port is not None and not 1 <= port <= 65535:
        raise UnsafeSource("invalid source port")
    if "%" in host or host.rstrip(".").lower() == "localhost":
        raise UnsafeSource("source host is not public")
    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        pass
    else:
        _public_address(str(address))
    return parts


def _public_address(value: str) -> str:
    address = ipaddress.ip_address(value)
    if (not address.is_global or address.is_multicast or address.is_reserved
            or getattr(address, "ipv4_mapped", None) is not None
            or getattr(address, "sixtofour", None) is not None
            or getattr(address, "teredo", None) is not None):
        raise UnsafeSource("source address is not public")
    return str(address)


def _remaining(deadline: float) -> float:
    remaining = deadline - time.monotonic()
    if remaining <= 0:
        raise TimeoutError("source fetch time limit exceeded")
    return remaining


def _resolve(host: str, port: int, deadline: float) -> list[str]:
    # DNS has no socket timeout. Bound caller waiting and outstanding resolver jobs.
    if not _DNS_SLOTS.acquire(timeout=_remaining(deadline)):
        raise TimeoutError("source resolver busy")
    result = queue.Queue(maxsize=1)

    def resolve():
        try:
            result.put((True, socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)))
        except Exception as exc:
            result.put((False, exc))
        finally:
            _DNS_SLOTS.release()

    threading.Thread(target=resolve, daemon=True).start()
    try:
        ok, value = result.get(timeout=_remaining(deadline))
    except queue.Empty as exc:
        raise TimeoutError("source DNS time limit exceeded") from exc
    if not ok:
        raise value
    addresses = list(dict.fromkeys(_public_address(row[4][0]) for row in value))
    if not addresses:
        raise UnsafeSource("source host has no public address")
    return addresses


class _PinnedHTTP(http.client.HTTPConnection):
    def __init__(self, host, port, address, timeout):
        super().__init__(host, port, timeout=timeout)
        self.address = address
        self.deadline = time.monotonic() + timeout

    def connect(self):
        self.sock = socket.create_connection((self.address, self.port), self.timeout)
        self.bound_socket = self.sock
        try:
            self.sock.settimeout(_remaining(self.deadline))
        except Exception:
            self.sock.close()
            raise


class _PinnedHTTPS(_PinnedHTTP):
    def connect(self):
        super().connect()
        try:
            self.sock = ssl.create_default_context().wrap_socket(
                self.sock, server_hostname=self.host)
            self.bound_socket = self.sock
        except Exception:
            self.sock.close()
            raise


def _connection(parts, address, timeout):
    cls = _PinnedHTTPS if parts.scheme == "https" else _PinnedHTTP
    return cls(parts.hostname, parts.port or (443 if parts.scheme == "https" else 80),
               address, timeout)


def fetch_public(url: str, *, timeout: float = MAX_SECONDS,
                 max_bytes: int = MAX_BYTES, user_agent: str = "AgentScience/1.0") -> tuple[bytes, str]:
    """Return (body bytes, final URL); failures never return partial documents."""
    timeout = min(float(timeout), MAX_SECONDS)
    max_bytes = min(int(max_bytes), MAX_BYTES)
    if timeout <= 0 or max_bytes <= 0:
        raise ValueError("fetch limits must be positive")
    deadline = time.monotonic() + timeout
    current = url
    for hop in range(MAX_REDIRECTS + 1):
        parts = validate_url(current)
        port = parts.port or (443 if parts.scheme == "https" else 80)
        addresses = _resolve(parts.hostname, port, deadline)
        con = _connection(parts, addresses[0], _remaining(deadline))
        response = None
        # The watchdog bounds headers and slow-drip reads as well as connect time.
        def abort(connection=con):
            sock = getattr(connection, "bound_socket", None)
            if sock is not None:
                try:
                    sock.shutdown(socket.SHUT_RDWR)
                except OSError:
                    pass
                sock.close()

        timer = threading.Timer(_remaining(deadline), abort)
        timer.daemon = True
        timer.start()
        try:
            path = parts.path or "/"
            if parts.query:
                path += "?" + parts.query
            con.request("GET", path, headers={"User-Agent": user_agent,
                        "Accept-Encoding": "identity", "Connection": "close"})
            response = con.getresponse()
            if response.status in (301, 302, 303, 307, 308):
                location = response.getheader("Location")
                if not location or hop == MAX_REDIRECTS:
                    raise UnsafeSource("source redirect limit or missing destination")
                current = urljoin(current, location)
                continue
            if not 200 <= response.status < 300:
                raise OSError(f"source HTTP status {response.status}")
            if response.getheader("Content-Encoding", "identity").lower() != "identity":
                raise UnsafeSource("compressed source response is not supported")
            length = response.getheader("Content-Length")
            if length and int(length) > max_bytes:
                raise UnsafeSource("source exceeds byte limit")
            body = bytearray()
            while True:
                _remaining(deadline)
                chunk = response.read1(min(65536, max_bytes + 1 - len(body)))
                if not chunk:
                    break
                body.extend(chunk)
                if len(body) > max_bytes:
                    raise UnsafeSource("source exceeds byte limit")
            _remaining(deadline)
            return bytes(body), current
        finally:
            timer.cancel()
            if response is not None:
                response.close()
            con.close()
    raise UnsafeSource("source redirect limit exceeded")
