"""HTTP route contracts for the FastAPI surface (health/readiness)."""

from fastapi.testclient import TestClient

from arrivia_recs.main import app


def test_health_and_ready_routes_registered() -> None:
    # Assert the public contract rather than FastAPI's internal router representation.
    # Newer FastAPI releases retain included routers lazily in ``app.routes``.
    paths = set(app.openapi()["paths"])
    assert "/health" in paths
    assert "/ready" in paths


def test_health_and_ready_response_contract() -> None:
    client = TestClient(app)
    assert client.get("/health").json() == {"status": "ok"}
    assert client.get("/ready").json() == {"status": "ready"}


def test_only_primary_recommendation_route_is_registered() -> None:
    paths = set(app.openapi()["paths"])
    assert "/v1/recommendations" in paths
    assert "/v1/recommendations-orchestrator" not in paths
