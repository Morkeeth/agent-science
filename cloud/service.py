#!/usr/bin/env python3
"""Agent Science HTTP API — Cloud Run / Agent Builder hosted surface.

  GET  /health           liveness (not /healthz — GCP reserves *z paths)
  GET  /                   paste UI for judges
  POST /clear              {"script": "...", "subject": "dust-bowl"} -> gap report JSON

Stdlib only in the serving path (same pattern as agent-claims-inbox).
"""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from http.server import BaseHTTPRequestHandler, HTTPServer  # noqa: E402

import agent_science  # noqa: E402

_PAGE = """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><title>Agent Science</title>
<style>
body{font-family:system-ui;max-width:720px;margin:2rem auto;padding:0 1rem}
textarea{width:100%;min-height:160px;font-size:14px}
button{margin-top:.5rem;padding:.5rem 1rem}
pre{background:#f4f4f4;padding:1rem;overflow:auto;font-size:13px}
</style></head><body>
<h1>Agent Science</h1>
<p>Paste documentary narration. Every factual claim comes back sourced or UNSOURCED with the reason.</p>
<form method="post" action="/clear">
<label>Subject tag (for corpus compounding): <input name="subject" value="dust-bowl" size="20"></label><br><br>
<textarea name="script" placeholder="Paste script text here…" required></textarea><br>
<button type="submit">Clear</button>
</form>
</body></html>"""


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def _send(self, code: int, body: bytes, content_type: str):
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _json(self, code: int, payload):
        self._send(code, json.dumps(payload, indent=1).encode(), "application/json")

    def _read_json(self):
        n = int(self.headers.get("Content-Length") or 0)
        if not n:
            return {}
        try:
            return json.loads(self.rfile.read(n))
        except json.JSONDecodeError:
            return None

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            return self._send(200, _PAGE.encode(), "text/html; charset=utf-8")
        if self.path == "/health":
            return self._json(200, {
                "ok": True,
                "service": "agent-science",
                "gemini": bool(os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")),
                "parallel": bool(os.environ.get("PARALLEL_API_KEY")),
            })
        self._json(404, {"error": f"no route {self.path}"})

    def do_POST(self):
        if self.path == "/clear":
            ct = self.headers.get("Content-Type", "")
            if "application/json" in ct:
                body = self._read_json()
                if body is None:
                    return self._json(400, {"error": "body is not valid JSON"})
                script = (body.get("script") or "").strip()
                subject = (body.get("subject") or "default").strip()
            else:
                n = int(self.headers.get("Content-Length") or 0)
                raw = self.rfile.read(n).decode("utf-8", errors="replace")
                parts = {}
                for pair in raw.split("&"):
                    if "=" in pair:
                        k, v = pair.split("=", 1)
                        from urllib.parse import unquote_plus
                        parts[k] = unquote_plus(v.replace("+", " "))
                script = (parts.get("script") or "").strip()
                subject = (parts.get("subject") or "default").strip()
            if not script:
                return self._json(400, {"error": "field 'script' is required"})
            model = os.environ.get("GEMINI_MODEL", "gemini-3.5-flash-lite")
            try:
                out = agent_science.clear_script(script, subject=subject, model=model)
            except RuntimeError as e:
                return self._json(503, {"error": str(e)})
            code = 200 if out.get("ok") else 422
            if "application/json" not in ct and out.get("ok"):
                html = (
                    "<!DOCTYPE html><html><head><meta charset=utf-8><title>Gap report</title>"
                    "<style>body{font-family:system-ui;max-width:720px;margin:2rem auto}"
                    "pre{background:#f4f4f4;padding:1rem;white-space:pre-wrap}</style></head><body>"
                    f"<p><a href='/'>← back</a></p><pre>{out.get('markdown','')}</pre>"
                    f"<p>Parallel calls: {out.get('parallel_calls')} · "
                    f"Corpus hits: {out.get('corpus_hits')}</p></body></html>"
                )
                return self._send(200, html.encode(), "text/html; charset=utf-8")
            return self._json(code, out)
        self._json(404, {"error": f"no route {self.path}"})

    def log_message(self, fmt, *a):
        sys.stderr.write("%s %s\n" % (self.address_string(), fmt % a))


def main():
    port = int(os.environ.get("PORT", 8080))
    sys.stderr.write(f"agent-science api on :{port}\n")
    HTTPServer(("0.0.0.0", port), Handler).serve_forever()


if __name__ == "__main__":
    main()
