"""Study identity controls — mirrors collapse; titles never merge."""
from clearance import study


def test_five_arxiv_mirrors_are_one_study():
    urls = [
        'https://arxiv.org/abs/2301.12345',
        'https://arxiv.org/pdf/2301.12345.pdf',
        'https://arxiv.org/html/2301.12345',
        'https://ar5iv.labs.arxiv.org/html/2301.12345',
        'http://arxiv.org/abs/2301.12345v2',
    ]
    groups = study.group_documents(urls)
    assert len(groups) == 1
    assert groups[0]['identity'] == 'arxiv'
    assert groups[0]['id'] == '2301.12345'
    assert set(groups[0]['urls']) == set(urls)


def test_doi_prefers_over_url_and_title_never_merges():
    a = study.study_key('https://doi.org/10.1145/1234567.7654321')
    b = study.study_key('https://dl.acm.org/doi/10.1145/1234567.7654321')
    # ACM path without doi.org host still extracts DOI from path
    assert a == b == ('doi', '10.1145/1234567.7654321')
    # Different papers with similar titles are not mergeable by this module (no title input).
    assert study.study_key('https://example.org/paper-about-memory') != study.study_key(
        'https://example.org/another-paper-about-memory'
    )


def test_uncertain_link_stays_candidate():
    groups = study.group_documents(['not-a-url', 'https://example.org/x'])
    assert groups[0]['identity'] == 'candidate'
    assert groups[1]['identity'] == 'url'
