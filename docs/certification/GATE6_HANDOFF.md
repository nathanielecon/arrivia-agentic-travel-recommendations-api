---
owner: P_integration / repository maintainer
status: independently reviewed and passed
candidate: f5e9dc4df174b1844741efbfb07cb8bdbca3e34c
image_digest: sha256:7551188a779f278fbe270348027c8cea213a0c9688dae2bbb5d430c6f8a921d4
last_verified: 2026-07-16
---

# Gate 6 clean-context handoff

This is the complete reviewer input. It intentionally contains no repair history, prior scores, or author conclusions.

## Candidate

| Field | Value |
| --- | --- |
| Git SHA (source reviewed and used for the image) | `f5e9dc4df174b1844741efbfb07cb8bdbca3e34c` |
| Evidence binding checkout | Exact pushed `codex/project-completion` tip supplied with the reviewer assignment |
| Image | `arrivia-recs:gate6-f5e9dc4` / digest `sha256:7551188a779f278fbe270348027c8cea213a0c9688dae2bbb5d430c6f8a921d4` |
| Previous verified rollback image | `arrivia-recs:c1-verified` / `sha256:e5f093d29f0d3fdb54677f3e634604a2cef5914a5423af2a112b0260b49d3d08` |

## Claim boundary

v0 supports one active recommendation-serving replica. REST and MCP may share session-cap state only through the same SQLite file in one filesystem-locking domain. A Windows host MCP process must not concurrently open the Docker Desktop Linux bind-mounted database. The project does not claim production authentication, safe public-internet exposure, multi-replica consistency, uptime, compliance, autonomous policy creation, or guarantees beyond the independently reproduced v0 boundary.

## Acceptance IDs

Requirements: `REQ-REL-001`, `REQ-POL-001`, `REQ-OBS-001`, `REQ-OPS-001`, `REQ-DOC-001`, `REQ-EVID-001`, `REQ-EVID-002`, `REQ-EVID-003`, `REQ-PORT-001`, `REQ-ORCH-001`

Runtime checks: `CHECK-HEALTH`, `CHECK-READY`, `CHECK-METRICS`, `CHECK-CIRCUIT-RECOVERY`, `CHECK-FINAL-SLOT`, `CHECK-LIVE-CLI`, `CHECK-LIVE-502-RECOVERY`, `CHECK-ROLLBACK`, `CHECK-VISUAL-PARITY`, `CHECK-FULL-PROOF-FLOW`, `CHECK-CLEAN-REVIEW`

## Bootstrap and required reproduction

```powershell
git checkout <exact-evidence-binding-sha-from-review-assignment>
Copy-Item .env.example .env -Force
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements-dev.lock
.\.venv\Scripts\python -m pip install --no-deps -e .
.\.venv\Scripts\python -m pytest -q
.\.venv\Scripts\python -m ruff check .
.\.venv\Scripts\python -m compileall -q src tests scripts
$env:ARRIVIA_RECS_IMAGE = "arrivia-recs:gate6-f5e9dc4"
docker compose --profile mocks up -d
.\.venv\Scripts\python scripts/deployment_verifier.py --base-url http://127.0.0.1:8080
.\.venv\Scripts\python -m arrivia_recs.cli --member-id m1 --session-id gate6-cli --base-url http://127.0.0.1:8080
.\.venv\Scripts\python -m pytest -q tests/test_mcp_stdio_smoke.py tests/test_session_budget_multiprocess.py tests/test_design_authority.py
.\.venv\Scripts\python scripts/healthy_mock_benchmark.py --base-url http://127.0.0.1:8080 --requests 100 --concurrency 10
```

Inject a partner-config fault through the local WireMock admin endpoint, confirm three `upstream_error` responses followed by `upstream_circuit_open`, disable the fault, wait for the open interval, and confirm recovery. Do not alter source or evidence while reviewing.

## Evidence lookup

- Append-only index: `docs/evidence/index.json`
- Certification matrix: `docs/certification/CHECK_MATRIX.md`
- Raw current-candidate captures: `docs/evidence/raw/final-certification/`
- Walkthrough and exact terminal footage: `walkthrough/README.md`

## Pass criteria

Every command and journey above passes from the clean checkout; the evidence artifacts resolve and hash correctly; README claims match the evidence index; and no hidden conversation context or repair is needed. Record blocked and failed checks as failures. D5/E6 is earned only after the reviewer independently reports a full pass.
