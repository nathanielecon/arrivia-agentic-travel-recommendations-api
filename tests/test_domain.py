from datetime import date

import pytest
from pydantic import ValidationError

from arrivia_recs.domain import (
    Booking,
    BookingType,
    LoyaltyTier,
    Member,
    PartnerPolicy,
    PolicyRuleApplied,
    RecommendationAudit,
    RecommendationItem,
    RecommendationResponse,
)


def test_member_and_booking_round_trip() -> None:
    m = Member(
        member_id="m1",
        partner_id="p1",
        loyalty_tier=LoyaltyTier.GOLD,
        bookings=[
            Booking(
                destination="Tokyo",
                start_date=date(2025, 1, 10),
                end_date=date(2025, 1, 20),
                booking_type=BookingType.HOTEL,
            )
        ],
    )
    data = m.model_dump(mode="json")
    m2 = Member.model_validate(data)
    assert m2.member_id == "m1"
    assert m2.bookings[0].destination == "Tokyo"


def test_member_rejects_more_than_five_bookings() -> None:
    bookings = [
        Booking(
            destination=f"d{i}",
            start_date=date(2025, 1, 1),
            booking_type=BookingType.FLIGHT,
        )
        for i in range(6)
    ]
    with pytest.raises(ValidationError) as exc:
        Member(
            member_id="m1",
            partner_id="p1",
            loyalty_tier=LoyaltyTier.SILVER,
            bookings=bookings,
        )
    assert "at most 5" in str(exc.value).lower()


def test_partner_policy_cap_validation() -> None:
    PartnerPolicy(partner_id="p1", max_recommendations_per_session=3)
    PartnerPolicy(partner_id="p1", max_recommendations_per_session=None)
    with pytest.raises(ValidationError):
        PartnerPolicy(partner_id="p1", max_recommendations_per_session=-1)


def test_recommendation_response_includes_audit() -> None:
    audit = RecommendationAudit(
        partner_id="p1",
        policy_rules_applied=[
            PolicyRuleApplied(rule_code="SESSION_CAP", detail="capped at 3 for partner p1"),
        ],
        session_cap_applied=True,
        excluded_categories=["cruise"],
    )
    resp = RecommendationResponse(
        member_id="m1",
        partner_id="p1",
        items=[
            RecommendationItem(
                recommendation_type="hotel",
                title="Stay in Kyoto",
                destination="Kyoto",
            )
        ],
        audit=audit,
    )
    dumped = resp.model_dump(mode="json")
    assert dumped["audit"]["session_cap_applied"] is True
    assert dumped["audit"]["excluded_categories"] == ["cruise"]
    assert dumped["items"][0]["title"] == "Stay in Kyoto"
