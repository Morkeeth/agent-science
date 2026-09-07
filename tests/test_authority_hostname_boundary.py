"""Adversarial hostname controls bind to the actual public classifier."""
import pytest
from clearance.independence import classify, note

@pytest.mark.parametrize("url", [
 "https://example.gov.attacker.invalid/report.pdf",
 "https://agency.government.example.com/report",
 "https://notwipo.int/report", "https://evilw3.org/report",
 "https://www.un.org@attacker.invalid/report",
 "https://example.org/?source=example.gov", "https://example.org/example.gov",
 "javascript://example.gov/a", "file://example.gov/a", "example.gov/report",
 "https://[invalid/", "https://example.gov:999999/report",
])
def test_lookalikes_never_primary(url):
 assert classify(url)[0] != "primary"

@pytest.mark.parametrize("url", [
 "https://example.gov/report", "https://www.example.gov/report",
 "https://EXAMPLE.GOV.:443/report", "https://www.wipo.int/report",
 "https://www.un.org/report", "https://www.w3.org/report",
])
def test_real_domain_boundaries_remain_recognised(url):
 assert classify(url)[0] == "primary"
 assert "hostname hint only" in note(url)


def test_derived_hints_match_hosts_not_unrelated_paths():
 assert classify('https://example.gov/reports/wikipedia.org-analysis')[0] == 'primary'
 assert classify('https://wikipedia.org.attacker.invalid/report')[0] == 'unclassified'
 assert classify('https://en.wikipedia.org/wiki/Test')[0] == 'derived'


def test_spoofed_primary_cannot_satisfy_independence_alone():
 from clearance.independence import assess
 assert assess(['https://example.gov.attacker.invalid/report'])['has_independent_support'] is False


def test_bare_registry_is_not_a_publisher():
    assert classify("https://gov/x")[0] == "unclassified"
