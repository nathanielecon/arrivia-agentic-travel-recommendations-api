# Judge Proof

Prompt constraint -> shipped interpretation -> proof

- MCP discover and invoke -> real stdio MCP server discovered and called by an external client -> `tests/test_mcp_stdio_smoke.py`
- Partner-specific rule enforcement -> read-only partner policy is applied to recommendations with an auditable `audit` block -> `tests/test_recommendations.py`
- Four-week first step -> v0 is intentionally one active recommendation-service replica per environment -> `docs/examples/v0-rollout.yaml`
- Same-machine session-cap parity -> REST and MCP share the same local `SESSION_BUDGET_STORE_PATH` budget for the same `session_id` -> `tests/test_mcp_stdio_smoke.py`
- Non-distributed session semantics are intentional -> separate stores do not share state, and horizontal scale is deferred -> `docs/plan/reliability.md`, `tests/test_scope_contracts.py`
- Iterative AI workflow -> checked-in YAML orchestration runs simultaneous review tracks with the Codex engine -> `docs/examples/codex-ralphy-review.yaml`

Reviewer note:

- Ralphy plus Codex is the shipped multi-agent workflow artifact in this repo.
- Cursor is compatible as an editor or MCP client, but it is not the checked-in orchestration layer for this submission.
