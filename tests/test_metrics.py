from types import SimpleNamespace

from fastapi.testclient import TestClient

import arrivia_recs.main as main_module
from arrivia_recs.main import create_app


def test_metrics_endpoint_exposes_contract_names() -> None:
    response = TestClient(create_app()).get("/metrics")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/plain")
    for metric in (
        "recommendation_requests_total",
        "recommendation_request_duration_seconds",
        "upstream_request_duration_seconds",
        "partner_config_upstream_requests_total",
        "rule_evaluation_duration_seconds",
        "rule_evaluations_total",
        "session_budget_reservations_total",
        "budget_reservation_failures_total",
        "circuit_breaker_state",
    ):
        assert metric in response.text


def test_metrics_endpoint_is_not_registered_when_disabled(monkeypatch) -> None:
    monkeypatch.setattr(
        main_module,
        "settings",
        SimpleNamespace(app_name="test", metrics_enabled=False, log_level="INFO"),
    )
    response = TestClient(main_module.create_app()).get("/metrics")
    assert response.status_code == 404


def test_request_middleware_sets_or_replaces_request_id() -> None:
    client = TestClient(create_app())
    accepted = client.get("/health", headers={"x-request-id": "review-123"})
    rejected = client.get("/health", headers={"x-request-id": "unsafe request id"})
    assert accepted.headers["x-request-id"] == "review-123"
    assert rejected.headers["x-request-id"] != "unsafe request id"
