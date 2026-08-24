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
