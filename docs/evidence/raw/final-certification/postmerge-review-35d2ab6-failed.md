---
owner: P_integration
status: superseded preliminary review-command failure; candidate later passed exact handoff
candidate: 35d2ab60aa101d93124c31060cc9730db26fe3c6
reviewed_at: 2026-07-17
claim_ceiling: E5 for this portfolio refresh candidate; existing runtime D5/E6 remains unchanged
---

# Superseded preliminary run — candidate 35d2ab6

A fresh no-write Codex reviewer checked a separate clean detached checkout of
`35d2ab60aa101d93124c31060cc9730db26fe3c6`.

The local suite passed 139 tests with Ruff and compilation clean. The evidence-index envelope,
37 historical events, content-addressed artifact archive, unchanged event history, architecture,
claims, artifacts, and current 160-second walkthrough checks passed.

An initial locked offline Linux command failed. In a fresh `python:3.12-slim` container with
network access disabled, the wheelhouse installed `httpx==0.28.1` into the virtual environment,
but both MCP stdio tests created `StdioServerParameters(command="python", env={...})`. The replacement
environment omitted `PATH`, so Linux resolved the MCP child to the system interpreter rather than
the locked virtual-environment interpreter. Both child processes failed with
`ModuleNotFoundError: No module named 'httpx'`; the container result was 137 passed and 2 failed.
The failure reproduced twice.

## Reviewer correction

Before issuing a verdict, the reviewer found that the failing command directly invoked the virtual
environment executable without first activating that environment. The parent `PATH` therefore
still selected system Python for the child. The repository's exact documented handoff—run the
installer, `source` the virtual environment, then run pytest—passed 139/139 with network disabled.
All remaining evidence and media checks passed, so candidate `35d2ab6` received a final **PASS**.

The preliminary command failure remains visible here and is not evidence of a candidate defect.
The later `sys.executable` change is defense-in-depth for test-harness interpreter identity; it does
not change the production runtime, public interfaces, dependency locks, wheelhouse, container
definition, or previously certified runtime D5/E6 result.
