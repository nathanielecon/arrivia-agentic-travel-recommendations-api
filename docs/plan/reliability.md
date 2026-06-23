# Reliability Decisions

## Explicit failures over silent degradation

- Upstream network failures become `502`-class errors or explicit MCP error payloads.
- Missing members and missing partner policy are surfaced as distinct not-found cases.
- Invalid upstream JSON or schema mismatches are treated as upstream-invalid payloads instead of being ignored.

## Timeouts and simplicity

- HTTP clients use small request timeouts and avoid background retry loops.
- Session caps are tracked in a local SQLite store for v0, so the API and MCP process can share same-machine state when they use the same `SESSION_BUDGET_STORE_PATH`.
- First rollout assumes a single active replica so the local session budget has one authoritative recommendation-serving replica for that environment.
- Horizontal scale is deferred until the service has shared distributed session state; otherwise the same session could consume separate cap buckets on different replicas or hosts.
- Health and readiness stay shallow so operators can distinguish process health from upstream dependency health.

## On-call expectations

- Responses carry policy audit metadata so incidents can tie a recommendation back to partner rules.
- Structured warnings are emitted for upstream member and partner failures.
- The local Docker path includes checked-in mock stubs so responders can reproduce issues without a live upstream dependency.

## Later work

- A true shared session-budget store with cross-instance consistency across hosts/replicas
- Authenticated upstream calls
- Production metrics, tracing, and deployment manifests tuned for the target environment
