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
| Schemas / design authority | passed locally | `tests/test_design_authority.py` |
| Full pytest | passed locally | 130 passed |
| Ruff | passed locally | exit 0 |
| compileall | passed locally | exit 0 |
| Dependency audit / SBOM | passed locally | Linux image audit: no known vulnerabilities; current SBOM retained |
| Container build | passed locally | `arrivia-recs:gate6-3156cf8`; OCI revision and digest match the source candidate |
| Healthy-mock benchmark | passed locally | 100/100 valid requests at concurrency 10; measurement only, no latency SLO |
| MCP stdio smoke | passed locally | discovery and invocation with isolated SQLite path |
| Deployment verifier | passed locally | health, readiness, metrics, audit, exclusion, and cap |
| Failure / circuit / recovery | passed locally | `upstream_error` ×3, `upstream_circuit_open`, then recovery |
| Distinct-image rollback | passed locally | SQLite cap remained enforced across B→A→B; no restore used |
| Links / hashes / evidence freshness | passed locally | exact source/image and current artifacts validate; independent lookup pending |
| Walkthrough render / visual parity | passed locally | deterministic 300-second render and inspected contact sheet |
| Gate 6 independent review | pending | fresh local Codex reviewer receives only `GATE6_HANDOFF.md` |

## Immutable identities

- Completion source candidate: `3156cf8869563b9683f5c3ff67b4104d95dc1b40`
- Completion image digest: `sha256:689c588dcdf98bcd60adbaf26b0d3c52b0a86a694eabe8c5f9736c47ad6517ee`
- Evidence binding tip: the pushed `codex/project-completion` commit containing this matrix and the append-only events
- Retained rollback target: `17cc00d7cf06a04028a1ff3aabdd552875cf5d0a` / `sha256:e5f093d29f0d3fdb54677f3e634604a2cef5914a5423af2a112b0260b49d3d08`

Latency figures are observations from a local healthy-mock run, not service-level objectives.
