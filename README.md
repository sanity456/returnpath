# ReturnCustodyRoute

A reusable non-payment return route that maps items to policy windows, then enforces merchant authorization, buyer handoff, carrier acceptance, warehouse receipt, and consensus image comparison.

The repository is standalone and the contract is reusable: one deployment can hold multiple independent records for unrelated callers. It has no frontend and moves no funds.

## Native mechanism

semantic category lookup + deterministic window -> ordered four-role custody -> two-image condition-change consensus.

## Actors

merchant, buyer, carrier, warehouse, GenLayer validators.

## Source boundary

No web collection. Policies, categories, references, custody notes, and images are public caller-provided data and are not authenticated.

## Safety boundary

It creates no return right, compels no merchant, moves no money, proves no custody fact, and assigns no liability.

All inputs and results are public. Untrusted public data is delimited in prompts and cannot change the closed response schema. A malformed or non-consensus model result fails without committing the intended state transition.

## Verification

    genvm-lint check contracts/return_custody_route.py
    genvm-lint typecheck contracts/return_custody_route.py --strict
    python -m pytest tests/direct -q -p no:cacheprovider
    python tests/run_glsim.py --port 4000 --validators 5 --no-browser
    python -m pytest tests/integration -q -s -p no:cacheprovider

See ARCHITECTURE.md, SECURITY.md, SOURCE_PROVENANCE.md, AUDIT.md, SUBMISSION_CHECKLIST.md, and deployments/studionet.json.

MIT licensed.

<!-- correction-release-start -->
## Corrected release integrity

The full twelve-repository correction audit applied both steward findings to this contract. Both nondeterministic decisions now pass through the same closed-domain canonicalizers in the validator and again after consensus, so an out-of-domain leader value cannot reach custody state.

The current StudioNet release is `0xAB268c502a9D6162411Da2f0ee9C793438afdc90`. Its source bytes and full schema were read back from StudioNet and matched this repository exactly. Use `CORRECTION.md`, `REVIEW_RESPONSE.txt`, and the commit-pinned `deployments/studionet.json` for submission evidence; do not reuse the superseded address `0x3Ce0fA4B60782c7fE24073842673F156A3cc5E48`.
<!-- correction-release-end -->
