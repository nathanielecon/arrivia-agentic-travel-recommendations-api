from pydantic import BaseModel, Field, field_validator, model_validator


class PartnerPolicy(BaseModel):
    """Read-only partner configuration: caps and exclusions enforced by this service."""

    partner_id: str
    max_recommendations_per_session: int | None = Field(
        default=None,
        description="Hard cap on recommendations returned for a session; None means no cap.",
    )
    exclude_cruise: bool = False

    @model_validator(mode="before")
    @classmethod
    def _normalize_exclude_aliases(cls, data: object) -> object:
        if not isinstance(data, dict):
            return data
        if "exclude_cruise" not in data and "exclude_cruises" in data:
            data = {**data, "exclude_cruise": data["exclude_cruises"]}
        return data

    @property
    def exclude_cruises(self) -> bool:
        """Alias used by some services and upstream JSON (`exclude_cruises`)."""
        return self.exclude_cruise

    @field_validator("max_recommendations_per_session")
    @classmethod
    def non_negative_cap(cls, v: int | None) -> int | None:
        if v is not None and v < 0:
            raise ValueError("max_recommendations_per_session must be non-negative when set")
        return v
