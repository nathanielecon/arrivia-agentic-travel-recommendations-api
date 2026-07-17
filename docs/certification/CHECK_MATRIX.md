---
owner: P_integration / repository maintainer
candidate: f5e9dc4df174b1844741efbfb07cb8bdbca3e34c
image_digest: sha256:7551188a779f278fbe270348027c8cea213a0c9688dae2bbb5d430c6f8a921d4
recorded_at: 2026-07-16T23:30:00-04:00
---

# Certification check matrix

The replacement candidate earned D5/E6 after a fresh clean-context reviewer passed every required check. Failed and superseded attempts remain in the append-only evidence index.

| Check | Result | Notes |
| --- | --- | --- |
| Locked clean install | passed independently | Fresh Windows venv from `requirements-dev.lock` |
| Schemas / design authority | passed independently | 9/9; portable hashes, schemas, ownership, IDs, links, and artifacts |
| Full pytest | passed independently | 131 passed; one third-party deprecation warning |
| Ruff | passed independently | exit 0 |
| compileall | passed independently | exit 0 |
| Dependency audit / SBOM | passed locally | Linux image audit: no known vulnerabilities; current SBOM retained |
| Container build | passed locally | `arrivia-recs:gate6-f5e9dc4`; OCI revision and digest match the replacement source |
| Healthy-mock benchmark | passed independently | 100/100 valid at concurrency 10; p95 185.778 ms measurement only |
| MCP stdio smoke | passed independently | 2 passed; discovery, invocation, audit, exclusion, and cap parity |
| Deployment verifier | passed independently | health, readiness, metrics, audit, exclusion, and cap |
| Failure / circuit / recovery | passed independently | `upstream_error` ×3, `upstream_circuit_open`, cleanup, then HTTP 200 |
| Distinct-image rollback | passed locally | SQLite cap remained enforced across B→A→B; no restore used |
| Links / hashes / evidence freshness | passed independently | 15/15 README links; 0 missing and 0 mismatched declared artifact hashes |
| Walkthrough render / visual parity | passed after user soundtrack selection | Every static scene is five seconds; all 160 encoded frames and scene cuts remain validated; user-supplied Suno track “Quiet Systems” is duration-fitted, credited, level-checked, and reproducible; see `EVID-WALKTHROUGH-QUIET-SYSTEMS` |
| Gate 6 independent review | passed | no defects or blocked checks; `EVID-GATE6-PASS-F4C6D50` |
| Post-certification PR #2 integration | passed | read-only Grok council + sole lead writer resolved five conflicts; 132 tests and no-index offline bootstrap passed; reviewed runtime/image unchanged; see `BF-20260716-026` and `ADR-009` |
| Post-merge portfolio refresh | passed independently | candidate `86fd185d`; locked no-network Python 3.12 install, 139 tests, evidence/archive authority, links, diagrams, all 160 frames and every scene boundary passed; see `EVID-POSTMERGE-PORTFOLIO-REFRESH` |

## Immutable identities

- Replacement source candidate: `f5e9dc4df174b1844741efbfb07cb8bdbca3e34c`
- Replacement image digest: `sha256:7551188a779f278fbe270348027c8cea213a0c9688dae2bbb5d430c6f8a921d4`
- Evidence binding tip: the pushed `codex/project-completion` commit containing this matrix and the append-only events
- Retained rollback target: `17cc00d7cf06a04028a1ff3aabdd552875cf5d0a` / `sha256:e5f093d29f0d3fdb54677f3e634604a2cef5914a5423af2a112b0260b49d3d08`

The superseded `3156cf8` review failure remains at `docs/evidence/raw/final-certification/gate6-review-07bbc91-failed.md`.

Latency figures are observations from a local healthy-mock run, not service-level objectives.

The post-certification integration and walkthrough corrections do not alter the reviewed runtime source or image identity above. The original Gate 6 row remains 131 tests because that is the historical review result; the merged-tree integration result is 132 tests and the final portfolio-refresh result is 139 tests, recorded separately. No D6 tier exists: the earned level remains D5/E6.
