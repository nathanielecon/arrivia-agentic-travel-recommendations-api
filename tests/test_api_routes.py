"""HTTP route contracts for the FastAPI surface (health/readiness)."""

from fastapi.testclient import TestClient

from arrivia_recs.main import app


def test_health_and_ready_routes_registered() -> None:
    paths = {getattr(r, "path", None) for r in app.routes}
    assert "/health" in paths
    assert "/ready" in paths


def test_health_and_ready_response_contract() -> None:
    client = TestClient(app)
    assert client.get("/health").json() == {"status": "ok"}
    assert client.get("/ready").json() == {"status": "ready"}


def test_only_primary_recommendation_route_is_registered() -> None:
    paths = {getattr(r, "path", None) for r in app.routes}
    assert "/v1/recommendations" in paths
    assert "/v1/recommendations-orchestrator" not in paths
