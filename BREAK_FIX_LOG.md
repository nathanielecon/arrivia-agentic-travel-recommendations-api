---
owner: P_authority / repository maintainer
status: accepted
candidate: working-tree@5b2fc6f80e7714d0af5459fa2b9d3a30b1c28896
last_verified: 2026-07-16
review_trigger: Every defect, failed verification, repair, rollback, superseded artifact, or unresolved blocker
---

# Break/fix log

This file is append-only. Never delete failed attempts. A correction adds a new entry that links the original. Timestamps use ISO-8601 with timezone; candidate means an immutable commit or an explicitly labeled working-tree base.

## Entry format

| Field | Required content |
| --- | --- |
| ID / time | Stable `BF-YYYYMMDD-NNN` and timestamp |
| Candidate | Commit SHA, image digest when relevant, dirty-state note |
| Detection | Test/evidence/observation and expected invariant |
| Impact | Affected requirements, users, claims, and evidence invalidated |
| Cause | Reproduced technical cause; use `unknown` until proven |
| Containment | Immediate reversible action |
| Repair | Files/decision/new candidate; never rewrite the old record |
| Verification | Fresh validator/evidence IDs and result |
| Owner/status | One owner; open, contained, fixed, verified, superseded |

## Entries

### BF-20260716-001 — Pre-existing README working-tree modification

- Time: 2026-07-16T13:33:00-04:00
- Candidate: working tree based on `5b2fc6f80e7714d0af5459fa2b9d3a30b1c28896`
- Detection: `git status --short` reported `M README.md` before Phase 0 design files were created.
- Impact: `REQ-DOC-001`, `REQ-PORT-001`; portfolio work could overwrite user content or attribute it to the wrong candidate.
- Cause: Existing user-owned modification; content origin intentionally not inferred.
- Containment: Phase 0 does not edit README. `P_portfolio` is its only mutation owner.
- Repair: Before portfolio mutation, compare README with baseline, preserve the full user diff, and integrate the visual-first/evidence content around it. Record the resulting candidate and review.
- Verification: Pending `TEST-DOC-CONTRACT`, link/claim checks, and user-diff reconciliation review.
- Owner/status: P_portfolio / contained-open.

### BF-20260716-002 — Structured logger retained a temporary capture stream

- Time: 2026-07-16T13:54:00-04:00
- Candidate: dirty working tree based on `5b2fc6f80e7714d0af5459fa2b9d3a30b1c28896`
- Detection: Integrated pytest run produced 12 failures with `ValueError: I/O operation on closed file`; expected request logging to remain available across test capture lifecycles.
- Impact: `REQ-OBS-001`, REST/MCP request tests, and all runtime log evidence were invalid.
- Cause: `PrintLoggerFactory(file=sys.stdout)` retained pytest's temporary capture object after it closed.
- Containment: No runtime evidence was accepted from the failing run.
- Repair: Construct `PrintLoggerFactory()` without binding the current stream and add the full observability/recommendation subset rerun.
- Verification: 23 affected tests passed, followed by 114 non-authority tests, Ruff, and compilation.
- Owner/status: P_operations / verified.

### BF-20260716-003 — First live-fault transcript used unavailable curl.exe

- Time: 2026-07-16T14:02:00-04:00
- Candidate: local Compose image `sha256:51d0e45da9d4b60001a9f92b25d5d0612f19a923bacef13d366499714c0e7d73`
- Detection: PowerShell reported that `curl.exe` was unavailable after the WireMock override was installed.
- Impact: `REQ-EVID-002`; the first request/response assertion was untested.
- Cause: The host PATH does not expose curl.exe.
- Containment: The same command sequence still executed the disable helper; its successful cleanup was observed.
- Repair: Repeat with `Invoke-WebRequest -SkipHttpErrorCheck`, then perform a second four-request circuit run and 31-second recovery.
- Verification: Exact REST bodies showed three `upstream_error` 502s, one `upstream_circuit_open` 502, cleanup passed, and recovery returned 200.
- Owner/status: P_portfolio / verified; failed attempt retained in the raw transcript notes.

### BF-20260716-004 — Production lock audit attempted on the wrong host platform

