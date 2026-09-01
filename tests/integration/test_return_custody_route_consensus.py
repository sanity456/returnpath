import hashlib
import json
from pathlib import Path

from gltest import get_contract_factory, get_validator_factory
from gltest.accounts import create_accounts
from gltest.assertions import tx_execution_succeeded
from gltest.types import TransactionStatus
from gltest.utils import extract_contract_address


def _ok(receipt):
    assert tx_execution_succeeded(receipt), json.dumps(receipt, default=str)


def _context(fragment, response):
    validators = get_validator_factory().batch_create_mock_validators(
        5,
        mock_llm_response={"nondet_exec_prompt": {fragment: json.dumps(response)}},
    )
    return {
        "validators": [validator.to_dict() for validator in validators],
        "genvm_datetime": "2026-08-25T12:00:00Z",
    }


def _deploy(contract_file, owner_account):
    factory = get_contract_factory(
        contract_file_path=Path(__file__).resolve().parents[2] / "contracts" / contract_file
    )
    receipt = factory.deploy_contract_tx(
        args=[],
        account=owner_account,
        wait_transaction_status=TransactionStatus.FINALIZED,
    )
    _ok(receipt)
    return factory, extract_contract_address(receipt)


def _send(method, args, context=None):
    if context is None:
        receipt = method(args=args).transact(
            wait_transaction_status=TransactionStatus.FINALIZED
        )
    else:
        receipt = method(args=args).transact(
            transaction_context=context,
            wait_transaction_status=TransactionStatus.FINALIZED,
        )
    _ok(receipt)
    return receipt


def test_five_validator_eligibility_and_custody_flow():
    merchant_account, buyer_account, carrier_account, warehouse_account = create_accounts(4)
    factory, address = _deploy("return_custody_route.py", merchant_account)
    merchant = factory.build_contract(address, account=merchant_account)
    buyer = factory.build_contract(address, account=buyer_account)
    carrier = factory.build_contract(address, account=carrier_account)
    warehouse = factory.build_contract(address, account=warehouse_account)
    policy_id = f"{str(merchant_account.address).lower()}:STANDARD"
    return_id = f"{str(buyer_account.address).lower()}:R1"
    initial = b"public-initial-return-image:" + b"a" * 64
    final = b"public-final-return-image:" + b"b" * 64
    categories = json.dumps({"categories": [{"id": "HOUSEHOLD", "description": "Small nonperishable household goods in the listed program.", "window_minutes": 100}]})
    _send(merchant.publish_policy, ["STANDARD", warehouse_account.address, categories, "Frozen informational return workflow for the listed public category and window.", "merchant-policy-snapshot"])
    _send(buyer.open_return, ["R1", policy_id, carrier_account.address, "A small nonperishable household storage item from the listed program.", 0, 50, initial])
    _send(buyer.classify_eligibility, [return_id], _context("Map one public item description", {"category_id": "HOUSEHOLD"}))
    _send(merchant.merchant_authorize, [return_id, True, "Merchant authorizes the documented custody route."])
    _send(buyer.buyer_handoff, [return_id, "public-carrier-handoff-1"])
    _send(carrier.carrier_checkpoint, [return_id, True, "Carrier accepts the public handoff record."])
    _send(
        warehouse.warehouse_receive,
        [return_id, initial, final, "Warehouse records public receipt of the item."],
        _context("Compare two public item images", {"condition_change": "SAME"}),
    )
    _send(merchant.merchant_close, [return_id, "COMPLETE", "Merchant closes the non-payment public return record."])
    assert merchant.matches_custody(args=[return_id, "CLOSED", "SAME"]).call() is True
