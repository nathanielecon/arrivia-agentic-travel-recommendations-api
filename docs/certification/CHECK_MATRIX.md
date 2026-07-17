---
owner: P_integration / repository maintainer
candidate: 3156cf8869563b9683f5c3ff67b4104d95dc1b40
image_digest: sha256:689c588dcdf98bcd60adbaf26b0d3c52b0a86a694eabe8c5f9736c47ad6517ee
recorded_at: 2026-07-16T23:30:00-04:00
---

# Certification check matrix

The active claim remains D4/E4 until the independent Gate 6 row passes. Failed and superseded attempts remain in the append-only evidence index.

| Check | Result | Notes |
| --- | --- | --- |
| Locked clean install | passed locally | Fresh Windows venv from `requirements-dev.lock` |
| Schemas / design authority | failed independently | clean checkout found stale `IFACE-POLICY-001` and `IFACE-OPS-001` hashes |
| Full pytest | failed independently | 129 passed, 1 failed; replacement candidate required |
| Ruff | passed locally | exit 0 |
| compileall | passed locally | exit 0 |
| Dependency audit / SBOM | passed locally | Linux image audit: no known vulnerabilities; current SBOM retained |
| Container build | passed locally | `arrivia-recs:gate6-3156cf8`; OCI revision and digest match the source candidate |
| Healthy-mock benchmark | passed locally | 100/100 valid requests at concurrency 10; measurement only, no latency SLO |
| MCP stdio smoke | passed locally | discovery and invocation with isolated SQLite path |
| Deployment verifier | passed locally | health, readiness, metrics, audit, exclusion, and cap |
| Failure / circuit / recovery | passed locally | `upstream_error` ×3, `upstream_circuit_open`, then recovery |
| Distinct-image rollback | passed locally | SQLite cap remained enforced across B→A→B; no restore used |
| Links / hashes / evidence freshness | failed independently | evidence artifacts passed; frozen interface hashes did not reproduce |
| Walkthrough render / visual parity | passed locally | deterministic 300-second render and inspected contact sheet |
| Gate 6 independent review | failed | runtime journeys passed, but mandatory full suite failed; D5/E6 not earned |

## Immutable identities

- Superseded completion source candidate: `3156cf8869563b9683f5c3ff67b4104d95dc1b40`
- Completion image digest: `sha256:689c588dcdf98bcd60adbaf26b0d3c52b0a86a694eabe8c5f9736c47ad6517ee`
- Evidence binding tip: the pushed `codex/project-completion` commit containing this matrix and the append-only events
- Retained rollback target: `17cc00d7cf06a04028a1ff3aabdd552875cf5d0a` / `sha256:e5f093d29f0d3fdb54677f3e634604a2cef5914a5423af2a112b0260b49d3d08`

Replacement source/image identities are pending. See `docs/evidence/raw/final-certification/gate6-review-07bbc91-failed.md`.

Latency figures are observations from a local healthy-mock run, not service-level objectives.
