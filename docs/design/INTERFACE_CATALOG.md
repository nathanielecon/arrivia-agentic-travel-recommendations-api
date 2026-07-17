---
owner: P_authority / repository maintainer
status: accepted
candidate: final-source-freeze-pending
last_verified: 2026-07-16
review_trigger: Any public payload, error, setting, metric, log event, policy field, or session-budget invariant change
---

# Frozen interface catalog

Hashes use SHA-256 over the UTF-8 text `path:file_sha256` for each sorted contract path, joined by `\n` with no terminal newline. The current values are stored in `partition-manifest.json`; a material hash change invalidates every listed consumer until contract tests and evidence are rerun.

## IFACE-REST-001

- Owner: `P_reliability`; consumers: `P_operations`, `P_portfolio`, `P_integration`.
- Request: `POST /v1/recommendations` with non-empty `member_id` and optional `session_id`.
- Success: `200` `RecommendationResponse` containing member/partner identifiers, recommendations, and structured `audit` (`partner_id`, `policy_source`, `rules_applied`).
- Error: FastAPI `{"detail":"<code>"}`; member absence is `404 member_not_found`; required partner absence and dependency failures are `502`; circuit rejection is `502 upstream_circuit_open`.
- Compatibility: additive optional fields require consumer tests; removal, rename, type/status change, or new error semantics require a versioned contract.

## IFACE-MCP-001

- Owner: `P_reliability`; consumers: `P_portfolio`, `P_integration`.
- Tool: `get_travel_recommendations(member_id: str, session_id: str | null) -> str` over stdio.
- Success: JSON-encoded recommendation response with policy audit. Failure: JSON with stable `error`, optional `detail`, and member context; includes `upstream_circuit_open`.
- Compatibility: tool name and existing arguments are stable; additive optional arguments are allowed after stdio smoke coverage.

## IFACE-POLICY-001

- Owner: `P_reliability`; consumers: `P_operations`, `P_portfolio`, `P_integration`.
- Upstream operation: read-only partner lookup resolved from the member's `partner_id`.
- Payload: `partner_id: string`, `max_recommendations_per_session: integer >= 0 | null`, `exclude_cruise: boolean`; `exclude_cruises` is the only accepted legacy alias and cannot conflict with the canonical key.
- Strictness: unknown fields, invalid JSON/schema, or conflicting aliases produce `upstream_invalid_payload`; no policy is invented or cached as fallback.
- Evolution: known value changes are dynamic; new properties require schema, model, evaluator, test, and deployed compatibility window.

## IFACE-BUDGET-001

- Owner: `P_reliability`; consumers: `P_operations`, `P_integration`.
- Key: `(partner_id, session_id)`; value: non-negative `used`, expiry, last-touch timestamp.
- Atomic operation: `reserve(cap, requested)` returns `granted` and `remaining_before`; one `BEGIN IMMEDIATE` transaction contains prune, read, grant, write, capacity enforcement, and commit.
- Invariant: for one shared SQLite file, concurrent grants never make persisted `used > cap`. TTL expiration resets a key; capacity eviction bounds cardinality but does not create distributed guarantees.
- Persistence: routine code rollback preserves database, WAL, and SHM; this hardening has no schema migration.

## IFACE-OPS-001

- Owner: `P_operations`; consumers: `P_portfolio`, `P_integration`.
- Timeouts: connect `0.25s`, read `1.0s`, write `0.25s`, pool `0.25s`; circuit threshold `3`, open interval `30s`, one half-open probe, no retry.
- Settings: `UPSTREAM_CONNECT_TIMEOUT_SECONDS`, `UPSTREAM_READ_TIMEOUT_SECONDS`, `UPSTREAM_WRITE_TIMEOUT_SECONDS`, `UPSTREAM_POOL_TIMEOUT_SECONDS`, `UPSTREAM_CIRCUIT_FAILURE_THRESHOLD`, `UPSTREAM_CIRCUIT_OPEN_SECONDS`, `METRICS_ENABLED`, and `ARRIVIA_RECS_IMAGE`.
- Logs: newline JSON with timestamp, level, event, request ID, surface, hashed member/session context, partner ID, outcome, duration, circuit state, error code, and completion audit. Raw upstream bodies, secrets, and full profiles are forbidden.
- Metrics: `recommendation_requests_total`, `recommendation_request_duration_seconds`, `upstream_request_duration_seconds`, `partner_config_upstream_requests_total`, `rule_evaluation_duration_seconds`, `rule_evaluations_total`, `session_budget_reservations_total`, `budget_reservation_failures_total`, and `circuit_breaker_state`. Labels must be bounded; member/session/request IDs are forbidden labels.
- Endpoint: internal `GET /metrics`, present only when `METRICS_ENABLED`; deployment restricts network access.

