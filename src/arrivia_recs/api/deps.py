from fastapi import Depends

from arrivia_recs.config import settings
from arrivia_recs.integrations.member_client import MemberClient
from arrivia_recs.integrations.partner_config_client import PartnerConfigClient
from arrivia_recs.services.recommendations import RecommendationService
from arrivia_recs.services.session_budget import (
    SessionRecommendationBudget,
    get_shared_session_budget,
)


def get_member_client() -> MemberClient:
    return MemberClient(settings.member_service_base_url)


def get_partner_config_client() -> PartnerConfigClient:
    return PartnerConfigClient(settings.partner_config_base_url)


def get_session_budget() -> SessionRecommendationBudget:
    return get_shared_session_budget()


def get_recommendation_service(
    members: MemberClient = Depends(get_member_client),
    partners: PartnerConfigClient = Depends(get_partner_config_client),
    session_budget: SessionRecommendationBudget = Depends(get_session_budget),
) -> RecommendationService:
    return RecommendationService(members, partners, session_budget=session_budget)
