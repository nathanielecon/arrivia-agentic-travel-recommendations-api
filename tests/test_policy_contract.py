from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from arrivia_recs.domain.partner_policy import PartnerPolicy

ROOT = Path(__file__).resolve().parent.parent


def test_published_partner_policy_contract_matches_canonical_example() -> None:
    schema = json.loads((ROOT / "docs/contracts/partner-policy.schema.json").read_text())
    example = json.loads((ROOT / "docs/contracts/partner-policy.example.json").read_text())

    assert schema["additionalProperties"] is False
    assert schema["required"] == ["partner_id"]
    assert set(schema["properties"]) == {
        "partner_id",
        "max_recommendations_per_session",
        "exclude_cruise",
        "exclude_cruises",
    }
    assert PartnerPolicy.model_validate(example).exclude_cruise is True


@pytest.mark.parametrize("cap", [None, 0, 3])
def test_partner_policy_accepts_null_and_non_negative_caps(cap: int | None) -> None:
    policy = PartnerPolicy(partner_id="p1", max_recommendations_per_session=cap)
    assert policy.max_recommendations_per_session == cap


def test_partner_policy_accepts_only_documented_alias() -> None:
    assert PartnerPolicy(partner_id="p1", exclude_cruises=True).exclude_cruise is True
    assert (
        PartnerPolicy(partner_id="p1", exclude_cruise=True, exclude_cruises=True).exclude_cruise
        is True
    )


@pytest.mark.parametrize(
    "payload",
    [
        {"partner_id": "p1", "new_restriction": True},
        {"partner_id": "p1", "max_recommendations_per_session": -1},
        {"partner_id": "p1", "exclude_cruise": "yes"},
        {"partner_id": "p1", "exclude_cruise": True, "exclude_cruises": False},
    ],
)
def test_partner_policy_fails_closed_for_unsupported_or_conflicting_payload(payload: dict) -> None:
    with pytest.raises(ValidationError):
        PartnerPolicy.model_validate(payload)
