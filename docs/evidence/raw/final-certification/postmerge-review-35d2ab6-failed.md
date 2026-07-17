---
owner: P_integration
status: failed independent review; preserved
candidate: 35d2ab60aa101d93124c31060cc9730db26fe3c6
reviewed_at: 2026-07-17
claim_ceiling: E5 for this portfolio refresh candidate; existing runtime D5/E6 remains unchanged
---

# Failed clean-context review — candidate 35d2ab6

A fresh no-write Codex reviewer checked a separate clean detached checkout of
`35d2ab60aa101d93124c31060cc9730db26fe3c6`.

The local suite passed 139 tests with Ruff and compilation clean. The evidence-index envelope,
37 historical events, content-addressed artifact archive, unchanged event history, architecture,
claims, artifacts, and current 160-second walkthrough checks passed.

The candidate failed the locked offline Linux check. In a fresh `python:3.12-slim` container with
network access disabled, the wheelhouse installed `httpx==0.28.1` into the virtual environment,
but both MCP stdio tests created `StdioServerParameters(command="python", env={...})`. The replacement
environment omitted `PATH`, so Linux resolved the MCP child to the system interpreter rather than
the locked virtual-environment interpreter. Both child processes failed with
`ModuleNotFoundError: No module named 'httpx'`; the container result was 137 passed and 2 failed.
The failure reproduced twice.

The result is retained as failed evidence. The narrow repair is for the MCP smoke harness to spawn
`sys.executable`, preserving exact interpreter identity. It does not change the production runtime,
public interfaces, dependency locks, wheelhouse, container definition, or previously certified
runtime D5/E6 result.
