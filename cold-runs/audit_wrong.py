#!/usr/bin/env python3
"""Manual-audit helper: flag rows whose transcript contains the claim but product refused."""
from __future__ import annotations

import json
import re
import sys
import urllib.request
from pathlib import Path


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s.lower().strip())


def terms_in_text(claim: str, text: str) -> list[str]:
    """Return distinctive numeric/proper-noun tokens from claim found in text."""
    hits = []
    for m in re.finditer(r"\d[\d,]*|\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b", claim):
        tok = m.group(0)
        if len(tok) >= 3 and tok.lower() in text.lower():
            hits.append(tok)
    return hits


def claim_in_transcript(claim: str, text: str) -> bool:
    """Heuristic: key content words from claim appear in source transcript."""
    stop = {"the", "and", "that", "with", "from", "were", "was", "for", "are", "their", "this", "than"}
    words = [w for w in re.findall(r"[a-z0-9]+", claim.lower()) if len(w) > 3 and w not in stop]
    if not words:
        return False
    found = sum(1 for w in words if w in text)
    return found >= max(3, int(len(words) * 0.6))


def span_in_url(url: str, span: str) -> bool:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "agent-science-audit/1.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        return False
    # loose: all significant words from span appear in order-ish
    words = [w for w in re.findall(r"[a-z0-9]+", span.lower()) if len(w) > 3]
    if not words:
        return False
    return all(w in body.lower() for w in words[:8])


def audit(receipt_path: Path, script_path: Path) -> dict:
    receipt = json.loads(receipt_path.read_text())
    script = norm(script_path.read_text())
    rows = receipt["result"]["rows"]
    wrong = []
    for r in rows:
        claim = r["text"]
        label = r["label"]
        tid = r["claim_id"]
        if label == "SOURCED":
            url = r.get("citation_url") or ""
            span = r.get("quoted_terms") or ""
            if url and span and not span_in_url(url, span):
                wrong.append({
                    "id": tid,
                    "kind": "false_GREEN",
                    "claim": claim,
                    "reason": f"quoted span not found at {url}",
                    "label": label,
                    "citation_url": url,
                    "quoted_terms": span,
                })
        else:
            hits = terms_in_text(claim, script)
            nums = re.findall(r"\d[\d,]*", claim)
            num_hit = any(n.replace(",", "") in script.replace(",", "") for n in nums) if nums else False
            in_tx = claim_in_transcript(claim, script)
            if in_tx or len(hits) >= 2 or (num_hit and len(hits) >= 1):
                wrong.append({
                    "id": tid,
                    "kind": "false_REFUSE_transcript",
                    "claim": claim,
                    "reason": "source transcript contains claim terms; product refused",
                    "label": label,
                    "cause": r.get("cause"),
                    "terms_in_transcript": hits,
                })
    return {
        "receipt": str(receipt_path),
        "claims": len(rows),
        "sourced": sum(1 for r in rows if r["label"] == "SOURCED"),
        "refused": sum(1 for r in rows if r["label"] != "SOURCED"),
        "wrong": wrong,
        "wrong_count": len(wrong),
    }


if __name__ == "__main__":
    pairs = [
        ("cold-runs/receipts/script1.json", "cold-runs/scripts/script1-civil-war-historical-run.txt"),
        ("cold-runs/receipts/script2.json", "cold-runs/scripts/script2-nova-climate-science-run.txt"),
        ("cold-runs/receipts/script3.json", "cold-runs/scripts/script3-korea-adoption-policy-run.txt"),
    ]
    out = []
    for rp, sp in pairs:
        out.append(audit(Path(rp), Path(sp)))
    print(json.dumps(out, indent=2))
