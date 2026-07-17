from __future__ import annotations

import json

import httpx
import pytest
from fastapi.testclient import TestClient

from arrivia_recs.api.deps import get_recommendation_service
from arrivia_recs.domain.models import BookingRecord, MemberProfile
from arrivia_recs.integrations.circuit_breaker import AsyncCircuitBreaker, CircuitState
from arrivia_recs.integrations.member_client import MemberClient, MemberServiceError
from arrivia_recs.integrations.partner_config_client import (
    PartnerConfigClient,
    PartnerConfigError,
)
from arrivia_recs.main import app
from arrivia_recs.mcp import server as mcp_server
from arrivia_recs.services.recommendations import RecommendationService


@pytest.mark.asyncio
async def test_owned_member_client_reuses_and_closes_one_http_pool(monkeypatch) -> None:
    instances = []

    class FakeClient:
        def __init__(self, **_kwargs) -> None:
            self.calls = 0
            self.closed = False
            instances.append(self)

        async def get(self, _path: str, **_kwargs) -> httpx.Response:
            self.calls += 1
            return httpx.Response(200, json=_member_payload())

        async def aclose(self) -> None:
            self.closed = True

    monkeypatch.setattr("arrivia_recs.integrations.member_client.httpx.AsyncClient", FakeClient)
    client = MemberClient("http://member")

    await client.get_member("m1")
    await client.get_member("m1")
    await client.aclose()

    assert len(instances) == 1
    assert instances[0].calls == 2
    assert instances[0].closed is True


@pytest.mark.asyncio
async def test_owned_partner_client_reuses_and_closes_one_http_pool(monkeypatch) -> None:
    instances = []

    class FakeClient:
        def __init__(self, **_kwargs) -> None:
            self.calls = 0
            self.closed = False
            instances.append(self)

        async def get(self, _path: str, **_kwargs) -> httpx.Response:
            self.calls += 1
            return httpx.Response(200, json=_policy_payload())

        async def aclose(self) -> None:
            self.closed = True

    monkeypatch.setattr(
        "arrivia_recs.integrations.partner_config_client.httpx.AsyncClient", FakeClient
    )
    client = PartnerConfigClient("http://partner")

    await client.get_policy("p1")
    await client.get_policy("p1")
    await client.aclose()

    assert len(instances) == 1
    assert instances[0].calls == 2
    assert instances[0].closed is True
def _member_payload() -> dict[str, object]:
    return {
        "member_id": "m1",
        "partner_id": "p1",
        "loyalty_tier": "Gold",
        "bookings": [],
    }


def _policy_payload() -> dict[str, object]:
    return {
        "partner_id": "p1",
        "max_recommendations_per_session": None,
        "exclude_cruise": False,
    }


@pytest.mark.asyncio
async def test_injected_clients_receive_frozen_timeout_budget() -> None:
    observed: list[dict[str, float]] = []

    def handler(request: httpx.Request) -> httpx.Response:
        observed.append(request.extensions["timeout"])
        if request.url.path.startswith("/members/"):
            return httpx.Response(200, json=_member_payload())
        return httpx.Response(200, json=_policy_payload())

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport, base_url="http://upstream") as client:
        await MemberClient("http://member", client=client).get_member("m1")
        await PartnerConfigClient("http://partner", client=client).get_policy("p1")

    assert observed == [
        {"connect": 0.25, "read": 1.0, "write": 0.25, "pool": 0.25},
        {"connect": 0.25, "read": 1.0, "write": 0.25, "pool": 0.25},
    ]


