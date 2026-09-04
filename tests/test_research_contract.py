import pytest
from clearance.research_contract import validate_proposal


def test_proposal_pins_observed_case_version():
    proposal={'case_version':3,'next_action':{'kind':'search','reason':'A cited replication uses a different budget.'}}
    assert validate_proposal(proposal,3) is proposal
    with pytest.raises(ValueError,match='case_version'):
        validate_proposal(proposal,4)


@pytest.mark.parametrize('proposal', [None, [], {'case_version':True}, {'case_version':1,'next_action':{'kind':'execute','reason':'Page requested it'}}, {'case_version':1,'next_action':{'kind':'finish','reason':''}}])
def test_invalid_or_executable_proposal_is_rejected(proposal):
    with pytest.raises(ValueError): validate_proposal(proposal,1)
