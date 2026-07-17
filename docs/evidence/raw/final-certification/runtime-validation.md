# Final candidate runtime validation

- Source candidate: `3156cf8869563b9683f5c3ff67b4104d95dc1b40`
- OCI image digest: `sha256:689c588dcdf98bcd60adbaf26b0d3c52b0a86a694eabe8c5f9736c47ad6517ee`
- Environment: Windows host, Docker Desktop Linux containers, isolated network `arrivia-cert-net`, API `127.0.0.1:18080`
- Recorded: 2026-07-16/17 America/New_York

## Static and contract suite

- Fresh locked Windows virtual environment: passed.
- `pytest -q`: 130 passed.
- Ruff: passed.
- Python compilation: passed.
- JSON Schemas, evidence links, partition ownership, interface hashes, and artifact hashes: passed.
- Linux image dependency audit with pip-audit 2.10.1: no known vulnerabilities.

## Runtime journeys

- Deployment verifier: `/health`, `/ready`, `/metrics`, audit/cruise exclusion, and session cap all passed.
- Live CLI: HTTP 200; `partner_id=p1`; three non-cruise recommendations; audit source `partner-config-service`; cap and exclusion rules present.
- MCP stdio discovery and invocation: passed in the candidate test suite with an isolated SQLite path.
- Cross-process final-slot test: passed in the candidate test suite; independent contenders share one SQLite file and preserve the cap invariant.

## Controlled partner failure and recovery

With the temporary partner-config WireMock fault enabled, four unique-session REST calls returned:

1. `502 {"detail":"upstream_error"}`
2. `502 {"detail":"upstream_error"}`
3. `502 {"detail":"upstream_error"}`
4. `502 {"detail":"upstream_circuit_open"}`

After disabling the fault and waiting 31 seconds, the half-open probe returned HTTP 200 with policy source `partner-config-service`.

## Telemetry and strict policy

- Completion logs were newline-delimited JSON and contained timestamp, level, event, request/surface identifiers, hashed member/session identifiers, partner, outcome, duration, and the structured audit block.
- Circuit-open logs carried `error_code=upstream_circuit_open` and did not contain upstream bodies or member profiles.
- `/metrics` exposed the frozen request, upstream, rule, budget, and circuit series.
- Strict partner-policy schema and tests reject unknown properties, alias conflicts, and partner identity mismatches.
