"""Read-only upstream HTTP adapters (member data, partner configuration)."""

from arrivia_recs.integrations.exceptions import (
    MemberNotFoundError,
    PartnerRulesNotFoundError,
    UpstreamAdapterError,
    UpstreamResponseError,
    UpstreamTransportError,
)
from arrivia_recs.integrations.member_client import (
    MemberAdapter,
    MemberClient,
    MemberServiceError,
)
from arrivia_recs.integrations.models import MemberProfile, PartnerRules, TravelBooking
from arrivia_recs.integrations.partner_client import PartnerClient, PartnerConfigError
from arrivia_recs.integrations.partner_config_client import (
    PartnerConfigAdapter,
    PartnerConfigClient,
)

__all__ = [
    "MemberAdapter",
    "MemberClient",
    "MemberNotFoundError",
    "MemberProfile",
    "MemberServiceError",
    "PartnerClient",
    "PartnerConfigAdapter",
    "PartnerConfigClient",
    "PartnerConfigError",
    "PartnerRules",
    "PartnerRulesNotFoundError",
    "TravelBooking",
    "UpstreamAdapterError",
    "UpstreamResponseError",
    "UpstreamTransportError",
]
