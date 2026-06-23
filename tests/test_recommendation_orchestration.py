import asyncio
from unittest.mock import AsyncMock

import pytest

from arrivia_recs.integrations.http_clients import MemberServiceError, PartnerConfigError
from arrivia_recs.schemas.recommendations import (
    MemberProfile,
    PartnerRules,
    TravelHistoryEntry,
)
from arrivia_recs.services.recommendation_orchestrator import (
    RecommendationOrchestrator,
    SessionRecommendationBudget,
)


def _sample_member(*, cruise: bool = True) -> MemberProfile:
    history = [
        TravelHistoryEntry(
            destination="Paris",
            start_date="2024-01-01",
            end_date="2024-01-05",
            booking_type="flight",
        ),
        TravelHistoryEntry(
            destination="Miami",
            start_date="2024-02-01",
            end_date="2024-02-08",
            booking_type="cruise",
        ),
        TravelHistoryEntry(
            destination="Denver",
            start_date="2024-03-01",
            end_date="2024-03-03",
            booking_type="flight",
        ),
    ]
    if not cruise:
        history = [h for h in history if h.booking_type != "cruise"]
    return MemberProfile(
        member_id="m1",
        loyalty_tier="Gold",
        partner_id="p1",
        travel_history=history,
    )


@pytest.mark.asyncio
async def test_orchestrator_unlimited() -> None:
    member = AsyncMock()
    member.get_member = AsyncMock(return_value=_sample_member())
    partner = AsyncMock()
    partner.get_rules = AsyncMock(
        return_value=PartnerRules(partner_id="p1", max_recommendations_per_session=None)
    )
    orch = RecommendationOrchestrator(member, partner, SessionRecommendationBudget())
    result = await orch.recommend("m1", session_id=None)
    assert len(result.recommendations) == 3
    assert any(a.rule == "max_recommendations_per_session" for a in result.policy_audit)


@pytest.mark.asyncio
async def test_orchestrator_excludes_cruise() -> None:
    member = AsyncMock()
    member.get_member = AsyncMock(return_value=_sample_member())
    partner = AsyncMock()
    partner.get_rules = AsyncMock(
        return_value=PartnerRules(
            partner_id="p1",
            max_recommendations_per_session=None,
            exclude_cruise=True,
        )
    )
    orch = RecommendationOrchestrator(member, partner, SessionRecommendationBudget())
    result = await orch.recommend("m1", session_id=None)
    assert len(result.recommendations) == 2
    assert all(r.booking_type.lower() != "cruise" for r in result.recommendations)
    assert any(a.rule == "exclude_cruise" for a in result.policy_audit)


@pytest.mark.asyncio
async def test_orchestrator_per_request_cap_without_session() -> None:
    member = AsyncMock()
    member.get_member = AsyncMock(return_value=_sample_member())
    partner = AsyncMock()
    partner.get_rules = AsyncMock(
        return_value=PartnerRules(partner_id="p1", max_recommendations_per_session=2)
    )
    orch = RecommendationOrchestrator(member, partner, SessionRecommendationBudget())
    result = await orch.recommend("m1", session_id=None)
    assert len(result.recommendations) == 2


@pytest.mark.asyncio
async def test_orchestrator_session_cap_accumulates() -> None:
    member = AsyncMock()
    member.get_member = AsyncMock(return_value=_sample_member())
    partner = AsyncMock()
    partner.get_rules = AsyncMock(
        return_value=PartnerRules(partner_id="p1", max_recommendations_per_session=2)
    )
    budget = SessionRecommendationBudget()
    orch = RecommendationOrchestrator(member, partner, budget)
    first = await orch.recommend("m1", session_id="sess-a")
    second = await orch.recommend("m1", session_id="sess-a")
    assert len(first.recommendations) == 2
    assert len(second.recommendations) == 0


@pytest.mark.asyncio
async def test_orchestrator_session_cap_is_isolated_per_partner() -> None:
    member_a = AsyncMock()
    member_a.get_member = AsyncMock(return_value=_sample_member())
    member_b = AsyncMock()
    member_b.get_member = AsyncMock(
        return_value=_sample_member().model_copy(update={"partner_id": "p2"})
    )
    partner_a = AsyncMock()
    partner_a.get_rules = AsyncMock(
        return_value=PartnerRules(partner_id="p1", max_recommendations_per_session=1)
    )
    partner_b = AsyncMock()
    partner_b.get_rules = AsyncMock(
        return_value=PartnerRules(partner_id="p2", max_recommendations_per_session=1)
    )

    budget = SessionRecommendationBudget()
    orch_a = RecommendationOrchestrator(member_a, partner_a, budget)
    orch_b = RecommendationOrchestrator(member_b, partner_b, budget)

    first = await orch_a.recommend("m1", session_id="shared")
    second = await orch_b.recommend("m1", session_id="shared")

    assert len(first.recommendations) == 1
    assert len(second.recommendations) == 1


@pytest.mark.asyncio
async def test_orchestrator_session_cap_reservation_is_atomic() -> None:
    member = AsyncMock()
    member.get_member = AsyncMock(return_value=_sample_member())
    partner = AsyncMock()
    partner.get_rules = AsyncMock(
        return_value=PartnerRules(partner_id="p1", max_recommendations_per_session=1)
    )
    budget = SessionRecommendationBudget()
    orch = RecommendationOrchestrator(member, partner, budget)

    first, second = await asyncio.gather(
        orch.recommend("m1", session_id="sess-a"),
        orch.recommend("m1", session_id="sess-a"),
    )

    lengths = sorted([len(first.recommendations), len(second.recommendations)])
    assert lengths == [0, 1]


@pytest.mark.asyncio
async def test_orchestrator_returns_expected_response_shape() -> None:
    member = AsyncMock()
    member.get_member = AsyncMock(return_value=_sample_member(cruise=False))
    partner = AsyncMock()
    partner.get_rules = AsyncMock(
        return_value=PartnerRules(partner_id="p1", max_recommendations_per_session=10)
    )
    orch = RecommendationOrchestrator(member, partner, SessionRecommendationBudget())
    result = await orch.recommend("m1", session_id=None)
    assert result.member_id == "m1"
    assert result.partner_id == "p1"
    assert len(result.recommendations) == 2
    assert all(a.partner_id == "p1" for a in result.policy_audit)


@pytest.mark.asyncio
async def test_member_not_found() -> None:
    member = AsyncMock()
    member.get_member = AsyncMock(side_effect=MemberServiceError("x", status_code=404))
    partner = AsyncMock()
    partner.get_rules = AsyncMock(return_value=PartnerRules(partner_id="p1"))
    orch = RecommendationOrchestrator(member, partner, SessionRecommendationBudget())
    with pytest.raises(MemberServiceError):
        await orch.recommend("missing", session_id=None)


@pytest.mark.asyncio
async def test_partner_unavailable() -> None:
    member = AsyncMock()
    member.get_member = AsyncMock(return_value=_sample_member(cruise=False))
    partner = AsyncMock()
    partner.get_rules = AsyncMock(side_effect=PartnerConfigError("down"))
    orch = RecommendationOrchestrator(member, partner, SessionRecommendationBudget())
    with pytest.raises(PartnerConfigError):
        await orch.recommend("m1", session_id=None)
