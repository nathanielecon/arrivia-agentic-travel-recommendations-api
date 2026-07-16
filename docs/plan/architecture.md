# Architecture Overview

The six-page [draw.io source](../architecture/arrivia-system.drawio) is topology authority; its
[exact SVG](../architecture/arrivia-system.svg) and [PNG](../architecture/arrivia-system.png) are
review renders. This page is supporting prose, not a competing diagram.

This service ships a small, container-friendly FastAPI application with two external-facing surfaces:

- HTTP routes under `src/arrivia_recs/api/routes/`
- An MCP stdio server under `src/arrivia_recs/mcp/server.py`

## Service boundaries

- `api/`: FastAPI routers for health, readiness, and recommendation endpoints.
- `domain/` and `schemas/`: request, response, member, booking, and policy models.
- `integrations/`: read-only clients for member data and partner configuration.
- `services/`: recommendation orchestration and policy application.
- `use_cases/`: thin compatibility package that points callers at the recommendation workflows.
- `mcp/`: MCP tool registration that forwards to the shared recommendation service.

## Request flow

1. The API or MCP tool receives a member ID and optional session ID.
2. The service loads member context from the member service.
3. The service loads partner policy from the partner configuration service.
4. Recommendation candidates are derived from recent travel history.
5. Partner exclusions and per-session caps are applied.
6. The response includes an audit block that records the partner context and rules applied.

## Enforcement and isolation

- Partner configuration is read-only. This service never mutates upstream policy.
- Session caps are tracked per `(partner_id, session_id)` to avoid tenant crossover.
- Audit metadata is returned with every recommendation response so on-call responders can see which rule applied.
- v0 deployment assumes a single active service replica for first rollout.
- REST and MCP session-cap parity is only a one-file, one-locking-domain guarantee in v0; both
  processes must run in the same OS/container filesystem domain. Horizontal scale and cross-kernel
  bind-mount concurrency are deferred until shared distributed state exists.
- Partner policies must identify the same partner requested by the service; a mismatch fails closed.

## Partner-policy data model

The machine-readable contract is [partner-policy.schema.json](../contracts/partner-policy.schema.json)
with a [valid example](../contracts/partner-policy.example.json). `partner_id` is a required string;
`max_recommendations_per_session` is `null` for unlimited or a non-negative integer; and
`exclude_cruise` is the canonical boolean exclusion flag. `exclude_cruises` is the only accepted
legacy alias, and conflicting canonical/alias values are rejected.

Known value changes are dynamic. Unknown properties fail closed as `upstream_invalid_payload`.
Adding a rule requires a model field, evaluator, contract test, deployment support, and a versioned
compatibility window. Type or semantic changes never take effect as an unversioned payload change.

## First-step scope

The four-week first step focuses on a runnable internal service with explicit failures, mocked upstreams for local development, and an MCP surface that mirrors the core recommendation flow. The supported v0 rollout is one active recommendation-service replica per environment, with API and MCP session-cap parity guaranteed only for same-machine processes that share `SESSION_BUDGET_STORE_PATH`. Live upstream auth, durable distributed state, and richer ranking stay out of scope for v0.
