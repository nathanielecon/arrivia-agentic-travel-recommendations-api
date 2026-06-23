from __future__ import annotations

import uuid
from collections.abc import MutableMapping
from typing import Literal

import structlog

from arrivia_recs.domain.models import (
    ApiRecommendationAudit,
    MemberProfile,
    PolicyAuditEntry,
    RecommendationItem,
    RecommendationRequest,
    RecommendationResponse,
)
from arrivia_recs.domain.partner_policy import PartnerPolicy
from arrivia_recs.integrations.member_client import MemberClient
from arrivia_recs.integrations.partner_config_client import PartnerConfigClient
from arrivia_recs.services.session_budget import SessionRecommendationBudget

log = structlog.get_logger(__name__)

POLICY_SOURCE = "partner-config-service"

OfferType = Literal["flight", "hotel", "cruise", "package", "car"]


def _map_booking_type(booking_type: str) -> OfferType:
    t = booking_type.lower()
    if t == "flight":
        return "flight"
    if t in ("hotel", "lodging"):
        return "hotel"
    if t == "cruise":
        return "cruise"
    if t in ("car", "rental_car"):
        return "car"
    return "package"


def _build_candidates(member: MemberProfile) -> list[RecommendationItem]:
    # v0 keeps candidate generation intentionally simple so the walkthrough can focus on policy enforcement.
    items: list[RecommendationItem] = []
    seen: set[str] = set()
    for booking in member.bookings[:5]:
        key = booking.destination.strip().lower()
        if not key or key in seen:
            continue
        seen.add(key)
        offer_type = _map_booking_type(booking.booking_type)
        items.append(
            RecommendationItem(
                id=str(uuid.uuid4()),
                title=f"Return to {booking.destination}",
                offer_type=offer_type,
                rationale=f"Based on your recent {booking.booking_type} stay.",
            )
        )
    items.extend(
        [
            RecommendationItem(
                id=str(uuid.uuid4()),
                title="Weekend city break (flight + hotel)",
                offer_type="package",
                rationale="Popular for your loyalty tier.",
            ),
            RecommendationItem(
                id=str(uuid.uuid4()),
                title="Caribbean cruise getaway",
                offer_type="cruise",
                rationale="Seasonal cruise offers.",
            ),
            RecommendationItem(
                id=str(uuid.uuid4()),
                title="Point-to-point flight deals",
                offer_type="flight",
                rationale="Flexible dates from your home airport.",
            ),
        ]
    )
    return items


class RecommendationService:
    """Orchestrates member + partner policy and returns auditable recommendations."""

    def __init__(
        self,
        member_client: MemberClient,
        partner_client: PartnerConfigClient,
        session_counts: MutableMapping[tuple[str, str], int] | None = None,
        session_budget: SessionRecommendationBudget | None = None,
    ) -> None:
        self._members = member_client
        self._partners = partner_client
        self._session_budget = session_budget or SessionRecommendationBudget(session_counts)

    async def recommend(self, body: RecommendationRequest) -> RecommendationResponse:
        # Walkthrough cue: "This is the heart of the project. Everything important happens in this flow."
        # Step 1: load the member so we know both travel history and the partner context.
        member = await self._members.get_member(body.member_id)
        partner_id = member.partner_id
        # Step 2: load the authoritative read-only partner policy for that member's partner.
        policy = await self._partners.get_policy(partner_id)

        audit_rules: list[PolicyAuditEntry] = [
            PolicyAuditEntry(
                rule="max_recommendations_per_session",
                value="unlimited"
                if policy.max_recommendations_per_session is None
                else str(policy.max_recommendations_per_session),
            ),
            PolicyAuditEntry(rule="exclude_cruise", value=str(policy.exclude_cruise).lower()),
        ]

        log.info(
            "recommendations.policy_loaded",
            partner_id=partner_id,
            member_id=member.member_id,
            max_per_session=policy.max_recommendations_per_session,
            exclude_cruise=policy.exclude_cruise,
        )

        # Step 3: build generic recommendation candidates, then let partner policy narrow them.
        candidates = _build_candidates(member)
        if policy.exclude_cruise:
            candidates = [c for c in candidates if c.offer_type != "cruise"]

        # Step 4: enforce per-session caps before returning anything to the caller.
        if policy.max_recommendations_per_session is None:
            recs = candidates
        else:
            granted = await self._reserve_budget(
                partner_id,
                body.session_id,
                policy,
                requested=len(candidates),
            )
            recs = candidates[:granted]

        audit = ApiRecommendationAudit(
            partner_id=partner_id,
            policy_source=POLICY_SOURCE,
            rules_applied=audit_rules,
        )
        return RecommendationResponse(
            partner_id=partner_id,
            member_id=member.member_id,
            recommendations=recs,
            audit=audit,
        )

    async def _reserve_budget(
        self,
        partner_id: str,
        session_id: str | None,
        policy: PartnerPolicy,
        *,
        requested: int,
    ) -> int:
        # Walkthrough cue: "This is where the partner's session cap becomes real."
        # No session_id means we can still enforce a per-request cap, but not accumulate usage over time.
        if policy.max_recommendations_per_session is None:
            return requested
        cap = policy.max_recommendations_per_session
        if not session_id:
            return min(requested, cap)
        reservation = await self._session_budget.reserve(
            partner_id,
            session_id,
            cap=cap,
            requested=requested,
        )
        return reservation.granted
