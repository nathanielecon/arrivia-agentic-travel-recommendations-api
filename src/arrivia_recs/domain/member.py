from datetime import date

from pydantic import BaseModel, Field, field_validator

from arrivia_recs.domain.enums import BookingType, LoyaltyTier


class Booking(BaseModel):
    """A single historical booking in member context (member service shape)."""

    destination: str
    start_date: date
    end_date: date | None = None
    booking_type: BookingType


class Member(BaseModel):
    """Member profile and recent travel history for personalization."""

    member_id: str
    partner_id: str
    loyalty_tier: LoyaltyTier
    bookings: list[Booking] = Field(default_factory=list)

    @field_validator("bookings")
    @classmethod
    def at_most_five_bookings(cls, v: list[Booking]) -> list[Booking]:
        if len(v) > 5:
            raise ValueError("at most 5 bookings are retained in member context")
        return v
