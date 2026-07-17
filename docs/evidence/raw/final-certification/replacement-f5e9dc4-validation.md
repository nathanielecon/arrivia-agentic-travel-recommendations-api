# Replacement candidate validation

- Source candidate: `f5e9dc4df174b1844741efbfb07cb8bdbca3e34c`
- OCI image digest: `sha256:7551188a779f278fbe270348027c8cea213a0c9688dae2bbb5d430c6f8a921d4`
- Image tag: `arrivia-recs:gate6-f5e9dc4`
- Recorded: 2026-07-16/17 America/New_York

## Clean source validation

A separate detached Git worktree at the exact candidate created a new virtual environment, installed `requirements-dev.lock`, installed the project without dependency resolution, and ran the full suite. Results: 131 passed, Ruff passed, compilation passed, and the checkout remained clean. The portable-hash regression proves CRLF and LF text inputs produce the same digest.

## Runtime validation

The image digest and OCI revision matched the source candidate. The isolated Docker stack passed health, readiness, metrics, audit/cruise exclusion, session cap, live CLI, MCP and final-slot tests, and the deployment verifier.

The controlled partner-config fault produced `upstream_error` three times and `upstream_circuit_open` on the fourth call. After fault removal and a 31-second open interval, recovery returned HTTP 200.

The replacement retains the already hashed architecture, infographic, live terminal footage, and 300-second walkthrough. No production runtime interface or SQLite schema changed from the superseded candidate; the repair affects portable certification hashing and its regression test.
