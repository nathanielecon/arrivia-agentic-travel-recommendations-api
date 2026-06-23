"""MCP smoke tests: tool registration and a stubbed recommendation call path."""

from __future__ import annotations

import json

import pytest

from arrivia_recs.domain.models import (
    BookingRecord,
    MemberProfile,
    PartnerPolicy,
)
from arrivia_recs.integrations.member_client import MemberClient, MemberServiceError
from arrivia_recs.integrations.partner_config_client import (
    PartnerConfigClient,
    PartnerConfigError,
)
from arrivia_recs.mcp import server as mcp_server
from arrivia_recs.services.recommendations import RecommendationService


class _StubMember(MemberClient):
    def __init__(self, profile: MemberProfile | None, *, missing: bool = False) -> None:
        super().__init__("http://member-service")
        self._profile = profile
        self._missing = missing

    async def get_member(self, member_id: str) -> MemberProfile:
        if self._missing or member_id == "missing":
            raise MemberServiceError("member not found", status_code=404, code="member_not_found")
        assert self._profile is not None
        return self._profile


class _StubPartner(PartnerConfigClient):
    def __init__(self, policy: PartnerPolicy | None, *, missing: bool = False) -> None:
        super().__init__("http://partner-service")
        self._policy = policy
        self._missing = missing

    async def get_policy(self, partner_id: str) -> PartnerPolicy:
        if self._missing:
            raise PartnerConfigError(
                "partner policy not found",
                status_code=404,
                code="partner_policy_not_found",
            )
        assert self._policy is not None
        return self._policy


def _sample_member() -> MemberProfile:
    return MemberProfile(
        member_id="m1",
        partner_id="p1",
        loyalty_tier="Gold",
        bookings=[
            BookingRecord(
                destination="Paris",
                start_date="2024-01-01",
                end_date="2024-01-10",
                booking_type="hotel",
            )
        ],
    )


@pytest.mark.asyncio
async def test_mcp_registers_get_travel_recommendations_tool() -> None:
    tools = await mcp_server.mcp.list_tools()
    names = {t.name for t in tools}
    assert "get_travel_recommendations" in names
    tool = next(t for t in tools if t.name == "get_travel_recommendations")
    assert tool.description
    assert "member_id" in tool.inputSchema.get("properties", {})
    assert "session_id" in tool.inputSchema.get("properties", {})


@pytest.mark.asyncio
async def test_mcp_tool_returns_recommendations_json(monkeypatch: pytest.MonkeyPatch) -> None:
    policy = PartnerPolicy(partner_id="p1", max_recommendations_per_session=None, exclude_cruise=False)
    service = RecommendationService(
        _StubMember(_sample_member()),
        _StubPartner(policy),
        session_counts={},
    )
    monkeypatch.setattr(mcp_server, "get_recommendation_service_mcp", lambda: service)

    content, meta = await mcp_server.mcp.call_tool(
        "get_travel_recommendations",
        {"member_id": "m1"},
    )
    assert content
    text = content[0].text
    body = json.loads(text)
    assert body["partner_id"] == "p1"
    assert body["member_id"] == "m1"
    assert body["audit"]["policy_source"] == "partner-config-service"
    assert len(body["recommendations"]) >= 1
    assert "result" in meta


@pytest.mark.asyncio
async def test_mcp_tool_member_not_found(monkeypatch: pytest.MonkeyPatch) -> None:
    policy = PartnerPolicy(partner_id="p1", max_recommendations_per_session=None, exclude_cruise=False)
    service = RecommendationService(
        _StubMember(_sample_member(), missing=True),
        _StubPartner(policy),
        session_counts={},
    )
    monkeypatch.setattr(mcp_server, "get_recommendation_service_mcp", lambda: service)

    content, _meta = await mcp_server.mcp.call_tool(
        "get_travel_recommendations",
        {"member_id": "missing"},
    )
    err = json.loads(content[0].text)
    assert err["error"] == "member_not_found"


class _InvalidPartner(PartnerConfigClient):
    def __init__(self) -> None:
        super().__init__("http://partner-service")

    async def get_policy(self, partner_id: str) -> PartnerPolicy:
        raise PartnerConfigError(
            "partner config returned invalid policy payload",
            status_code=502,
            code="upstream_invalid_payload",
        )


@pytest.mark.asyncio
async def test_mcp_tool_invalid_payload_is_explicit(monkeypatch: pytest.MonkeyPatch) -> None:
    service = RecommendationService(
        _StubMember(_sample_member()),
        _InvalidPartner(),
        session_counts={},
    )
    monkeypatch.setattr(mcp_server, "get_recommendation_service_mcp", lambda: service)

    content, _meta = await mcp_server.mcp.call_tool(
        "get_travel_recommendations",
        {"member_id": "m1"},
    )

    err = json.loads(content[0].text)
    assert err["error"] == "upstream_invalid_payload"
