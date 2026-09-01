# Architecture

Project: ReturnCustodyRoute

Reusable primitive: semantic category lookup + deterministic window -> ordered four-role custody -> two-image condition-change consensus.

The contract separates caller-attested public inputs, validator-agreed semantic fields, deterministic state transitions, and role-bound final actions. It stores canonical JSON strings in GenVM maps, validates every identifier and bound before consensus, and keeps source references explicitly unverified.

The mechanism is not a renamed assessment record. Its state transitions, role topology, storage layout, deterministic algorithm, and public ABI are specific to this project.

<!-- correction-release-start -->
## Consensus and storage safety boundary

Both nondeterministic decisions now pass through the same closed-domain canonicalizers in the validator and again after consensus, so an out-of-domain leader value cannot reach custody state.

The on-chain state transition consumes only the canonical value returned by the post-consensus binding boundary. This contract does not expose a shared permissionless fixed-cap operational registry.
<!-- correction-release-end -->
