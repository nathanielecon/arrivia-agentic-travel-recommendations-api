---
owner: P_authority / repository maintainer
status: accepted
candidate: f5e9dc4df174b1844741efbfb07cb8bdbca3e34c
last_verified: 2026-07-16
review_trigger: Requirement, interface, dependency, topology, trust-boundary, state, recovery, or public-claim change
---

# Arrivia project charter, system design, and reimplementation order

## Charter and claim boundary

The service helps an internal travel concierge obtain recommendations for a member while enforcing read-only partner policy. Human reviewers, application clients, and MCP-capable agents are the immediate users. A successful request returns recommendations and a policy audit; an unsafe or unavailable dependency produces an explicit error rather than invented policy.

The design package earns `D5 Reimplementable` with `E6` independent reproduction. The certified v0 claim remains restricted to one active recommendation-serving replica. REST and MCP processes may coordinate budget state only through one same-machine SQLite file. No production authentication, public exposure, multi-replica consistency, availability, compliance, or guarantees beyond the reviewed v0 are claimed.

Non-goals are upstream writes, generalized travel inventory/search, distributed coordination, account authorization, and silent policy fallback. Expected v0 load is evaluation/demo traffic bounded by `10,000` live session keys and the configured `1,800s` idle TTL; capacity or cost claims beyond that require a measured workload.

## Environments and system context

| Environment | Purpose | Authority and ceiling |
| --- | --- | --- |
| Local Python | Unit/integration tests, CLI, MCP stdio | Developer machine; `E2` |
| Local Compose | One API container, two controlled WireMock upstreams, `.data` bind mount | Candidate-bound verification; up to `E4` after capture |
| Clean review | Fresh checkout and context-free execution | Independent reviewer; required for `D5/E6` |

Both public surfaces construct the same `RecommendationService`. The service reads a member profile, then reads that member's partner policy, derives deterministic candidates, applies exclusion rules, atomically reserves a capped count in SQLite when a session cap applies, and returns a structured audit. The member and partner dependencies are outside the service trust boundary and their payloads are untrusted. SQLite, logs, and metrics are operational state; only the SQLite budget is correctness-affecting.

## Components, interfaces, and data flow

1. `POST /v1/recommendations` or MCP `get_travel_recommendations` accepts `member_id` and optional `session_id`.
2. `MemberClient` performs a read-only member lookup. `404` is a business absence; timeout, transport failure, `429`, `5xx`, invalid JSON, and invalid schema are dependency failures.
3. `PartnerConfigClient` reads the resolved partner policy. Missing or untrusted policy fails closed; no cache or default policy is substituted.
4. `RecommendationService` enforces exclusions and cap semantics for both surfaces.
5. `SessionRecommendationBudget.reserve()` wraps read, grant calculation, write, and commit in `BEGIN IMMEDIATE`; the invariant is `persisted used <= cap` for one shared SQLite file.
6. The surface returns the same business outcome shape appropriate to its protocol, including policy-audit information. Structured completion logs and bounded-cardinality metrics describe the request without raw profiles, bodies, secrets, or unhashed member/session identifiers.

The normative contracts and compatibility rules are in [INTERFACE_CATALOG.md](INTERFACE_CATALOG.md). Existing duplicate/legacy adapter models are compatibility code, not a second architectural path; hardening applies first to clients constructed by REST and MCP factories.

## Reliability, security, and failure behavior

Each process holds one independent circuit per dependency. A circuit opens after three consecutive qualifying failures, rejects calls for 30 seconds, and permits one half-open probe. Successful trusted responses reset the failure count; `404` does not trip a circuit. HTTP connect/read/write/pool budgets are `0.25s/1.0s/0.25s/0.25s` with no automatic retry. The public code `upstream_circuit_open` maps to REST `502` and an MCP JSON error.

Partner policy rejects unknown properties. Value changes to known fields are dynamic; a new rule requires model, evaluator, contract test, and release support. Member and session identifiers are hashed in logs. Metrics are internal operational metadata and must be network-restricted outside local evaluation. Environment configuration contains endpoints and operational settings; secrets, if added later, must be externally injected and must never enter manifests or evidence.

Readiness and recommendation error rate are P1 signals. Partner success, circuit-open duration, partner latency, budget infrastructure failure, and material exclusion-rule drift are P2 signals. Exact thresholds and queries are implementation acceptance in `REQ-OBS-001` and `REQ-OPS-001`.

## Delivery, rollback, performance, and cost

Source is packaged into a non-root Python container. Promotion must select an immutable digest through `ARRIVIA_RECS_IMAGE`; mutable tags or rebuild-at-rollback are prohibited. Routine rollback stops the sole replica, snapshots SQLite plus WAL/SHM, starts the previous image without deleting `.data`, then runs business and telemetry verification. The snapshot is restored only for corruption. This release adds no database migration; live counts retain their original TTL across routine rollback.

Latency is dominated by two upstream reads. The design intentionally performs no retry, bounding work and avoiding retry storms. Prometheus histograms must show actual latency before a throughput or p95 claim is published. Direct runtime cost is one small API process, two upstream calls per recommendation request, local disk I/O, and telemetry storage; no currency estimate is authoritative without a target host and measured volume. Rendering dependencies remain outside the production image.

## Reimplementation order and recovery paths

1. Validate `project-design.json`, the requirement matrix, dependency register, partition ownership, and interface hashes.
2. Implement the REST request/response and MCP tool over one `RecommendationService` using fakes.
3. Implement strict member/policy adapters and the fail-fast circuit state machine.
4. Implement atomic SQLite reservation and prove the final-slot race with independently spawned processes.
5. Add redacted JSON logs, Prometheus metrics, health/readiness, and failure translation.
6. Package one immutable image; wire controlled dependencies; run success, injected-`502`, recovery, and rollback drills.
7. Capture candidate-bound evidence, exact architecture renders, and presentation derivatives.
8. Give a fresh reviewer only the candidate and acceptance criteria. Earn `D5/E6` only if they reproduce without repair history.

Recovery distinguishes five actions: rollback changes code only; database restore replaces corrupt state; rebuild produces a new artifact and is never rollback; failover is unsupported in v0; forward-fix creates a new candidate and revalidates affected consumers.

## D4 design gate

The design gate is passed for implementation planning because all ten mandatory requirements have acceptance and evidence definitions, dependencies and risks are registered, mutable paths have one owner, public interfaces have compatibility/invalidation rules, and frozen decisions are recorded. The gate does not certify implementation. Any interface hash change invalidates affected partition work and evidence; any ownership overlap blocks parallel writes; any broader scale/security claim reopens the charter and ADR review.

