"""Direct tests for eligibility and ordered return custody."""

import json


INITIAL = b"public-initial-return-image:" + b"a" * 64
FINAL = b"public-final-return-image:" + b"b" * 64
CATEGORIES = json.dumps({"categories": [{"id": "HOUSEHOLD", "description": "Small nonperishable household goods in the listed program.", "window_minutes": 100}]})


def _policy(contract, vm, merchant, warehouse):
    vm.sender = merchant
    return contract.publish_policy("STANDARD", warehouse, CATEGORIES, "Frozen informational return workflow for the listed public category and window.", "merchant-policy-snapshot")


def _open(contract, vm, buyer, policy_id, carrier, request=50):
    vm.sender = buyer
    return contract.open_return("R1", policy_id, carrier, "A small nonperishable household storage item from the listed program.", 0, request, INITIAL)


def _classify(contract, vm, buyer, return_id, category="HOUSEHOLD"):
    vm.sender = buyer
    vm.mock_llm(r".*Map one public item description.*", json.dumps({"category_id": category}))
    return contract.classify_eligibility(return_id)


def test_policy_is_caller_snapshot(contract, direct_vm, direct_alice, direct_charlie):
    policy_id = _policy(contract, direct_vm, direct_alice, direct_charlie)
    assert contract.get_policy(policy_id)["source_verified"] is False


def test_within_window_is_eligible(contract, direct_vm, direct_alice, direct_bob, direct_charlie):
    policy_id = _policy(contract, direct_vm, direct_alice, direct_charlie)
    return_id = _open(contract, direct_vm, direct_bob, policy_id, direct_charlie)
    assert _classify(contract, direct_vm, direct_bob, return_id) == "ELIGIBLE"


def test_expired_window_is_code_derived(contract, direct_vm, direct_alice, direct_bob, direct_charlie):
    policy_id = _policy(contract, direct_vm, direct_alice, direct_charlie)
    return_id = _open(contract, direct_vm, direct_bob, policy_id, direct_alice, 101)
    assert _classify(contract, direct_vm, direct_bob, return_id) == "WINDOW_EXPIRED"


def test_unknown_category_routes_manual_review(contract, direct_vm, direct_alice, direct_bob, direct_charlie):
    policy_id = _policy(contract, direct_vm, direct_alice, direct_charlie)
    return_id = _open(contract, direct_vm, direct_bob, policy_id, direct_alice)
    assert _classify(contract, direct_vm, direct_bob, return_id, "UNKNOWN") == "MANUAL_REVIEW"


def test_only_merchant_authorizes(contract, direct_vm, direct_alice, direct_bob, direct_charlie):
    policy_id = _policy(contract, direct_vm, direct_alice, direct_charlie)
    return_id = _open(contract, direct_vm, direct_bob, policy_id, direct_alice)
    _classify(contract, direct_vm, direct_bob, return_id)
    direct_vm.sender = direct_bob
    with direct_vm.expect_revert("only_merchant"):
        contract.merchant_authorize(return_id, True, "Wrong wallet cannot authorize this public return.")


def test_full_custody_and_condition_compare(contract, direct_vm, direct_alice, direct_bob, direct_charlie):
    policy_id = _policy(contract, direct_vm, direct_alice, direct_charlie)
    return_id = _open(contract, direct_vm, direct_bob, policy_id, direct_charlie)
    _classify(contract, direct_vm, direct_bob, return_id)
    direct_vm.sender = direct_alice
    contract.merchant_authorize(return_id, True, "Merchant authorizes the documented custody route.")
    direct_vm.sender = direct_bob
    contract.buyer_handoff(return_id, "public-carrier-handoff-1")
    direct_vm.sender = direct_charlie
    contract.carrier_checkpoint(return_id, True, "Carrier accepts the public handoff record.")
    direct_vm.sender = direct_charlie
    direct_vm.mock_llm(r".*Compare two public item images.*", json.dumps({"condition_change": "SAME"}))
    assert contract.warehouse_receive(return_id, INITIAL, FINAL, "Warehouse records public receipt of the item.") == "SAME"
    direct_vm.sender = direct_alice
    contract.merchant_close(return_id, "COMPLETE", "Merchant closes the non-payment public return record.")
    assert contract.get_return(return_id)["state"] == "CLOSED"


def test_wrong_initial_image_blocks_receipt(contract, direct_vm, direct_alice, direct_bob, direct_charlie):
    policy_id = _policy(contract, direct_vm, direct_alice, direct_charlie)
    return_id = _open(contract, direct_vm, direct_bob, policy_id, direct_charlie)
    _classify(contract, direct_vm, direct_bob, return_id)
    direct_vm.sender = direct_alice
    contract.merchant_authorize(return_id, True, "Merchant authorizes the documented custody route.")
    direct_vm.sender = direct_bob
    contract.buyer_handoff(return_id, "public-carrier-handoff-1")
    direct_vm.sender = direct_charlie
    contract.carrier_checkpoint(return_id, True, "Carrier accepts the public handoff record.")
    direct_vm.sender = direct_charlie
    with direct_vm.expect_revert("initial_image_fingerprint_mismatch"):
        contract.warehouse_receive(return_id, INITIAL + b"x", FINAL, "Warehouse records public receipt of the item.")


def test_bad_category_output_keeps_open(contract, direct_vm, direct_alice, direct_bob, direct_charlie):
    policy_id = _policy(contract, direct_vm, direct_alice, direct_charlie)
    return_id = _open(contract, direct_vm, direct_bob, policy_id, direct_alice)
    with direct_vm.expect_revert("[LLM_ERROR] invalid_category_id"):
        _classify(contract, direct_vm, direct_bob, return_id, "NOPE")
    assert contract.get_return(return_id)["state"] == "OPEN"
