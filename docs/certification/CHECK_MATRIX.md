---
owner: P_integration / repository maintainer
candidate: PENDING_C3_SHA
image_digest: sha256:76e294048920ae40f37db1c0f7f5e9f8625ef213abea3b5a81245638f176aead
recorded_at: 2026-07-16T16:55:00-04:00
---

# Certification check matrix

| Check | Result | Notes |
| --- | --- | --- |
| Locked clean install | pending-final | Re-run after C3 evidence rebind |
| Schemas / design authority | passed | `tests/test_design_authority.py` |
| Full pytest | pending-final | Re-run after C3 |
| Ruff | passed | exit 0 |
| compileall | passed | exit 0 |
| Dependency audit / SBOM | passed | Linux container `pip-audit`; no known vulnerabilities |
| Container build (B) | passed | `sha256:76e294048920ae40f37db1c0f7f5e9f8625ef213abea3b5a81245638f176aead` |
| Benchmark | untested | No measured workload harness in repo |
| MCP stdio smoke | passed | host SQLite domain |
| Deployment verifier (B) | passed | health/ready/metrics/audit/exclusion/cap |
| Failure/recovery | passed | WireMock 502 + circuit + disable |
| Rollback A←B | passed | seed session remained at cap (`0` grants); `.data` preserved |
| Links / evidence freshness | pending-final | After candidate rebind |
| Visual inspection | passed | Walkthrough frames; footage under annotations |
| Gate 6 independent review | pending | Clean-context agent |

## Digests

- C1 / image A: `17cc00d7cf06a04028a1ff3aabdd552875cf5d0a` / `sha256:e5f093d29f0d3fdb54677f3e634604a2cef5914a5423af2a112b0260b49d3d08`
- C2 / image B: `67ca053d2d5f62051fd175dc091b7dd1e2bbc5e8` / `sha256:76e294048920ae40f37db1c0f7f5e9f8625ef213abea3b5a81245638f176aead`