- Time: 2026-07-16T14:15:00-04:00
- Candidate: dirty working tree based on `5b2fc6f80e7714d0af5459fa2b9d3a30b1c28896`
- Detection: `pip-audit` on Windows could not build Linux-only `uvloop` from `requirements.lock`.
- Impact: Dependency-audit evidence was blocked; the lock itself was not invalid.
- Cause: The production lock is intentionally resolved under the pinned Linux/Python 3.12 base, but the first audit ran under Windows/Python 3.14.
- Containment: Do not remove or conditionally hide the target dependency to make the host audit pass.
- Repair: Run `pip-audit 2.10.1` inside the same pinned Python 3.12 Linux container.
- Verification: Container audit completed with no known vulnerabilities and wrote `sbom/pip-audit.json`.
- Owner/status: P_integration / verified.

### BF-20260716-005 — README worktree marker reconciled

- Time: 2026-07-16T14:05:00-04:00
- Candidate: dirty working tree based on `5b2fc6f80e7714d0af5459fa2b9d3a30b1c28896`
- Detection: Repeated `git diff -- README.md` showed no content delta despite the pre-existing modified marker.
- Impact: `REQ-DOC-001`, `REQ-PORT-001` mutation could proceed without discarding user text.
- Cause: Worktree/index metadata or line-ending state, not a visible content change.
- Containment: Existing README content was retained and extended in place.
- Repair: Add the visual-first architecture, verified working-candidate results, exact claim boundary, assumption matrix, locks, and evidence links around the existing guidance.
- Verification: README contract tests and final link/claim checks are required after interface hash refresh.
- Owner/status: P_portfolio / fixed; final verification pending.

### BF-20260716-006 — Route test coupled to FastAPI's eager router internals

- Time: 2026-07-16T14:35:00-04:00
- Candidate: dirty working tree based on `5b2fc6f80e7714d0af5459fa2b9d3a30b1c28896`; locked FastAPI 0.139.2 / Starlette 1.3.1.
- Detection: First locked clean-environment run had two failures because `app.routes` now contains lazy `_IncludedRouter` objects without direct `path` attributes; live container routes and HTTP responses were healthy.
- Impact: Clean-install gate was red even though the public route contract worked.
- Cause: Tests asserted a framework-private representation instead of the generated OpenAPI contract.
- Containment: Do not downgrade the lock or ignore the failures; compare host, clean venv, container, and live HTTP behavior.
- Repair: Assert registered public paths through `app.openapi()["paths"]`, which is stable across both supported FastAPI representations.
- Verification: Locked clean environment passed 122 tests, Ruff, and compilation; live container verifier remained green.
- Owner/status: P_integration / verified.

### BF-20260716-007 — Docker Desktop bind-mounted SQLite lost cross-kernel writability

- Time: 2026-07-16T14:40:00-04:00
- Candidate: locked image `sha256:18745339ebc3aa07dd96a1287048cf4de477efb9b10ed9aaf558d8a26ebc1977`.
- Detection: Final deployment verifier returned HTTP 500; structured log recorded `budget_infrastructure_error` with `sqlite3.OperationalError: unable to open database file` while health/readiness/metrics stayed available.
- Impact: `REQ-OPS-001`, session-cap correctness, final verifier, and any claim that Windows-host MCP can concurrently share the Docker Linux bind-mounted database.
- Cause: Windows host and Docker Desktop Linux VM are different SQLite locking domains; host access to the NTFS-backed file invalidated the container's subsequent lock/open behavior despite permissive mode bits.
- Containment: Stop the API before host database access; do not run host MCP and container API against the same file.
- Repair: Stop API, integrity-check and preserve timestamped snapshots, copy identical database bytes to a new NTFS file identity, restart the unchanged image, and narrow documentation to one filesystem-locking domain. For Compose, run MCP inside the API container.
- Verification: Container integrity check returned `ok`, `BEGIN IMMEDIATE` succeeded, and the deployment verifier again passed health, readiness, metrics, audit, exclusion, and cap checks.
- Owner/status: P_operations / verified locally; distinct-image rollback remains untested.
