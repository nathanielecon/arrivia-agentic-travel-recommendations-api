from __future__ import annotations

from prometheus_client import Counter, Gauge, Histogram

recommendation_requests_total = Counter(
    "recommendation_requests_total",
    "Recommendation HTTP requests by bounded outcome and status class.",
    ("surface", "outcome", "status_class"),
)
recommendation_request_duration_seconds = Histogram(
    "recommendation_request_duration_seconds",
    "End-to-end recommendation request duration.",
    ("surface", "outcome"),
)
upstream_request_duration_seconds = Histogram(
    "upstream_request_duration_seconds",
    "Upstream dependency call duration.",
    ("dependency", "outcome"),
)
partner_config_upstream_requests_total = Counter(
    "partner_config_upstream_requests_total",
    "Partner-config dependency calls.",
    ("outcome",),
)
rule_evaluation_duration_seconds = Histogram(
    "rule_evaluation_duration_seconds",
    "Partner-rule evaluation duration.",
    ("partner_id", "rule"),
)
rule_evaluations_total = Counter(
    "rule_evaluations_total",
    "Partner-rule evaluations by normalized value.",
    ("partner_id", "rule", "value"),
)
session_budget_reservations_total = Counter(
    "session_budget_reservations_total",
    "Session-budget reservation attempts.",
    ("outcome",),
)
budget_reservation_failures_total = Counter(
    "budget_reservation_failures_total",
    "Session-budget infrastructure failures.",
    ("reason",),
)
circuit_breaker_state = Gauge(
    "circuit_breaker_state",
    "Circuit state as a one-hot gauge.",
    ("dependency", "state"),
)

_DEPENDENCIES = ("member", "partner_config")
_CIRCUIT_STATES = ("closed", "open", "half_open")
for _dependency in _DEPENDENCIES:
    for _state in _CIRCUIT_STATES:
        circuit_breaker_state.labels(dependency=_dependency, state=_state).set(
            1 if _state == "closed" else 0
        )


def set_circuit_state(dependency: str, state: str) -> None:
    """Set a bounded one-hot circuit state; invalid values fail fast."""
    if dependency not in _DEPENDENCIES:
        raise ValueError(f"unsupported dependency: {dependency}")
    if state not in _CIRCUIT_STATES:
        raise ValueError(f"unsupported circuit state: {state}")
    for candidate in _CIRCUIT_STATES:
        circuit_breaker_state.labels(dependency=dependency, state=candidate).set(
            1 if candidate == state else 0
        )


def normalize_rule_value(rule: str, value: object) -> str:
    """Map dynamic rule values to finite label sets."""
    if rule == "exclude_cruise":
        return "true" if value is True else "false"
    if rule == "max_recommendations_per_session":
        return "unlimited" if value is None else "limited"
    return "unsupported"
