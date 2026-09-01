"""Strict validator and post-consensus domain binding regressions."""

import json

from tests.direct.test_return_custody_route import FINAL, INITIAL, _classify, _open, _policy


def _open_and_classify(contract, vm, merchant, buyer, warehouse, carrier=None):
    policy_id = _policy(contract, vm, merchant, warehouse)
    return_id = _open(contract, vm, buyer, policy_id, carrier or merchant)
    _classify(contract, vm, buyer, return_id)
    return return_id


def test_category_validator_rejects_out_of_catalog_value(contract, direct_vm, direct_alice, direct_bob, direct_charlie):
    _open_and_classify(contract, direct_vm, direct_alice, direct_bob, direct_charlie)
    assert direct_vm.run_validator(leader_result={"category_id": "NOPE"}) is False


def test_category_validator_accepts_honest_value(contract, direct_vm, direct_alice, direct_bob, direct_charlie):
    _open_and_classify(contract, direct_vm, direct_alice, direct_bob, direct_charlie)
    assert direct_vm.run_validator() is True


def test_post_consensus_invalid_category_preserves_open_return(contract, direct_vm, direct_alice, direct_bob, direct_charlie, monkeypatch):
    from genlayer import gl

    policy_id = _policy(contract, direct_vm, direct_alice, direct_charlie)
    return_id = _open(contract, direct_vm, direct_bob, policy_id, direct_alice)
    before = contract.get_return(return_id)
    direct_vm.sender = direct_bob
    monkeypatch.setattr(gl.vm, "run_nondet_unsafe", lambda *args: {"category_id": "NOPE"})
    with direct_vm.expect_revert("invalid_category_id"):
        contract.classify_eligibility(return_id)
    assert contract.get_return(return_id) == before


def test_condition_validator_rejects_out_of_domain_value(contract, direct_vm, direct_alice, direct_bob, direct_charlie):
    return_id = _open_and_classify(contract, direct_vm, direct_alice, direct_bob, direct_charlie, direct_charlie)
    direct_vm.sender = direct_alice
    contract.merchant_authorize(return_id, True, "Merchant authorizes the documented custody route.")
    direct_vm.sender = direct_bob
    contract.buyer_handoff(return_id, "public-carrier-handoff-1")
    direct_vm.sender = direct_charlie
    contract.carrier_checkpoint(return_id, True, "Carrier accepts the public handoff record.")
    direct_vm.mock_llm(r".*Compare two public item images.*", json.dumps({"condition_change": "SAME"}))
    contract.warehouse_receive(return_id, INITIAL, FINAL, "Warehouse records public receipt of the item.")
    assert direct_vm.run_validator(leader_result={"condition_change": "DAMAGED"}) is False
