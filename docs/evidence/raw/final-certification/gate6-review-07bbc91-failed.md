# Independent Gate 6 review — failed candidate 07bbc91

- Review package: `07bbc9168a00cfcaa8e1ccea4b3593ff75edf2c5`
- Runtime source: `3156cf8869563b9683f5c3ff67b4104d95dc1b40`
- Image: `sha256:689c588dcdf98bcd60adbaf26b0d3c52b0a86a694eabe8c5f9736c47ad6517ee`
- Reviewer: fresh local Codex subagent with no conversation context
- Result: **failed; D5/E6 not earned**
- Candidate/evidence modifications by reviewer: none

## Passed

- Exact clean checkout and locked Python 3.14.3 installation.
- Ruff and compilation.
- Evidence/worker schema validation and evidence artifact hashes.
- MCP stdio discovery/invocation and cross-process final-slot test.
- Exact image digest, OCI revision, and running-container identity.
- Deployment verifier, live CLI, 100/100 healthy-mock benchmark, controlled partner failure/circuit/recovery, final health/readiness.
- README D4/E4 claim parity and evidence discovery.

## Failed

`pytest -q` returned 129 passed and one failed. The failing validator was `test_frozen_interface_hashes_match_contract_files`; a focused run returned 10 passed and one failed. `IFACE-POLICY-001` and `IFACE-OPS-001` did not reproduce from the clean checkout.

This failure supersedes the prior local claim that all 130 tests and interface hashes passed for this candidate. The runtime passes do not substitute for the mandatory full-suite gate.
