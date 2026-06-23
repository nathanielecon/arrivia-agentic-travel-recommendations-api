"""Domain models for recommendations and canonical domain types."""

from arrivia_recs.domain.enums import BookingType, LoyaltyTier
from arrivia_recs.domain.member import Booking, Member
from arrivia_recs.domain.models import (
    BookingRecord,
    MemberContext,
    MemberProfile,
    RecommendationRequest,
    RecommendationResult,
    TravelBooking,
)
from arrivia_recs.domain.partner_policy import PartnerPolicy
from arrivia_recs.domain.recommendation import (
    PolicyRuleApplied,
    RecommendationAudit,
    RecommendationItem,
    RecommendationResponse,
)

__all__ = [
    "Booking",
    "BookingRecord",
    "BookingType",
    "LoyaltyTier",
    "Member",
    "MemberContext",
    "MemberProfile",
    "PartnerPolicy",
    "PolicyRuleApplied",
    "RecommendationAudit",
    "RecommendationItem",
    "RecommendationRequest",
    "RecommendationResponse",
    "RecommendationResult",
    "TravelBooking",
]
