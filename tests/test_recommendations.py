from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock

import httpx
import pytest
from fastapi.testclient import TestClient

from arrivia_recs.api.deps import get_recommendation_service
from arrivia_recs.domain.models import BookingRecord, MemberProfile, RecommendationRequest
from arrivia_recs.domain.partner_policy import PartnerPolicy
from arrivia_recs.integrations.member_client import MemberClient, MemberServiceError
from arrivia_recs.integrations.partner_config_client import (
    PartnerConfigClient,
    PartnerConfigError,
)
from arrivia_recs.main import app
from arrivia_recs.schemas.recommendations import (
    MemberProfile as OrchestratorMemberProfile,
)
from arrivia_recs.schemas.recommendations import (
    PartnerRules,
    TravelHistoryEntry,
)
from arrivia_recs.services.recommendation_orchestrator import RecommendationOrchestrator
from arrivia_recs.services.recommendations import RecommendationService
from arrivia_recs.services.session_budget import SessionRecommendationBudget


def _member_request(member_id: str) -> httpx.Request:
    return httpx.Request("GET", f"http://member-service/v1/members/{member_id}")


def _partner_request(partner_id: str) -> httpx.Request:
    return httpx.Request("GET", f"http://partner-service/v1/partners/{partner_id}/policy")


class _StubMember(MemberClient):
    def __init__(self, profile: MemberProfile | None, *, missing: bool = False) -> None:
        super().__init__("http://member-service")
        self._profile = profile
        self._missing = missing

    async def get_member(self, member_id: str) -> MemberProfile:
        if self._missing or member_id == "missing":
            raise httpx.HTTPStatusError(
                "not found",
                request=_member_request(member_id),
                response=httpx.Response(404, request=_member_request(member_id)),
            )
        assert self._profile is not None
        return self._profile


class _StubPartner(PartnerConfigClient):
    def __init__(self, policy: PartnerPolicy | None, *, missing: bool = False) -> None:
        super().__init__("http://partner-service")
        self._policy = policy
        self._missing = missing

    async def get_policy(self, partner_id: str) -> PartnerPolicy:
        if self._missing:
            raise httpx.HTTPStatusError(
                "not found",
                request=_partner_request(partner_id),
                response=httpx.Response(404, request=_partner_request(partner_id)),
            )
        assert self._policy is not None
        return self._policy


class _InvalidMember(MemberClient):
    def __init__(self) -> None:
        super().__init__("http://member-service")

    async def get_member(self, member_id: str) -> MemberProfile:
        raise MemberServiceError("member service returned invalid member payload")


class _InvalidPartner(PartnerConfigClient):
    def __init__(self) -> None:
        super().__init__("http://partner-service")

    async def get_policy(self, partner_id: str) -> PartnerPolicy:
        raise PartnerConfigError("partner config returned invalid policy payload")


@pytest.fixture
def client() -> TestClient:
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


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


def test_recommendations_returns_audit_and_items(client: TestClient) -> None:
    policy = PartnerPolicy(partner_id="p1", max_recommendations_per_session=None, exclude_cruise=False)
    service = RecommendationService(
        _StubMember(_sample_member()),
        _StubPartner(policy),
        session_counts={},
    )
    app.dependency_overrides[get_recommendation_service] = lambda: service

    response = client.post("/v1/recommendations", json={"member_id": "m1"})

    assert response.status_code == 200
    body = response.json()
    assert body["partner_id"] == "p1"
    assert body["member_id"] == "m1"
    assert len(body["recommendations"]) >= 1
    assert body["audit"]["policy_source"] == "partner-config-service"
    rules = {e["rule"]: e["value"] for e in body["audit"]["rules_applied"]}
    assert rules["exclude_cruise"] == "false"


def test_exclude_cruise_removes_cruise_offers(client: TestClient) -> None:
    policy = PartnerPolicy(partner_id="p1", max_recommendations_per_session=None, exclude_cruise=True)
    service = RecommendationService(
        _StubMember(_sample_member()),
        _StubPartner(policy),
        session_counts={},
    )
    app.dependency_overrides[get_recommendation_service] = lambda: service

    response = client.post("/v1/recommendations", json={"member_id": "m1"})
    assert response.status_code == 200
    types = {item["offer_type"] for item in response.json()["recommendations"]}
    assert "cruise" not in types


