---
owner: P_operations / repository maintainer
status: implemented and candidate-bound locally; independent review pending
candidate: f5e9dc4df174b1844741efbfb07cb8bdbca3e34c
last_verified: 2026-07-16
review_trigger: Log schema, metric, label, alert threshold, or deployment-boundary change
---

# Observability strategy

The API emits newline-delimited JSON to standard output. HTTP lifecycle events are
`request.started` and `request.completed`. The shared recommendation service emits
`upstream_call.completed`, `rule_evaluation.completed`, `session_budget.completed`, and
`recommendation.completed`. The successful recommendation event includes the exact structured
`audit_block` returned to the caller.

Common context is `timestamp`, `level`, `event`, `request_id`, and `surface`. Relevant events add
`member_id_hash`, `session_id_hash`, `partner_id`, `outcome`, `duration_seconds`, `error_code`, and
circuit information. Member/session identifiers use a domain-separated SHA-256 prefix. Raw
upstream bodies, complete member profiles, secrets, and raw member/session identifiers are never
logged. Request IDs are accepted only when they match a 128-character safe alphabet.

## Metrics and cardinality

`GET /metrics` is registered only when `METRICS_ENABLED=true`. It is operational metadata, not a
public API: restrict it to the scraper network outside local evaluation. This v0 provides no
production authentication or safe public-internet exposure.

| Metric | Labels | Meaning |
| --- | --- | --- |
| `recommendation_requests_total` | surface, outcome, status_class | Request count |
| `recommendation_request_duration_seconds` | surface, outcome | End-to-end latency |
| `upstream_request_duration_seconds` | dependency, outcome | Member/partner call latency |
| `partner_config_upstream_requests_total` | outcome | Partner dependency results |
| `rule_evaluation_duration_seconds` | partner_id, rule | Rule latency |
| `rule_evaluations_total` | partner_id, rule, value | Normalized rule decisions |
| `session_budget_reservations_total` | outcome | Reservation decisions |
| `budget_reservation_failures_total` | reason | Budget infrastructure failures |
| `circuit_breaker_state` | dependency, state | One-hot closed/open/half-open state |

All enumerated labels have finite values. `partner_id` is the controlled tenant dimension and must
remain bounded by the onboarded partner set; member, session, request, URL, exception text, and raw
cap values are forbidden labels. Cap values normalize to `limited`/`unlimited`.

## Alert ownership and response

The on-call service owner acknowledges P1 within 15 minutes and P2 within one business hour. P1
response is to stop promotion, inspect readiness/error logs, and choose rollback or forward-fix.
P2 response checks dependency health, circuit state, latency, policy drift, and budget storage,
then escalates to the upstream owner when applicable. The deployer owns rollback execution; a
database restore requires evidence of corruption and service-owner approval.

The executable Prometheus definitions are in `alerts.yml`. The tracked Grafana-compatible
dashboard source is `dashboard.json`; it covers request volume/errors, service and dependency
latency, partner-config success, circuit state, budget failures, and exclusion-policy drift:

- P1: readiness fails continuously for two minutes.
- P1: recommendation 5xx exceeds 5% for five minutes, with at least 50 requests.
- P2: partner-config success is below 99% for five minutes, with at least 20 calls.
- P2: the partner-config circuit is open continuously for one minute.
- P2: partner-config p95 exceeds 250 ms continuously for ten minutes.
- P2: a budget infrastructure failure remains visible for five minutes.
- P2: a partner's 15-minute `exclude_cruise=true` share is below 50% of its seven-day baseline,
  only when baseline is at least 5% and the current window has at least 100 evaluations.

The readiness rule relies on an external `probe_success{job="arrivia-readiness"}` probe. Drift
evaluation requires at least seven days of metric retention. If either prerequisite is absent, the
corresponding check is explicitly untested—not silently treated as passing.
