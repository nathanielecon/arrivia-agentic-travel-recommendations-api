---
owner: P_integration / repository maintainer
status: ready-for-independent-review
candidate: fdfc3a5efdeb2f79259983b1f4c8259d639074d5
image_digest: sha256:76e294048920ae40f37db1c0f7f5e9f8625ef213abea3b5a81245638f176aead
last_verified: 2026-07-16
---

# Gate 6 clean-context handoff

This package is the only input an independent reviewer should need. It contains no prior scores and no repair narrative.

## Candidate

| Field | Value |
| --- | --- |
| Git SHA (code + certification image source) | `fdfc3a5efdeb2f79259983b1f4c8259d639074d5` |
| Tip with evidence rebind (optional) | `c818c2f2d1c1cdd111bf76018f7a5fbdeb342bde` |
| Image | `arrivia-recs:c3-candidate` / digest `sha256:76e294048920ae40f37db1c0f7f5e9f8625ef213abea3b5a81245638f176aead` |
| Previous verified image (rollback target) | `arrivia-recs:c1-verified` / digest `sha256:e5f093d29f0d3fdb54677f3e634604a2cef5914a5423af2a112b0260b49d3d08` from SHA `17cc00d7cf06a04028a1ff3aabdd552875cf5d0a` |

## Claim boundary

v0 supports one active recommendation-serving replica. REST and MCP may share session-cap state only through the same SQLite file in one filesystem-locking domain. A Windows host MCP process must not concurrently open the Docker Desktop Linux bind-mounted database. The project does not claim production authentication, safe public-internet exposure, multi-replica consistency, uptime, compliance, autonomous policy creation, or independent reimplementability until this Gate 6 review passes.

## Bootstrap

```powershell
git checkout fdfc3a5efdeb2f79259983b1f4c8259d639074d5
Copy-Item .env.example .env -Force
# If host port 8082 is occupied, set PARTNER_CONFIG_ADMIN_PORT=18082 in .env
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.lock
python -m pip install --no-deps -e .
$env:ARRIVIA_RECS_IMAGE = "arrivia-recs:c3-candidate"
docker compose --profile mocks up --build -d
```

## Acceptance IDs

Requirements: `REQ-REL-001`, `REQ-POL-001`, `REQ-OBS-001`, `REQ-OPS-001`, `REQ-DOC-001`, `REQ-EVID-001`, `REQ-EVID-002`, `REQ-EVID-003`, `REQ-PORT-001`, `REQ-ORCH-001`

Validators: `TEST-CB-UNIT`, `TEST-UPSTREAM-REST`, `TEST-UPSTREAM-MCP`, `TEST-HALFOPEN-RACE`, `TEST-POLICY-SCHEMA`, `TEST-POLICY-CONTRACT`, `TEST-BUDGET-CROSSPROCESS`, `TEST-LOG-SCHEMA`, `TEST-METRICS`, `TEST-ALERT-RULES`, `TEST-DEPLOY-VERIFY`, `TEST-ROLLBACK-STATE`, `TEST-DOC-CONTRACT`, `TEST-B2-CONTRACT`, `TEST-LIVE-CLI`, `TEST-LIVE-502`, `TEST-DIAGRAM-PARITY`, `TEST-PORTFOLIO-CLAIMS`, `TEST-WALKTHROUGH`, `TEST-TASK-SCHEMA`, `TEST-PARTITION-OWNERSHIP`, `TEST-INTERFACE-HASH`, `TEST-CLEAN-INSTALL`, `TEST-EVIDENCE-FRESHNESS`

Runtime checks: `CHECK-HEALTH`, `CHECK-READY`, `CHECK-METRICS`, `CHECK-CIRCUIT-RECOVERY`, `CHECK-FINAL-SLOT`, `CHECK-LIVE-CLI`, `CHECK-LIVE-502-RECOVERY`, `CHECK-ROLLBACK`, `CHECK-VISUAL-PARITY`, `CHECK-FULL-PROOF-FLOW`, `CHECK-CLEAN-REVIEW`

## Required reproduction commands

```powershell
python -m pytest -q
python -m ruff check .
python -m compileall -q src tests scripts
python scripts/deployment_verifier.py --base-url http://127.0.0.1:8080
python -m arrivia_recs.cli --member-id m1 --session-id gate6-cli --base-url http://127.0.0.1:8080
python -m pytest -q tests/test_mcp_stdio_smoke.py
python -m pytest -q tests/test_design_authority.py
```

Evidence lookup: `docs/evidence/index.json`

## Pass criteria for D5/E6

1. Fresh checkout of the candidate SHA installs from the locked files and passes the full pytest suite, Ruff, and compileall.
2. Compose with the candidate image digest passes the deployment verifier.
3. Live CLI success is reproducible; controlled partner failure/recovery is reproducible when WireMock admin is available.
4. Claims in README and evidence stay within the boundary above.
5. Reviewer records results independently; the authoring worker must not self-certify.
