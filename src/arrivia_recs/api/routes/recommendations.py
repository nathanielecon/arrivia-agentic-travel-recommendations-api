from __future__ import annotations

import httpx
from fastapi import APIRouter, Depends, HTTPException

from arrivia_recs.api.deps import get_recommendation_service
from arrivia_recs.domain.models import RecommendationRequest, RecommendationResponse
from arrivia_recs.integrations.member_client import MemberServiceError as RecommendationMemberError
from arrivia_recs.integrations.partner_config_client import (
    PartnerConfigError as RecommendationPartnerError,
)
from arrivia_recs.services.recommendations import RecommendationService

router = APIRouter(tags=["recommendations"])


def _recommendation_error_detail(exc: Exception, *, not_found_code: str) -> tuple[int, str]:
    # Keep upstream failures explicit so the API contract stays predictable during demos and on-call triage.
    code = getattr(exc, "code", None)
    if code:
        return (404 if code == not_found_code else 502, code)

    message = str(exc).lower()
    if "not found" in message:
        return (404 if not_found_code == "member_not_found" else 502, not_found_code)
    if "invalid" in message:
        return 502, "upstream_invalid_payload"
    if "unreachable" in message:
        return 502, "upstream_unreachable"
    return 502, "upstream_error"


@router.post("/recommendations", response_model=RecommendationResponse)
async def create_recommendations(
    body: RecommendationRequest,
    service: RecommendationService = Depends(get_recommendation_service),
) -> RecommendationResponse:
    # Walkthrough cue: "This file is the front door. The API layer stays small on purpose."
    # The route is intentionally thin: validate input, delegate to the shared service, translate failures.
    try:
        return await service.recommend(body)
    except RecommendationMemberError as exc:
        status, detail = _recommendation_error_detail(exc, not_found_code="member_not_found")
        raise HTTPException(status_code=status, detail=detail) from exc
    except RecommendationPartnerError as exc:
        _status, detail = _recommendation_error_detail(exc, not_found_code="partner_policy_not_found")
        raise HTTPException(status_code=502, detail=detail) from exc
    except httpx.HTTPStatusError as exc:
        url = str(exc.request.url)
        status = exc.response.status_code
        if status == 404 and "/members/" in url:
            raise HTTPException(status_code=404, detail="member_not_found") from exc
        if status == 404 and "/partners/" in url:
            raise HTTPException(status_code=502, detail="partner_policy_not_found") from exc
        raise HTTPException(status_code=502, detail="upstream_error") from exc
    except httpx.RequestError as exc:
        raise HTTPException(status_code=502, detail="upstream_unreachable") from exc
