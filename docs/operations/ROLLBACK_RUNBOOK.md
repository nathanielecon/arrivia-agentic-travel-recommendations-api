---
owner: P_operations / repository maintainer
status: implemented and candidate-bound rehearsal passed; independent review pending
candidate: f5e9dc4df174b1844741efbfb07cb8bdbca3e34c
last_verified: 2026-07-16
review_trigger: Image selection, Compose topology, SQLite path/schema, verifier, or recovery policy change
---

# Single-replica rollback runbook

This procedure is valid only for the documented v0: one active API replica and the `.data` bind
mount. It introduces no SQLite schema migration. Routine rollback preserves live session usage and
its original TTL; it does not reconcile counts or restore a database snapshot.

## Preconditions

- Record the candidate Git SHA, current immutable image digest, previous verified digest, operator,
  UTC time, and incident/evidence ID.
- Confirm the previous digest was built from a schema-compatible release. Never use a mutable tag.
- Stop incoming traffic and confirm no second API replica is serving.

## Procedure

1. Stop the sole API replica: `docker compose stop api`.
2. Confirm the resolved `.data` path is inside this checkout. Create a timestamped snapshot directory
   outside `.data`, then copy `session_budget.sqlite3` and any existing `-wal` and `-shm` siblings.
   Record SHA-256 for every copied file. Do not delete or move the originals.
3. Set `ARRIVIA_RECS_IMAGE` to the complete previous `repository@sha256:digest` value.
4. Start without a build: `docker compose up -d --no-build api`. The Compose file retains
   `./.data:/app/.data`; do not add `-v`, remove the mount, or run a rebuild.
5. Run `python scripts/deployment_verifier.py --base-url http://127.0.0.1:8080` with its generated
   fresh session. Preserve the JSON result, container image ID, logs, and metrics snapshot.
6. Restore traffic only if health, readiness, metrics, audit, cruise exclusion, and session-cap
   checks all pass. Otherwise stop the replica and choose forward-fix or another verified image.

Restore the captured database files only when integrity checks demonstrate corruption and the
service owner approves state replacement. A code rollback selects an old image; a database restore
replaces corrupt state; a rebuild creates a new artifact; failover is unsupported; a forward-fix is
a new candidate. These are separate decisions.

## Controlled failure rehearsal

With Compose mocks running, `python scripts/wiremock_partner_fault.py enable` installs a temporary,
in-memory high-priority partner-policy 502. Run a recommendation request and capture the explicit
502 response, then always run `python scripts/wiremock_partner_fault.py disable`. The helper binds
WireMock admin access to `127.0.0.1` only.

## Image provenance

On 2026-07-16, `docker buildx imagetools inspect` resolved the production base index to
`python:3.12-slim@sha256:57cd7c3a7a273101a6485ba99423ee568157882804b1124b4dd04266317710de`
and WireMock 3.6.0 to
`wiremock/wiremock:3.6.0@sha256:1cf76043f9052c32d13fb06b562e3328e284fc46cf04c756595201f5de7d3c75`.
They are pinned in tracked files. Re-resolve deliberately during dependency updates; never silently
replace them during rollback.

### Docker Desktop on Windows

The Windows host and Docker Desktop's Linux VM are separate SQLite locking domains even though the
bind mount is on one physical machine. Stop the API before any host-side snapshot, integrity check,
or file copy. Restart the container after host access before running the verifier. Do not run a
Windows-host MCP process against the same database while the container API is active; launch MCP
inside the API container, or run both correctness processes bare-metal on Windows. A mere shared
path string does not make cross-kernel SQLite locking safe.