@pytest.mark.asyncio
@pytest.mark.parametrize("status", [429, 500, 503])
async def test_qualifying_http_failures_open_without_retry(status: int) -> None:
    calls = 0

    def handler(_request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return httpx.Response(status)

    circuit = AsyncCircuitBreaker("member", failure_threshold=3, open_seconds=30)
    async with httpx.AsyncClient(
        transport=httpx.MockTransport(handler), base_url="http://member"
    ) as client:
        member = MemberClient("http://member", client=client, circuit=circuit)
        for _ in range(3):
            with pytest.raises(MemberServiceError, match=f"HTTP {status}"):
                await member.get_member("m1")
        with pytest.raises(MemberServiceError) as opened:
            await member.get_member("m1")

    assert opened.value.code == "upstream_circuit_open"
    assert circuit.state is CircuitState.OPEN
    assert calls == 3


@pytest.mark.asyncio
async def test_member_404_does_not_count_toward_circuit() -> None:
    circuit = AsyncCircuitBreaker("member", failure_threshold=1, open_seconds=30)
    async with httpx.AsyncClient(
        transport=httpx.MockTransport(lambda _request: httpx.Response(404)),
        base_url="http://member",
    ) as client:
        member = MemberClient("http://member", client=client, circuit=circuit)
        with pytest.raises(MemberServiceError) as missing:
            await member.get_member("missing")

    assert missing.value.code == "member_not_found"
    assert circuit.state is CircuitState.CLOSED
    assert circuit.consecutive_failures == 0


@pytest.mark.asyncio
async def test_invalid_policy_payload_qualifies_and_unknown_rule_fails_closed() -> None:
    circuit = AsyncCircuitBreaker("partner_config", failure_threshold=1, open_seconds=30)
    payload = {**_policy_payload(), "new_restriction": True}
    async with httpx.AsyncClient(
        transport=httpx.MockTransport(lambda _request: httpx.Response(200, json=payload)),
        base_url="http://partner",
    ) as client:
        partner = PartnerConfigClient("http://partner", client=client, circuit=circuit)
        with pytest.raises(PartnerConfigError) as invalid:
            await partner.get_policy("p1")

    assert invalid.value.code == "upstream_invalid_payload"
    assert circuit.state is CircuitState.OPEN


@pytest.mark.asyncio
async def test_partner_identity_mismatch_fails_closed() -> None:
    circuit = AsyncCircuitBreaker("partner_config", failure_threshold=1, open_seconds=30)
    payload = {**_policy_payload(), "partner_id": "another-partner"}
    async with httpx.AsyncClient(
        transport=httpx.MockTransport(lambda _request: httpx.Response(200, json=payload)),
        base_url="http://partner",
    ) as client:
        partner = PartnerConfigClient("http://partner", client=client, circuit=circuit)
        with pytest.raises(PartnerConfigError) as invalid:
            await partner.get_policy("p1")

    assert invalid.value.code == "upstream_invalid_payload"
    assert circuit.state is CircuitState.OPEN


@pytest.mark.asyncio
async def test_timeout_is_classified_and_not_retried() -> None:
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        raise httpx.ReadTimeout("controlled timeout", request=request)

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(handler), base_url="http://member"
    ) as client:
        member = MemberClient("http://member", client=client)
        with pytest.raises(MemberServiceError) as timed_out:
            await member.get_member("m1")

    assert timed_out.value.code == "upstream_timeout"
    assert calls == 1


class _HealthyMember(MemberClient):
    def __init__(self) -> None:
        super().__init__("http://member")

    async def get_member(self, member_id: str) -> MemberProfile:
        return MemberProfile(
            member_id=member_id,
            partner_id="p1",
            loyalty_tier="Gold",
            bookings=[
                BookingRecord(
                    destination="Paris",
                    start_date="2024-01-01",
                    end_date="2024-01-02",
                    booking_type="hotel",
                )
            ],
        )


class _OpenPartner(PartnerConfigClient):
    def __init__(self) -> None:
        super().__init__("http://partner")

    async def get_policy(self, partner_id: str):  # noqa: ANN201
        raise PartnerConfigError(
            "partner_config circuit is open",
            status_code=502,
            code="upstream_circuit_open",
        )


def test_rest_translates_open_circuit_to_stable_502() -> None:
    service = RecommendationService(_HealthyMember(), _OpenPartner(), session_counts={})
    app.dependency_overrides[get_recommendation_service] = lambda: service
    try:
        with TestClient(app) as client:
            response = client.post("/v1/recommendations", json={"member_id": "m1"})
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 502
    assert response.json() == {"detail": "upstream_circuit_open"}


@pytest.mark.asyncio
async def test_mcp_translates_open_circuit_to_stable_json(monkeypatch: pytest.MonkeyPatch) -> None:
    service = RecommendationService(_HealthyMember(), _OpenPartner(), session_counts={})
    monkeypatch.setattr(mcp_server, "get_recommendation_service_mcp", lambda: service)

    content, _meta = await mcp_server.mcp.call_tool(
        "get_travel_recommendations", {"member_id": "m1"}
    )
    payload = json.loads(content[0].text)

    assert payload["error"] == "upstream_circuit_open"
    assert payload["member_id"] == "m1"
