from __future__ import annotations

from pydantic import BaseModel, Field, computed_field, model_validator

from arrivia_recs.domain.partner_policy import PartnerPolicy  # noqa: F401


class TravelBooking(BaseModel):
    destination: str
    start_date: str
    booking_type: str


class MemberContext(BaseModel):
    member_id: str
    partner_id: str
    loyalty_tier: str
    travel_history: list[TravelBooking] = Field(default_factory=list)


class BookingRecord(BaseModel):
    destination: str
    start_date: str
    end_date: str
    booking_type: str


class MemberProfile(BaseModel):
    member_id: str
    partner_id: str
    loyalty_tier: str
    bookings: list[BookingRecord] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def _bookings_from_travel_history(cls, data: object) -> object:
        if not isinstance(data, dict):
            return data
        if data.get("bookings"):
            return data
        travel_history = data.get("travel_history")
        if not travel_history:
            return data
        bookings: list[dict[str, str]] = []
        for row in travel_history:
            start = str(row.get("start_date", ""))
            bookings.append(
                {
                    "destination": str(row["destination"]),
                    "start_date": start,
                    "end_date": str(row.get("end_date") or start),
                    "booking_type": str(row["booking_type"]),
                }
            )
        merged = {**data, "bookings": bookings}
        merged.pop("travel_history", None)
        return merged

    @computed_field
    @property
    def travel_history(self) -> list[TravelBooking]:
        return [
            TravelBooking(
                destination=b.destination,
                start_date=b.start_date,
                booking_type=b.booking_type,
            )
            for b in self.bookings
        ]


class RecommendationItem(BaseModel):
    id: str
    title: str
    offer_type: str
    rationale: str = ""


class RecommendationResult(BaseModel):
    items: list[RecommendationItem]
    audit: dict[str, object]


class PolicyAuditEntry(BaseModel):
    rule: str
    value: str


class ApiRecommendationAudit(BaseModel):
    """Structured audit block returned by the HTTP recommendations API."""

    partner_id: str
    policy_source: str
    rules_applied: list[PolicyAuditEntry]


class RecommendationRequest(BaseModel):
    member_id: str = Field(min_length=1)
    session_id: str | None = Field(
        default=None,
        description="When set and partner policy caps per session, counts apply across calls.",
    )


class RecommendationResponse(BaseModel):
    partner_id: str
    member_id: str
    recommendations: list[RecommendationItem]
    audit: ApiRecommendationAudit
