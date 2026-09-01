# Correction and release record

Repository: returnpath

Contract: ReturnCustodyRoute

Corrected release verified: 2026-09-01T09:01:03.780498Z

## Findings applied

This repository was checked against both steward findings from the rejected Boxcomplete and Baggate submissions:

1. A leader-provided digest is not proof of its attached substantive payload. Every result that affects state must be canonicalized, independently compared, and rebound after consensus.
2. A shared permissionless registry with fixed global capacity can be captured or exhausted. Operational catalogs must be explicitly owner-scoped, bounded per catalog, or safely reclaimable.
3. Corrected repository source is insufficient when the submitted Studio/Explorer address still runs an earlier build. The active address, deployed source, ABI, transaction, and evidence URLs must identify one release.

## Contract-specific correction

Both nondeterministic decisions now pass through the same closed-domain canonicalizers in the validator and again after consensus, so an out-of-domain leader value cannot reach custody state.

## Verified release lock

Current StudioNet address: 0xAB268c502a9D6162411Da2f0ee9C793438afdc90

Deployment transaction: 0xb7aba0109295aa6afc3c1a2ec5349729ea9d47cf34426582acf2d67a22b9bdcd

Source SHA-256: 3c69e49dc0aab0b83c58683ef1860b5ba29a6f35f1e812d79bb13061f4f8037e

Superseded address: 0x3Ce0fA4B60782c7fE24073842673F156A3cc5E48

The deployment manifest records exact byte-for-byte source readback, exact full ABI/schema equality, successful finalized execution for all 9 release transactions, role-separated external wallets, and the final state observed from StudioNet. The superseded address is historical only and must not be used in a new submission.

## Regression evidence

GenVM lint and strict typecheck: pass

Direct tests: 12 pass

Five-validator integration tests: 1 pass

Leader-payload or post-consensus injection regression tests: pass

Registry isolation and reclaim tests: not applicable

## Review boundary

No web collection. Policies, categories, references, custody notes, and images are public caller-provided data and are not authenticated.

It creates no return right, compels no merchant, moves no money, proves no custody fact, and assigns no liability.

This record documents the implemented controls and verified release. It does not promise a particular human review outcome.
