"""Domain models for upstream member and partner configuration payloads."""

from datetime import date
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class TravelBooking(BaseModel):
    destination: str
    start_date: date
    end_date: date
    booking_type: str


class MemberProfile(BaseModel):
    """Read-only member snapshot from the member data service."""

    member_id: str
    partner_id: str
    loyalty_tier: Literal["Silver", "Gold", "Platinum"]
    travel_history: list[TravelBooking] = Field(default_factory=list, max_length=5)


class PartnerRules(BaseModel):
    """Read-only partner policy from the partner configuration service."""

    partner_id: str
    max_recommendations_per_session: int | None = None
    exclude_cruise_offers: bool = False

    @field_validator("max_recommendations_per_session")
    @classmethod
    def non_negative_cap(cls, v: int | None) -> int | None:
        if v is not None and v < 0:
            msg = "max_recommendations_per_session must be non-negative"
            raise ValueError(msg)
        return v
