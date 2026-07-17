---
owner: P_integration
status: failed independent review; preserved
candidate: 7e58f3a66462779e03a547f10df72fb8ffea4d3b
reviewed_at: 2026-07-17
claim_ceiling: E5 for this portfolio refresh candidate; existing runtime D5/E6 remains unchanged
---

# Failed clean-context review — candidate 7e58f3a

A fresh no-write Codex reviewer checked a separate clean detached checkout of
`7e58f3a66462779e03a547f10df72fb8ffea4d3b`.

Passed checks included exact checkout identity, 137 tests, Ruff, compilation, all five schemas,
the full evidence-index envelope and 37 embedded events, artifact hashes, unchanged runtime and
interface files, unchanged certified container identity, unchanged Quiet Systems source, and the
six-page architecture authority.

The candidate failed certification because its `append_only: true` ledger had edited historical
event records to follow mutable presentation paths instead of retaining their original bytes. It
also had no planned/current event for the refresh while the refresh report already said binding and
fresh review were recorded, and the final attestation incorrectly called the superseded Quiet
Systems cut the current portfolio authority.

The result is retained as a failed review. It does not reduce or replace the previously earned
runtime `D5 Reimplementable / E6 Independently reproduced` result.
