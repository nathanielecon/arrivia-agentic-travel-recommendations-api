# Operator runbook - Agentic Travel Recommendations API

On-call reference for the v0, four-week first step. The service stays containerized, partner configuration remains read-only, and recommendation responses should preserve tenant-aware audit information for incident review.

## Quick Smoke

1. Liveness: `GET /health` returns `200`
2. Readiness: `GET /ready` returns `200`
3. Recommendation smoke: only run after member and partner upstreams are reachable

Local example on port `8080`:

```powershell
curl -s http://127.0.0.1:8080/health
curl -s http://127.0.0.1:8080/ready
```

## Local Run Commands

### Python on the host

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
$env:MEMBER_SERVICE_BASE_URL="http://127.0.0.1:8081"
$env:PARTNER_CONFIG_BASE_URL="http://127.0.0.1:8082"
python -m uvicorn arrivia_recs.main:app --reload --host 127.0.0.1 --port 8080
```

These localhost overrides are required when mocks run in Docker and the API runs on bare metal. The `.env.example` defaults use Compose-only hostnames.

### Docker Compose (API only)

```powershell
Copy-Item .env.example .env -Force
docker compose up --build
```

### Docker Compose with WireMock mocks

```powershell
Copy-Item .env.example .env -Force
docker compose --profile mocks up --build
```

Inside Compose, the app expects:

- `MEMBER_SERVICE_BASE_URL=http://member-service:8081`
- `PARTNER_CONFIG_BASE_URL=http://partner-config-service:8082`

If the API container is up but the mocks are missing, recommendation calls should fail explicitly with `502`-class errors instead of silently bypassing partner policy.

v0 rollout topology:

- keep one active API replica
- evaluate MCP parity from the same machine as that active replica
- do not horizontally scale until a shared distributed session-state layer exists
- share `SESSION_BUDGET_STORE_PATH` between the active API process and any host-side MCP process

## MCP Smoke

Start the MCP server from the host when you want an agent-facing validation path:

```powershell
$env:MEMBER_SERVICE_BASE_URL="http://127.0.0.1:8081"
$env:PARTNER_CONFIG_BASE_URL="http://127.0.0.1:8082"
python -m arrivia_recs.mcp.server
```

Then register the stdio server in an MCP client and confirm:

1. `get_travel_recommendations` is discoverable
2. `{"member_id":"m1","session_id":"review-session-1"}` returns partner-aware output
3. the JSON response includes an `audit` block

Repository-backed proof command:

```powershell
python -m pytest tests/test_mcp_stdio_smoke.py -q
```

## Operator-Relevant Configuration

Loaded from environment or `.env` in the working directory:

| Variable | Role |
| --- | --- |
| `MEMBER_SERVICE_BASE_URL` | Base URL for member profile reads |
| `PARTNER_CONFIG_BASE_URL` | Base URL for read-only partner-policy reads |
| `APP_ENV` | Deployment label such as `local` or `staging` |
| `APP_NAME` | Service name for logs and metadata |
| `SESSION_BUDGET_STORE_PATH` | Local SQLite file for same-machine session-cap parity between API and MCP |
| `UPSTREAM_*_TIMEOUT_SECONDS` | Strict connect/read/write/pool budgets |
| `UPSTREAM_CIRCUIT_*` | Failure threshold and open interval |
| `METRICS_ENABLED` | Registers the internal `/metrics` endpoint when true |
| `ARRIVIA_RECS_IMAGE` | Compose image digest selected for promotion or rollback |

Misconfigured URLs are a common cause of `upstream_unreachable`.

## API Surfaces

- `POST /v1/recommendations`: primary public recommendation contract using `RecommendationService`

Use the primary path for reviewer smoke tests, incident triage, and MCP parity checks.

## Deployment Guardrail

Do not scale this service above one active recommendation-serving replica in v0. If failover is required, promote one replacement replica and keep the previous active replica out of service. Matching `SESSION_BUDGET_STORE_PATH` values alone do not make session caps globally consistent across replicas.

## Common Failures

| Symptom | Likely cause | What to check | Mitigation |
| --- | --- | --- | --- |
| `502` with `upstream_unreachable` | member or partner client cannot connect | `MEMBER_SERVICE_BASE_URL`, `PARTNER_CONFIG_BASE_URL`, `docker compose ps` | fix URL or start the mocks profile |
| `404` with `member_not_found` | unknown member ID | member mock mappings or upstream data | use `m1` for local smoke or fix the fixture |
| `502` with `partner_policy_not_found` | missing partner policy | partner mock mappings or upstream data | add or fix the partner policy fixture |
| `502` with `upstream_error` | upstream returned non-2xx | upstream logs and request URL | restore the upstream dependency |
| `502` with `upstream_circuit_open` | three qualifying failures opened a per-process circuit | circuit metric and upstream logs | restore dependency; allow one half-open probe after 30s |

## Rollback

Use the canonical [single-replica rollback runbook](../operations/ROLLBACK_RUNBOOK.md). Stop the sole
replica, snapshot the SQLite database plus WAL/SHM, select a previous immutable digest with
`ARRIVIA_RECS_IMAGE`, start with `--no-build`, and run `scripts/deployment_verifier.py` with a fresh
session. Routine code rollback keeps `.data` and active counts until their existing TTL. Restore a
database snapshot only for demonstrated corruption; rollback, restore, rebuild, failover, and
forward-fix are separate decisions.

## On-Call Notes

1. v0 keeps partner configuration read-only. Do not work around bad policy by editing upstream config from this service.
2. Recommendation responses should remain auditable. Inspect the `audit` block and confirm the applied rules match the partner policy fixture. Older internal demos may refer to the same concept as `policy_audit`.
3. Multi-tenant investigations should always confirm that the response partner context matches the member's `partner_id`.
4. WireMock plus the `mocks` profile is the supported local incident-repro path.
5. v0 session-cap behavior is only authoritative inside the single active rollout machine. Horizontal scale is intentionally deferred until shared distributed state exists.
6. Same-machine API and MCP processes should share `SESSION_BUDGET_STORE_PATH`; mismatched paths can make session-cap behavior look inconsistent during debugging.

## Related Docs

- `README.md`
- `docs/plan/mcp-tools.md`
- `docs/examples/mcp-stdio-transcript.md`
- `docs/examples/judge-proof.md`
