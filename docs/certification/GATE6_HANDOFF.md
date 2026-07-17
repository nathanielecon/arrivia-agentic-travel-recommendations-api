---
owner: P_integration / repository maintainer
status: blocked-after-independent-resume
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

### Local Windows (PyPI available)

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

### Codex Cloud / Linux (PyPI proxy 403 — use committed wheels)

Cloud agent-phase cannot reach PyPI (`HTTP 403`). Do **not** `pip install -r`
from the index and do **not** add `pip download` to setup/maintenance. Use the
vendored wheelhouse checked into the repo:

```bash
# Prefer tip that contains vendor/python-wheels/ (or cherry-pick that commit onto
# a detached worktree of the candidate SHA). Pin Environment Python to 3.12.
bash scripts/install-locked-offline.sh /tmp/g6v
source /tmp/g6v/bin/activate
# then run acceptance commands with this interpreter
```

Manual equivalent: `pip install --no-index --find-links=vendor/python-wheels -r requirements-build.lock -r requirements-dev.lock` then `pip install --no-deps -e .` (see [`vendor/python-wheels/README.md`](../../vendor/python-wheels/README.md)).


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

CloudWarm cache-resume was unblocked by removing `terraform|head` / `aws|head` under `pipefail` in `.codex/cloud-maintenance.sh` (arrivia tip `21b57c0`). Consecutive Force-warms READY on ENV `6a594effc15c8191a0b7fd4af300dda1`.

Resumed GPT-5.4 Gate 6 (worktree; tip checkout preserved):
- Proof `task_e_6a5975185c9c832b8f84f247bb822803` READY: clean checkout of `446679405d41bfd91d6b273e269d35f50afed458` and `compileall` passed; `pip install -r requirements-dev.lock` failed (Cloud proxy/index 403); pytest/Ruff/MCP unavailable; Docker untested.
- Verdict `task_e_6a597677b24c832b9ff579c5522c73be` READY: claim-boundary PASS; score **6/10**; **D5/E6 earned: NO**.

Prior independent attempt failed on Cloud PyPI **403** (not candidate code). Unblock path landed on main:

- `vendor/python-wheels/` (47 Linux cp312 wheels)
- `scripts/install-locked-offline.sh` (`PIP_NO_INDEX`, `--no-build-isolation`, no pip self-upgrade)
- Cloud proof **PASS**: `task_e_6a597b38c7a0832b9a273e859f5574e7` → `offline_install_ok`, **122 tests collected** (`docs/evidence/raw/cloud-offline-install-smoke.md`)

Still do **not** add network `pip download` to setup/maintenance. For Gate 6 on candidate SHA `4466794…`, use a worktree that also has tip’s `vendor/` + installer (or cherry-pick `13ee372`), then `bash scripts/install-locked-offline.sh /tmp/g6v`.


