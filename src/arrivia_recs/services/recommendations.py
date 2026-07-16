from __future__ import annotations

import time
import uuid
from collections.abc import Awaitable, MutableMapping
from typing import Literal, TypeVar

import structlog
from structlog.contextvars import bind_contextvars, get_contextvars, reset_contextvars

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
from arrivia_recs.observability.context import ensure_service_context, hash_identifier
from arrivia_recs.observability.metrics import (
    budget_reservation_failures_total,
    normalize_rule_value,
    partner_config_upstream_requests_total,
    recommendation_request_duration_seconds,
    recommendation_requests_total,
    rule_evaluation_duration_seconds,
    rule_evaluations_total,
    session_budget_reservations_total,
    set_circuit_state,
    upstream_request_duration_seconds,
)
from arrivia_recs.services.session_budget import SessionRecommendationBudget

log = structlog.get_logger(__name__)

POLICY_SOURCE = "partner-config-service"

OfferType = Literal["flight", "hotel", "cruise", "package", "car"]
T = TypeVar("T")


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
        context_tokens = ensure_service_context()
        identifier_tokens = bind_contextvars(
            member_id_hash=hash_identifier(body.member_id),
            session_id_hash=hash_identifier(body.session_id),
        )
        try:
            return await self._recommend(body)
        finally:
            reset_contextvars(**identifier_tokens)
            if context_tokens:
                reset_contextvars(**context_tokens)

    async def _recommend(self, body: RecommendationRequest) -> RecommendationResponse:
        # Walkthrough cue: "This is the heart of the project. Everything important happens in this flow."
        request_started = time.perf_counter()
        # Step 1: load the member so we know both travel history and the partner context.
        member = await self._load_upstream("member", self._members.get_member(body.member_id))
        partner_id = member.partner_id
        # Step 2: load the authoritative read-only partner policy for that member's partner.
        policy = await self._load_upstream(
            "partner_config", self._partners.get_policy(partner_id), partner_id=partner_id
        )

        audit_rules: list[PolicyAuditEntry] = [
            PolicyAuditEntry(
                rule="max_recommendations_per_session",
                value="unlimited"
                if policy.max_recommendations_per_session is None
                else str(policy.max_recommendations_per_session),
            ),
            PolicyAuditEntry(rule="exclude_cruise", value=str(policy.exclude_cruise).lower()),
        ]

        # Step 3: build generic recommendation candidates, then let partner policy narrow them.
        candidates = _build_candidates(member)
        rule_started = time.perf_counter()
        if policy.exclude_cruise:
            candidates = [c for c in candidates if c.offer_type != "cruise"]
        self._observe_rule("exclude_cruise", policy.exclude_cruise, rule_started, partner_id)

        cap_rule_started = time.perf_counter()
        self._observe_rule(
            "max_recommendations_per_session",
            policy.max_recommendations_per_session,
            cap_rule_started,
            partner_id,
        )

        # Step 4: enforce per-session caps before returning anything to the caller.
        if policy.max_recommendations_per_session is None:
            recs = candidates
            session_budget_reservations_total.labels(outcome="unlimited").inc()
            log.info(
                "session_budget.completed",
                outcome="unlimited",
                requested=len(candidates),
                granted=len(recs),
            )
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
        response = RecommendationResponse(
            partner_id=partner_id,
            member_id=member.member_id,
            recommendations=recs,
            audit=audit,
        )
        duration = time.perf_counter() - request_started
        log.info(
            "recommendation.completed",
            outcome="success",
            duration_seconds=duration,
            recommendation_count=len(recs),
            audit_block=audit.model_dump(mode="json"),
            partner_id=partner_id,
        )
        surface = str(get_contextvars().get("surface", "service"))
        if surface != "rest":
            recommendation_requests_total.labels(
                surface=surface, outcome="success", status_class="2xx"
            ).inc()
            recommendation_request_duration_seconds.labels(
                surface=surface, outcome="success"
            ).observe(duration)
        return response

    async def _load_upstream(
        self,
        dependency: str,
        awaitable: Awaitable[T],
        *,
        partner_id: str | None = None,
    ) -> T:
        started = time.perf_counter()
        try:
            result = await awaitable
        except Exception as exc:
            duration = time.perf_counter() - started
            error_code = str(getattr(exc, "code", "upstream_error"))
            outcome = self._bounded_upstream_outcome(error_code)
            upstream_request_duration_seconds.labels(
                dependency=dependency, outcome=outcome
            ).observe(duration)
            if dependency == "partner_config":
                partner_config_upstream_requests_total.labels(outcome=outcome).inc()
            if outcome == "circuit_open":
                set_circuit_state(dependency, "open")
            log.warning(
                "upstream_call.completed",
                dependency=dependency,
                partner_id=partner_id,
                outcome=outcome,
                duration_seconds=duration,
                error_code=error_code,
            )
            raise
        duration = time.perf_counter() - started
        upstream_request_duration_seconds.labels(dependency=dependency, outcome="success").observe(
            duration
        )
        if dependency == "partner_config":
            partner_config_upstream_requests_total.labels(outcome="success").inc()
        set_circuit_state(dependency, "closed")
        log.info(
            "upstream_call.completed",
            dependency=dependency,
            partner_id=partner_id,
            outcome="success",
            duration_seconds=duration,
        )
        return result

    @staticmethod
    def _bounded_upstream_outcome(error_code: str) -> str:
        if error_code == "upstream_circuit_open":
            return "circuit_open"
        if error_code in {"member_not_found", "partner_policy_not_found"}:
            return "not_found"
        if error_code == "upstream_invalid_payload":
            return "invalid_payload"
        if error_code in {"upstream_timeout", "upstream_unreachable"}:
            return "transport_error"
        return "error"

    @staticmethod
    def _observe_rule(rule: str, value: object, started: float, partner_id: str) -> None:
        duration = time.perf_counter() - started
        normalized = normalize_rule_value(rule, value)
        rule_evaluation_duration_seconds.labels(partner_id=partner_id, rule=rule).observe(duration)
        rule_evaluations_total.labels(
            partner_id=partner_id, rule=rule, value=normalized
        ).inc()
        log.info(
            "rule_evaluation.completed",
            rule=rule,
            value=normalized,
            outcome="applied",
            duration_seconds=duration,
            partner_id=partner_id,
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
            granted = min(requested, cap)
            session_budget_reservations_total.labels(outcome="per_request").inc()
            log.info(
                "session_budget.completed",
                outcome="per_request",
                requested=requested,
                granted=granted,
            )
            return granted
        started = time.perf_counter()
        try:
            reservation = await self._session_budget.reserve(
                partner_id,
                session_id,
                cap=cap,
                requested=requested,
            )
        except Exception:
            budget_reservation_failures_total.labels(reason="infrastructure").inc()
            session_budget_reservations_total.labels(outcome="failure").inc()
            log.exception(
                "session_budget.completed",
                outcome="failure",
                duration_seconds=time.perf_counter() - started,
                error_code="budget_infrastructure_error",
            )
            raise
        outcome = "granted" if reservation.granted > 0 else "exhausted"
        session_budget_reservations_total.labels(outcome=outcome).inc()
        log.info(
            "session_budget.completed",
            outcome=outcome,
            requested=requested,
            granted=reservation.granted,
            remaining_before=reservation.remaining_before,
            duration_seconds=time.perf_counter() - started,
        )
        return reservation.granted
