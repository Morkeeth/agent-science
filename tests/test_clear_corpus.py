"""The research corpus parses into claims Agent Science can verify — both the [CLAIM]/
[URL] format and the one-line 'claim ... [URL: ...]' bullet format."""
import sys, os, tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import clear_corpus as cc


def _corpus(text: str) -> str:
    d = tempfile.mkdtemp()
    open(os.path.join(d, "r.md"), "w").write(text)
    return d


def test_parses_claim_url_block_format():
    d = _corpus("[CLAIM] The sky is blue on a clear day.\n[URL] https://example.com/sky\n")
    cs = cc.parse_corpus(d)
    assert len(cs) == 1
    assert "sky is blue" in cs[0].text and cs[0].url == "https://example.com/sky"


def test_parses_one_line_bullet_format():
    d = _corpus("- Zenity raised $125M for agent governance — https://example.com/zenity\n"
                "- ASR was 12.7% average [URL: https://arxiv.org/abs/2507.20526]\n")
    cs = cc.parse_corpus(d)
    urls = {c.url for c in cs}
    assert "https://example.com/zenity" in urls
    assert "https://arxiv.org/abs/2507.20526" in urls
    # the bracket tag is stripped from the claim text
    assert all("[URL:" not in c.text for c in cs)


def test_must_contain_prefers_a_quoted_phrase():
    assert cc._must_contain('The paper says "beyond 138 is uncertain" clearly') == "beyond 138 is uncertain"
    # else the first clause, capped
    mc = cc._must_contain("Zenity raised $125M — the category is funded")
    assert mc.startswith("Zenity raised") and "—" not in mc


def test_a_bare_url_line_with_no_claim_is_skipped():
    d = _corpus("https://example.com/orphan\nsome prose with no url here\n")
    assert cc.parse_corpus(d) == []


if __name__ == "__main__":
    fns = [v for k,v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    bad=0
    for fn in fns:
        try: fn(); print("PASS", fn.__name__)
        except AssertionError as e: bad+=1; print("FAIL", fn.__name__, e)
    print(f"\n{len(fns)-bad}/{len(fns)} passed"); sys.exit(1 if bad else 0)


def test_verify_corpus_buckets_fetch_weather_apart_from_real_unsourced():
    """The dogfood's own gate: a dead URL (source_never_fetched) is UNKNOWN weather,
    never UNSOURCED. Only 'read it, does not state it' counts as UNSOURCED — the one
    cause a CI red-build can stand on without flapping. Pins the mis-bucket the full
    corpus run surfaced (9 dead URLs had been folded into 'refused')."""
    import clearance.facts as facts
    from clearance import verdict as V

    class FakeV:
        def __init__(self, vd, cause): self.verdict, self.cause = vd, cause

    # three claims, one per outcome, keyed by URL so the fake is deterministic
    plan = {
        "https://ok.example/green":   FakeV(V.GREEN, ""),
        "https://dead.example/403":   FakeV(V.UNKNOWN, V.SOURCE_UNREAD),   # fetch weather
        "https://silent.example/read": FakeV(V.UNKNOWN, V.SOURCE_SILENT),  # real UNSOURCED
    }
    d = _corpus(
        "[CLAIM] A sourced claim about the world.\n[URL] https://ok.example/green\n"
        "[CLAIM] A claim whose source is dead.\n[URL] https://dead.example/403\n"
        "[CLAIM] A claim its source does not state.\n[URL] https://silent.example/read\n"
    )
    orig = facts.judge_claim
    facts.judge_claim = lambda claim, **kw: plan[claim.source_url]
    try:
        res = cc.verify_corpus(d, fetch=False)
    finally:
        facts.judge_claim = orig

    assert res["sourced"] == 1, res
    assert res["unknown"] == 1, res      # the dead URL, NOT counted against the corpus
    assert res["refused"] == 1, res      # only the genuinely unsourced claim
    verdicts = {r["verdict"] for r in res["rows"]}
    assert verdicts == {"SOURCED", "UNKNOWN", "UNSOURCED"}, res["rows"]
