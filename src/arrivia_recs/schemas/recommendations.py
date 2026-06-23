from pydantic import BaseModel, Field, field_validator


class TravelHistoryEntry(BaseModel):
    destination: str
    start_date: str
    end_date: str
    booking_type: str


class MemberProfile(BaseModel):
    member_id: str
    loyalty_tier: str
    partner_id: str
    travel_history: list[TravelHistoryEntry] = Field(default_factory=list)


class PartnerRules(BaseModel):
    partner_id: str
    max_recommendations_per_session: int | None = None
    exclude_cruise: bool = False

    @field_validator("max_recommendations_per_session")
    @classmethod
    def non_negative_cap(cls, value: int | None) -> int | None:
        if value is not None and value < 0:
            raise ValueError("max_recommendations_per_session must be non-negative")
        return value


class RecommendationItem(BaseModel):
    destination: str
    booking_type: str
    rationale: str


class PolicyAuditEntry(BaseModel):
    rule: str
    partner_id: str
    source: str = "partner_config"
    detail: str


class RecommendationRequest(BaseModel):
    member_id: str = Field(min_length=1)
    session_id: str | None = None


class RecommendationResponse(BaseModel):
    member_id: str
    partner_id: str
    loyalty_tier: str
    recommendations: list[RecommendationItem]
    policy_audit: list[PolicyAuditEntry]
