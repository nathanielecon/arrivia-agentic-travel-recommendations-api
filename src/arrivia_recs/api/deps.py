from functools import lru_cache

import httpx
from fastapi import Depends

from arrivia_recs.config import settings
from arrivia_recs.integrations.circuit_breaker import AsyncCircuitBreaker
from arrivia_recs.integrations.member_client import MemberClient
from arrivia_recs.integrations.partner_config_client import PartnerConfigClient
from arrivia_recs.services.recommendations import RecommendationService
from arrivia_recs.services.session_budget import (
    SessionRecommendationBudget,
    get_shared_session_budget,
)


def _upstream_timeout() -> httpx.Timeout:
    return httpx.Timeout(
        connect=settings.upstream_connect_timeout_seconds,
        read=settings.upstream_read_timeout_seconds,
        write=settings.upstream_write_timeout_seconds,
        pool=settings.upstream_pool_timeout_seconds,
    )


def _circuit(dependency: str) -> AsyncCircuitBreaker:
    return AsyncCircuitBreaker(
        dependency,
        failure_threshold=settings.upstream_circuit_failure_threshold,
        open_seconds=settings.upstream_circuit_open_seconds,
    )


@lru_cache(maxsize=1)
def get_member_client() -> MemberClient:
    return MemberClient(
        settings.member_service_base_url,
        timeout=_upstream_timeout(),
        circuit=_circuit("member"),
    )


@lru_cache(maxsize=1)
def get_partner_config_client() -> PartnerConfigClient:
    return PartnerConfigClient(
        settings.partner_config_base_url,
        timeout=_upstream_timeout(),
        circuit=_circuit("partner_config"),
    )


def get_session_budget() -> SessionRecommendationBudget:
    return get_shared_session_budget()


def get_recommendation_service(
    members: MemberClient = Depends(get_member_client),
    partners: PartnerConfigClient = Depends(get_partner_config_client),
    session_budget: SessionRecommendationBudget = Depends(get_session_budget),
) -> RecommendationService:
    return RecommendationService(members, partners, session_budget=session_budget)
