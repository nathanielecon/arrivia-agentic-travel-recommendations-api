import json
from pathlib import Path

import pytest

from scripts import deployment_verifier

ROOT = Path(__file__).parents[1]


def test_verifier_checks_health_metrics_audit_exclusion_and_cap(monkeypatch) -> None:
    recommendation_calls = 0

    def fake_request(method: str, url: str, payload=None):
        nonlocal recommendation_calls
        if url.endswith("/health"):
            body = {"status": "ok"}
        elif url.endswith("/ready"):
            body = {"status": "ready"}
        elif url.endswith("/metrics"):
            content = "\n".join(
                (
                    "recommendation_requests_total 1",
                    "recommendation_request_duration_seconds_count 1",
                    "partner_config_upstream_requests_total 1",
                    "session_budget_reservations_total 1",
                )
            )
            return deployment_verifier.HttpResult(200, content.encode(), "text/plain")
        else:
            recommendation_calls += 1
            body = {
                "partner_id": "p1",
                "recommendations": (
                    [{"offer_type": "flight"}, {"offer_type": "hotel"}]
                    if recommendation_calls == 1
                    else [{"offer_type": "package"}]
                ),
                "audit": {"policy_source": "partner-config-service"},
            }
        return deployment_verifier.HttpResult(200, json.dumps(body).encode(), "application/json")

    monkeypatch.setattr(deployment_verifier, "request", fake_request)
    checks = deployment_verifier.verify("http://service", expected_cap=3)
    assert [check["result"] for check in checks] == ["pass"] * 5


def test_verifier_fails_if_cruise_policy_is_not_enforced(monkeypatch) -> None:
    def fake_request(method: str, url: str, payload=None):
        if url.endswith("/health"):
            body = {"status": "ok"}
        elif url.endswith("/ready"):
            body = {"status": "ready"}
        elif url.endswith("/metrics"):
            metrics = " ".join(
                (
                    "recommendation_requests_total",
                    "recommendation_request_duration_seconds",
                    "partner_config_upstream_requests_total",
                    "session_budget_reservations_total",
                )
            )
            return deployment_verifier.HttpResult(200, metrics.encode(), "text/plain")
        else:
            body = {
                "partner_id": "p1",
                "recommendations": [{"offer_type": "cruise"}],
                "audit": {"policy_source": "partner-config-service"},
            }
        return deployment_verifier.HttpResult(200, json.dumps(body).encode(), "application/json")

    monkeypatch.setattr(deployment_verifier, "request", fake_request)
    with pytest.raises(deployment_verifier.VerificationError, match="exclude_cruise"):
        deployment_verifier.verify("http://service")


def test_compose_and_runbook_preserve_state_and_immutable_selection() -> None:
    compose = (ROOT / "docker-compose.yml").read_text()
    runbook = (ROOT / "docs" / "operations" / "ROLLBACK_RUNBOOK.md").read_text()
    assert "${ARRIVIA_RECS_IMAGE:-arrivia-recs:local}" in compose
    assert "./.data:/app/.data" in compose
    assert "-wal" in runbook and "-shm" in runbook
    assert "--no-build" in runbook
    assert "only when integrity checks demonstrate corruption" in runbook


def test_alert_contract_contains_exact_thresholds() -> None:
    alerts = (ROOT / "docs" / "operations" / "alerts.yml").read_text()
    assert "for: 2m" in alerts
    assert "> 0.05" in alerts and ">= 50" in alerts
    assert "< 0.99" in alerts and ">= 20" in alerts
    assert 'dependency="partner_config",state="open"' in alerts
    assert "> 0.25" in alerts and "for: 10m" in alerts
    assert "[7d]" in alerts and ">= 0.05" in alerts and ">= 100" in alerts
