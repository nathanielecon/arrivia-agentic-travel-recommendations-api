import json

import pytest

from arrivia_recs.domain.models import BookingRecord, MemberProfile, RecommendationRequest
from arrivia_recs.domain.partner_policy import PartnerPolicy
from arrivia_recs.observability.context import hash_identifier, safe_request_id
from arrivia_recs.observability.logging import configure_logging
from arrivia_recs.services.recommendations import RecommendationService
from arrivia_recs.services.session_budget import SessionRecommendationBudget


class MemberStub:
    async def get_member(self, member_id: str) -> MemberProfile:
        return MemberProfile(
            member_id=member_id,
            partner_id="p1",
            loyalty_tier="Gold",
            bookings=[
                BookingRecord(
                    destination="Miami",
                    start_date="2026-01-01",
                    end_date="2026-01-07",
                    booking_type="cruise",
                )
            ],
        )


class PartnerStub:
    async def get_policy(self, partner_id: str) -> PartnerPolicy:
        return PartnerPolicy(
            partner_id=partner_id,
            max_recommendations_per_session=2,
            exclude_cruise=True,
        )


def test_identifier_hash_is_stable_and_does_not_expose_value() -> None:
    first = hash_identifier("member-secret")
    assert first == hash_identifier("member-secret")
    assert first != hash_identifier("another-member")
    assert "member-secret" not in str(first)
    assert str(first).startswith("sha256:")


def test_request_id_rejects_unbounded_or_unsafe_input() -> None:
    assert safe_request_id("trace-123") == "trace-123"
    assert safe_request_id("contains spaces") != "contains spaces"
    assert safe_request_id("x" * 129) != "x" * 129


@pytest.mark.asyncio
async def test_service_logs_json_audit_and_hashed_context_without_raw_identifiers(capsys) -> None:
    configure_logging("INFO", force=True)
    service = RecommendationService(
        MemberStub(),
        PartnerStub(),
        session_budget=SessionRecommendationBudget(),
    )

    await service.recommend(
        RecommendationRequest(member_id="member-secret", session_id="session-secret")
    )

    lines = [json.loads(line) for line in capsys.readouterr().out.splitlines() if line.startswith("{")]
    events = {line["event"] for line in lines}
    assert {
        "upstream_call.completed",
        "rule_evaluation.completed",
        "session_budget.completed",
        "recommendation.completed",
    } <= events
    completion = next(line for line in lines if line["event"] == "recommendation.completed")
    assert completion["audit_block"]["policy_source"] == "partner-config-service"
    assert completion["member_id_hash"].startswith("sha256:")
    assert completion["session_id_hash"].startswith("sha256:")
    serialized = json.dumps(lines)
    assert "member-secret" not in serialized
    assert "session-secret" not in serialized
    assert "bookings" not in serialized
