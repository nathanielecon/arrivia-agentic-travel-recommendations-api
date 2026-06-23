from pydantic import BaseModel, Field


class PolicyRuleApplied(BaseModel):
    """Single auditable record of a partner rule that influenced output."""

    rule_code: str
    detail: str


class RecommendationItem(BaseModel):
    """One concrete recommendation offered to the member."""

    recommendation_type: str
    title: str
    destination: str | None = None


class RecommendationAudit(BaseModel):
    """Structured trace for multi-tenant auditing: which partner rules shaped the response."""

    partner_id: str
    policy_rules_applied: list[PolicyRuleApplied] = Field(default_factory=list)
    session_cap_applied: bool = False
    excluded_categories: list[str] = Field(default_factory=list)


class RecommendationResponse(BaseModel):
    """API/use-case output: recommendations plus explicit audit metadata."""

    member_id: str
    partner_id: str
    items: list[RecommendationItem] = Field(default_factory=list)
    audit: RecommendationAudit