def test_session_cap_limits_across_calls(client: TestClient) -> None:
    policy = PartnerPolicy(partner_id="p1", max_recommendations_per_session=2, exclude_cruise=True)
    store: dict[tuple[str, str], int] = {}
    service = RecommendationService(
        _StubMember(_sample_member()),
        _StubPartner(policy),
        session_counts=store,
    )
    app.dependency_overrides[get_recommendation_service] = lambda: service

    first = client.post(
        "/v1/recommendations",
        json={"member_id": "m1", "session_id": "sess-a"},
    )
    assert first.status_code == 200
    assert len(first.json()["recommendations"]) == 2

    second = client.post(
        "/v1/recommendations",
        json={"member_id": "m1", "session_id": "sess-a"},
    )
    assert second.status_code == 200
    assert second.json()["recommendations"] == []


@pytest.mark.asyncio
async def test_service_budget_reservation_is_atomic() -> None:
    policy = PartnerPolicy(partner_id="p1", max_recommendations_per_session=1, exclude_cruise=False)
    service = RecommendationService(
        _StubMember(_sample_member()),
        _StubPartner(policy),
        session_counts={},
    )

    grants = await asyncio.gather(
        service._reserve_budget("p1", "sess-a", policy, requested=1),
        service._reserve_budget("p1", "sess-a", policy, requested=1),
    )

    assert sorted(grants) == [0, 1]


@pytest.mark.asyncio
async def test_primary_and_compatibility_services_can_share_session_budget() -> None:
    policy = PartnerPolicy(partner_id="p1", max_recommendations_per_session=1, exclude_cruise=False)
    budget = SessionRecommendationBudget()
    primary = RecommendationService(
        _StubMember(_sample_member()),
        _StubPartner(policy),
        session_budget=budget,
    )

    member = AsyncMock()
    member.get_member = AsyncMock(
        return_value=OrchestratorMemberProfile(
            member_id="m1",
            loyalty_tier="Gold",
            partner_id="p1",
            travel_history=[
                TravelHistoryEntry(
                    destination="Paris",
                    start_date="2024-01-01",
                    end_date="2024-01-05",
                    booking_type="flight",
                )
            ],
        )
    )
    partner = AsyncMock()
    partner.get_rules = AsyncMock(
        return_value=PartnerRules(partner_id="p1", max_recommendations_per_session=1)
    )
    compatibility = RecommendationOrchestrator(member, partner, budget)

    first = await primary.recommend(RecommendationRequest(member_id="m1", session_id="shared"))
    second = await compatibility.recommend("m1", session_id="shared")

    assert len(first.recommendations) == 1
    assert len(second.recommendations) == 0


def test_member_not_found_returns_404(client: TestClient) -> None:
    policy = PartnerPolicy(partner_id="p1")
    service = RecommendationService(
        _StubMember(None, missing=True),
        _StubPartner(policy),
        session_counts={},
    )
    app.dependency_overrides[get_recommendation_service] = lambda: service

    response = client.post("/v1/recommendations", json={"member_id": "missing"})
    assert response.status_code == 404
    assert response.json()["detail"] == "member_not_found"


def test_partner_policy_missing_returns_502(client: TestClient) -> None:
    service = RecommendationService(
        _StubMember(_sample_member()),
        _StubPartner(None, missing=True),
        session_counts={},
    )
    app.dependency_overrides[get_recommendation_service] = lambda: service

    response = client.post("/v1/recommendations", json={"member_id": "m1"})
    assert response.status_code == 502
    assert response.json()["detail"] == "partner_policy_not_found"


def test_invalid_member_payload_returns_502(client: TestClient) -> None:
    service = RecommendationService(
        _InvalidMember(),
        _StubPartner(PartnerPolicy(partner_id="p1")),
        session_counts={},
    )
    app.dependency_overrides[get_recommendation_service] = lambda: service

    response = client.post("/v1/recommendations", json={"member_id": "m1"})
    assert response.status_code == 502
    assert response.json()["detail"] == "upstream_invalid_payload"


def test_invalid_partner_payload_returns_502(client: TestClient) -> None:
    service = RecommendationService(
        _StubMember(_sample_member()),
        _InvalidPartner(),
        session_counts={},
    )
    app.dependency_overrides[get_recommendation_service] = lambda: service

    response = client.post("/v1/recommendations", json={"member_id": "m1"})
    assert response.status_code == 502
    assert response.json()["detail"] == "upstream_invalid_payload"
