"""Tests for read-only upstream HTTP adapters (member + partner config)."""

import httpx
import pytest
from httpx import Request, Response

from arrivia_recs.integrations import (
    MemberAdapter,
    MemberNotFoundError,
    PartnerConfigAdapter,
    PartnerRulesNotFoundError,
    UpstreamResponseError,
    UpstreamTransportError,
)
from arrivia_recs.integrations.models import PartnerRules

_MEMBER_JSON = {
    "member_id": "m-1",
    "partner_id": "p-9",
    "loyalty_tier": "Gold",
    "travel_history": [
        {
            "destination": "NYC",
            "start_date": "2025-01-01",
            "end_date": "2025-01-05",
            "booking_type": "hotel",
        }
    ],
}

_PARTNER_JSON = {
    "partner_id": "p-9",
    "max_recommendations_per_session": 3,
    "exclude_cruise_offers": True,
}


def _member_handler(request: Request) -> Response:
    if request.method != "GET":
        return Response(405)
    path = request.url.path
    if path == "/members/m-1":
        return Response(200, json=_MEMBER_JSON)
    if path == "/members/missing":
        return Response(404, text="not found")
    if path == "/members/bad-json":
        return Response(200, text="not json")
    if path == "/members/invalid-schema":
        return Response(200, json={"member_id": "x"})
    if path == "/members/503":
        return Response(503, text="upstream unavailable")
    return Response(404)


def _partner_handler(request: Request) -> Response:
    if request.method != "GET":
        return Response(405)
    path = request.url.path
    if path == "/partners/p-9/rules":
        return Response(200, json=_PARTNER_JSON)
    if path == "/partners/missing/rules":
        return Response(404)
    if path == "/partners/bad-json/rules":
        return Response(200, text="{")
    if path == "/partners/invalid/rules":
        return Response(200, json={"partner_id": "x", "max_recommendations_per_session": -1})
    return Response(404)


@pytest.mark.asyncio
async def test_member_adapter_returns_profile() -> None:
    transport = httpx.MockTransport(_member_handler)
    async with httpx.AsyncClient(transport=transport) as client:
        adapter = MemberAdapter("http://example.test", client=client)
        profile = await adapter.get_member("m-1")
    assert profile.member_id == "m-1"
    assert profile.partner_id == "p-9"
    assert profile.loyalty_tier == "Gold"
    assert len(profile.travel_history) == 1
    assert profile.travel_history[0].destination == "NYC"


@pytest.mark.asyncio
async def test_member_adapter_404_is_member_not_found() -> None:
    transport = httpx.MockTransport(_member_handler)
    async with httpx.AsyncClient(transport=transport) as client:
        adapter = MemberAdapter("http://example.test", client=client)
        with pytest.raises(MemberNotFoundError) as exc_info:
            await adapter.get_member("missing")
        assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_member_adapter_non_200_raises() -> None:
    transport = httpx.MockTransport(_member_handler)
    async with httpx.AsyncClient(transport=transport) as client:
        adapter = MemberAdapter("http://example.test", client=client)
        with pytest.raises(UpstreamResponseError) as exc_info:
            await adapter.get_member("503")
        assert exc_info.value.status_code == 503


@pytest.mark.asyncio
async def test_member_adapter_invalid_json_raises() -> None:
    transport = httpx.MockTransport(_member_handler)
    async with httpx.AsyncClient(transport=transport) as client:
        adapter = MemberAdapter("http://example.test", client=client)
        with pytest.raises(UpstreamResponseError) as exc_info:
            await adapter.get_member("bad-json")
        assert "validation" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_member_adapter_invalid_schema_raises() -> None:
    transport = httpx.MockTransport(_member_handler)
    async with httpx.AsyncClient(transport=transport) as client:
        adapter = MemberAdapter("http://example.test", client=client)
        with pytest.raises(UpstreamResponseError):
            await adapter.get_member("invalid-schema")


@pytest.mark.asyncio
async def test_member_adapter_encodes_path() -> None:
    calls: list[str] = []

    def handler(request: Request) -> Response:
        calls.append(request.url.raw_path.decode("ascii"))
        return Response(200, json={**_MEMBER_JSON, "member_id": "a/b"})

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport) as client:
        adapter = MemberAdapter("http://example.test", client=client)
        await adapter.get_member("a/b")
    assert calls == ["/members/a%2Fb"], "path segments must be percent-encoded for safe proxying"


@pytest.mark.asyncio
async def test_partner_adapter_returns_rules() -> None:
    transport = httpx.MockTransport(_partner_handler)
    async with httpx.AsyncClient(transport=transport) as client:
        adapter = PartnerConfigAdapter("http://example.test", client=client)
        rules = await adapter.get_rules("p-9")
    assert rules.partner_id == "p-9"
    assert rules.max_recommendations_per_session == 3
    assert rules.exclude_cruise_offers is True


@pytest.mark.asyncio
async def test_partner_adapter_404_is_not_found() -> None:
    transport = httpx.MockTransport(_partner_handler)
    async with httpx.AsyncClient(transport=transport) as client:
        adapter = PartnerConfigAdapter("http://example.test", client=client)
        with pytest.raises(PartnerRulesNotFoundError) as exc_info:
            await adapter.get_rules("missing")
        assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_partner_adapter_validation_failure() -> None:
    transport = httpx.MockTransport(_partner_handler)
    async with httpx.AsyncClient(transport=transport) as client:
        adapter = PartnerConfigAdapter("http://example.test", client=client)
        with pytest.raises(UpstreamResponseError):
            await adapter.get_rules("invalid")


@pytest.mark.asyncio
async def test_transport_error_when_no_response(monkeypatch: pytest.MonkeyPatch) -> None:
    transport = httpx.MockTransport(_member_handler)

    async def boom(*_a, **_k):
        raise httpx.ConnectError("simulated", request=None)

    async with httpx.AsyncClient(transport=transport) as client:
        monkeypatch.setattr(client, "get", boom)
        adapter = MemberAdapter("http://example.test", client=client)
        with pytest.raises(UpstreamTransportError):
            await adapter.get_member("m-1")


def test_partner_rules_rejects_negative_cap() -> None:
    with pytest.raises(ValueError):
        PartnerRules(partner_id="x", max_recommendations_per_session=-1)
