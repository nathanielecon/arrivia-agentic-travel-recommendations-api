# Architecture Overview

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
- REST and MCP session-cap parity is only a same-machine guarantee in v0; horizontal scale is deferred until shared distributed state exists.

## First-step scope

The four-week first step focuses on a runnable internal service with explicit failures, mocked upstreams for local development, and an MCP surface that mirrors the core recommendation flow. The supported v0 rollout is one active recommendation-service replica per environment, with API and MCP session-cap parity guaranteed only for same-machine processes that share `SESSION_BUDGET_STORE_PATH`. Live upstream auth, durable distributed state, and richer ranking stay out of scope for v0.
