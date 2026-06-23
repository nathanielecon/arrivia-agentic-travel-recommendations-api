"""MCP stdio server exposing partner-aware recommendation tools."""

from __future__ import annotations

import json

import httpx
import structlog
from mcp.server.fastmcp import FastMCP

from arrivia_recs.config import settings
from arrivia_recs.domain.models import RecommendationRequest
from arrivia_recs.integrations.member_client import MemberClient, MemberServiceError
from arrivia_recs.integrations.partner_config_client import (
    PartnerConfigClient,
    PartnerConfigError,
)
from arrivia_recs.services.recommendations import RecommendationService
from arrivia_recs.services.session_budget import get_shared_session_budget

log = structlog.get_logger(__name__)

mcp = FastMCP(
    "arrivia-agentic-travel-recs",
    instructions=(
        "Travel recommendation tools for arrivia members. Partner rules come from the "
        "read-only partner configuration service; caps and exclusions are enforced and "
        "reflected in each response audit block."
    ),
)


def get_recommendation_service_mcp() -> RecommendationService:
    """Factory for the MCP process; tests may monkeypatch this hook."""
    # MCP intentionally reuses the same service class as REST so rule enforcement stays aligned.
    return RecommendationService(
        MemberClient(settings.member_service_base_url),
        PartnerConfigClient(settings.partner_config_base_url),
        session_budget=get_shared_session_budget(),
    )


def _service_error_payload(exc: Exception, *, member_id: str) -> dict[str, str]:
    code = getattr(exc, "code", None)
    detail = str(exc)

    if code == "member_not_found":
        return {"error": "member_not_found", "member_id": member_id}
    if code == "partner_policy_not_found":
        return {"error": "partner_policy_not_found", "member_id": member_id}
    if code == "upstream_invalid_payload":
        return {"error": "upstream_invalid_payload", "detail": detail, "member_id": member_id}
    if code == "upstream_unreachable":
        return {"error": "upstream_unreachable", "detail": detail, "member_id": member_id}
    return {"error": "upstream_error", "detail": detail, "member_id": member_id}


@mcp.tool()
async def get_travel_recommendations(member_id: str, session_id: str | None = None) -> str:
    """
    Return personalized travel recommendations for a member.

    Applies the member's partner policy (session caps, cruise exclusions) and returns
    JSON including an auditable ``audit`` block (partner_id, policy_source, rules_applied).
    """
    # Walkthrough cue: "This is the AI-agent entry point, but it still uses the exact same business logic as REST."
    # This is the main "AI agent" entry point for the walkthrough.
    service = get_recommendation_service_mcp()
    body = RecommendationRequest(member_id=member_id, session_id=session_id)
    try:
        result = await service.recommend(body)
        return result.model_dump_json()
    except (MemberServiceError, PartnerConfigError) as exc:
        payload = _service_error_payload(exc, member_id=member_id)
        log.warning("mcp.recommendations_service_error", error=payload["error"], member_id=member_id)
        return json.dumps(payload)
    except httpx.HTTPStatusError as exc:
        url = str(exc.request.url)
        status = exc.response.status_code
        log.warning(
            "mcp.recommendations_upstream_http_error",
            status=status,
            url=url,
            member_id=member_id,
        )
        if status == 404 and "/members/" in url:
            return json.dumps({"error": "member_not_found", "member_id": member_id})
        if status == 404 and "/partners/" in url:
            return json.dumps({"error": "partner_policy_not_found", "member_id": member_id})
        return json.dumps(
            {
                "error": "upstream_error",
                "detail": f"HTTP {status}",
                "member_id": member_id,
            }
        )
    except httpx.RequestError as exc:
        log.warning("mcp.recommendations_upstream_unreachable", error=str(exc), member_id=member_id)
        return json.dumps({"error": "upstream_unreachable", "detail": str(exc)})


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
