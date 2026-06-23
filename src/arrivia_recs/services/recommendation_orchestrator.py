from __future__ import annotations

from arrivia_recs.integrations.http_clients import (
    MemberServiceClient,
    PartnerConfigClient,
)
from arrivia_recs.schemas.recommendations import (
    MemberProfile,
    PolicyAuditEntry,
    RecommendationItem,
    RecommendationResponse,
)
from arrivia_recs.services.session_budget import SessionRecommendationBudget


def _candidates_from_history(member: MemberProfile) -> list[RecommendationItem]:
    out: list[RecommendationItem] = []
    for entry in member.travel_history:
        out.append(
            RecommendationItem(
                destination=entry.destination,
                booking_type=entry.booking_type,
                rationale=(
                    f"Based on your recent {entry.booking_type} travel to {entry.destination}."
                ),
            )
        )
    return out


class RecommendationOrchestrator:
    def __init__(
        self,
        member_client: MemberServiceClient,
        partner_client: PartnerConfigClient,
        session_budget: SessionRecommendationBudget,
    ) -> None:
        self._members = member_client
        self._partners = partner_client
        self._budget = session_budget

    async def recommend(
        self,
        member_id: str,
        *,
        session_id: str | None,
    ) -> RecommendationResponse:
        member = await self._members.get_member(member_id)
        rules = await self._partners.get_rules(member.partner_id)

        audit: list[PolicyAuditEntry] = []
        candidates = _candidates_from_history(member)

        if rules.exclude_cruise:
            before = len(candidates)
            candidates = [c for c in candidates if c.booking_type.lower() != "cruise"]
            removed = before - len(candidates)
            audit.append(
                PolicyAuditEntry(
                    rule="exclude_cruise",
                    partner_id=rules.partner_id,
                    detail=f"Filtered {removed} cruise candidate(s) per partner policy.",
                )
            )

        max_n = rules.max_recommendations_per_session
        if max_n is None:
            audit.append(
                PolicyAuditEntry(
                    rule="max_recommendations_per_session",
                    partner_id=rules.partner_id,
                    detail="No cap configured (unlimited).",
                )
            )
            final = candidates
        elif session_id:
            reservation = await self._budget.reserve(
                rules.partner_id,
                session_id,
                cap=max_n,
                requested=len(candidates),
            )
            audit.append(
                PolicyAuditEntry(
                    rule="max_recommendations_per_session",
                    partner_id=rules.partner_id,
                    detail=(
                        f"Session cap {max_n}; {reservation.remaining_before} recommendation slot(s) "
                        f"remaining before this request."
                    ),
                )
            )
            final = candidates[: reservation.granted]
        else:
            audit.append(
                PolicyAuditEntry(
                    rule="max_recommendations_per_session",
                    partner_id=rules.partner_id,
                    detail=(
                        f"No session_id provided; applying cap {max_n} per request "
                        f"(session totals not tracked)."
                    ),
                )
            )
            final = candidates[:max_n]

        return RecommendationResponse(
            member_id=member.member_id,
            partner_id=member.partner_id,
            loyalty_tier=member.loyalty_tier,
            recommendations=final,
            policy_audit=audit,
        )
