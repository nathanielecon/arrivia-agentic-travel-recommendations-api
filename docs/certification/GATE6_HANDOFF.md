---
owner: P_integration / repository maintainer
status: blocked-after-independent-attempts
candidate: 446679405d41bfd91d6b273e269d35f50afed458
image_digest: sha256:84b02d8bc734e2cb3286fe261ef1cee666117ebeaeb21a6775dfffaaa1f9e720
last_verified: 2026-07-16
---

# Gate 6 clean-context handoff

This package is the only input an independent reviewer should need. It contains no prior scores and no repair narrative.

## Candidate

| Field | Value |
| --- | --- |
| Git SHA (code + certification image source) | `446679405d41bfd91d6b273e269d35f50afed458` |
| Tip with evidence rebind | Repository tip containing the attestation event |
| Image | `arrivia-recs:gate6-4466794` / digest `sha256:84b02d8bc734e2cb3286fe261ef1cee666117ebeaeb21a6775dfffaaa1f9e720` |
| Previous verified image (rollback target) | `arrivia-recs:c1-verified` / digest `sha256:e5f093d29f0d3fdb54677f3e634604a2cef5914a5423af2a112b0260b49d3d08` from SHA `17cc00d7cf06a04028a1ff3aabdd552875cf5d0a` |

## Claim boundary

v0 supports one active recommendation-serving replica. REST and MCP may share session-cap state only through the same SQLite file in one filesystem-locking domain. A Windows host MCP process must not concurrently open the Docker Desktop Linux bind-mounted database. The project does not claim production authentication, safe public-internet exposure, multi-replica consistency, uptime, compliance, autonomous policy creation, or independent reimplementability until this Gate 6 review passes.

## Bootstrap

```powershell
git checkout 446679405d41bfd91d6b273e269d35f50afed458
Copy-Item .env.example .env -Force
# If host port 8082 is occupied, set PARTNER_CONFIG_ADMIN_PORT=18082 in .env
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.lock
python -m pip install --no-deps -e .
$env:ARRIVIA_RECS_IMAGE = "arrivia-recs:gate6-4466794"
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

## Independent attempt outcome

The arrivia Environment `6a594effc15c8191a0b7fd4af300dda1` warmed successfully with GPT-5.4 and an offline wheel cache. A first independent proof on the superseded candidate reached a clean checkout but exposed the unmarked Windows-only `pywin32` pin. After repairing that lock portability defect, three clean-suite attempts and one verdict-only task terminated with Codex task status `ERROR` and no command output. Independent reproduction of this candidate is therefore blocked, not passed; D5/E6 is not earned.
