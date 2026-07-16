from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class PartnerPolicy(BaseModel):
    """Read-only partner configuration: caps and exclusions enforced by this service."""

    model_config = ConfigDict(extra="forbid", strict=True)

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
        canonical = data.get("exclude_cruise")
        if "exclude_cruises" not in data:
            return data
        alias = data["exclude_cruises"]
        if "exclude_cruise" in data and canonical != alias:
            raise ValueError("exclude_cruise and exclude_cruises cannot conflict")
        normalized = {**data, "exclude_cruise": alias}
        normalized.pop("exclude_cruises", None)
        return normalized

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
