"""Keep provider fixtures out of the user's local research history."""
import pytest


@pytest.fixture(autouse=True)
def private_search_store(tmp_path,monkeypatch):
    monkeypatch.setenv('AGENT_SCIENCE_SEARCH_DIR',str(tmp_path/'private-search'))
