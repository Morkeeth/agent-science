"""GCS-backed corpus sync — compounding that survives Cloud Run instances.

Cloud Run's /tmp dies with the container. This module keeps a local sqlite file and,
when CORPUS_GCS_URI=gs://bucket/object is set, pulls before open and pushes after
every remember. Uses the GCS JSON API + ADC (or gcloud token) — no extra pip deps.
"""
from __future__ import annotations

import json
import os
import subprocess
import urllib.error
import urllib.request
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

GCLOUD = Path.home() / "google-cloud-sdk" / "bin" / "gcloud"


def parse_gs(uri: str) -> tuple[str, str]:
    u = urlparse(uri)
    if u.scheme != "gs" or not u.netloc or not u.path:
        raise ValueError(f"CORPUS_GCS_URI must be gs://bucket/object, got {uri!r}")
    return u.netloc, u.path.lstrip("/")


def _token() -> Optional[str]:
    # Prefer the metadata server on Cloud Run / GCE.
    try:
        req = urllib.request.Request(
            "http://metadata.google.internal/computeMetadata/v1/"
            "instance/service-accounts/default/token",
            headers={"Metadata-Flavor": "Google"},
        )
        with urllib.request.urlopen(req, timeout=3) as r:
            return json.load(r).get("access_token")
    except Exception:
        pass
    if GCLOUD.exists():
        try:
            p = subprocess.run(
                [str(GCLOUD), "auth", "application-default", "print-access-token"],
                capture_output=True, text=True, timeout=30)
            return p.stdout.strip() or None
        except Exception:
            return None
    return None


def pull(uri: str, dest: Path) -> bool:
    """Download gs object to dest. True if an object existed."""
    bucket, obj = parse_gs(uri)
    token = _token()
    if not token:
        return False
    url = (f"https://storage.googleapis.com/storage/v1/b/{bucket}/o/"
           f"{urllib.request.quote(obj, safe='')}?alt=media")
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(r.read())
        return True
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return False
        raise


def push(uri: str, src: Path) -> None:
    """Upload dest file to gs object (overwrite)."""
    if not src.exists():
        return
    bucket, obj = parse_gs(uri)
    token = _token()
    if not token:
        raise RuntimeError("no ADC/metadata token — cannot push corpus to GCS")
    url = (f"https://storage.googleapis.com/upload/storage/v1/b/{bucket}/o"
           f"?uploadType=media&name={urllib.request.quote(obj, safe='')}")
    data = src.read_bytes()
    req = urllib.request.Request(
        url, data=data, method="POST",
        headers={"Authorization": f"Bearer {token}",
                 "Content-Type": "application/octet-stream",
                 "Content-Length": str(len(data))})
    with urllib.request.urlopen(req, timeout=120) as r:
        r.read()


def gcs_uri() -> Optional[str]:
    return os.environ.get("CORPUS_GCS_URI") or None
