---
owner: P_integration / repository maintainer
candidate: f5e9dc4df174b1844741efbfb07cb8bdbca3e34c
image_digest: sha256:7551188a779f278fbe270348027c8cea213a0c9688dae2bbb5d430c6f8a921d4
recorded_at: 2026-07-16T23:30:00-04:00
---

# Certification check matrix

The active claim remains D4/E4 until the independent Gate 6 row passes. Failed and superseded attempts remain in the append-only evidence index.

| Check | Result | Notes |
| --- | --- | --- |
| Locked clean install | passed locally | Fresh Windows venv from `requirements-dev.lock` |
| Schemas / design authority | passed locally | canonical-LF interface/dependency hashes pass from a separate clean checkout |
| Full pytest | passed locally | 131 passed from replacement clean checkout |
| Ruff | passed locally | exit 0 |
| compileall | passed locally | exit 0 |
| Dependency audit / SBOM | passed locally | Linux image audit: no known vulnerabilities; current SBOM retained |
| Container build | passed locally | `arrivia-recs:gate6-f5e9dc4`; OCI revision and digest match the replacement source |
| Healthy-mock benchmark | passed locally | 100/100 valid requests at concurrency 10; measurement only, no latency SLO |
| MCP stdio smoke | passed locally | discovery and invocation with isolated SQLite path |
| Deployment verifier | passed locally | health, readiness, metrics, audit, exclusion, and cap |
| Failure / circuit / recovery | passed locally | `upstream_error` ×3, `upstream_circuit_open`, then recovery |
| Distinct-image rollback | passed locally | SQLite cap remained enforced across B→A→B; no restore used |
| Links / hashes / evidence freshness | passed locally | replacement clean checkout validates schemas, links, artifacts, and portable hashes |
| Walkthrough render / visual parity | passed locally | deterministic 300-second render and inspected contact sheet |
| Gate 6 independent review | pending replacement review | prior failure retained as `EVID-GATE6-FAIL-07BBC91`; D5/E6 not yet earned |

## Immutable identities

- Replacement source candidate: `f5e9dc4df174b1844741efbfb07cb8bdbca3e34c`
- Replacement image digest: `sha256:7551188a779f278fbe270348027c8cea213a0c9688dae2bbb5d430c6f8a921d4`
- Evidence binding tip: the pushed `codex/project-completion` commit containing this matrix and the append-only events
- Retained rollback target: `17cc00d7cf06a04028a1ff3aabdd552875cf5d0a` / `sha256:e5f093d29f0d3fdb54677f3e634604a2cef5914a5423af2a112b0260b49d3d08`

The superseded `3156cf8` review failure remains at `docs/evidence/raw/final-certification/gate6-review-07bbc91-failed.md`.

Latency figures are observations from a local healthy-mock run, not service-level objectives.
