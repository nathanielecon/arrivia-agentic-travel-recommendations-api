"""HTTP clients for the member data service (read-only)."""

from __future__ import annotations

from urllib.parse import quote

import httpx
from pydantic import ValidationError

from arrivia_recs.domain.models import MemberProfile
from arrivia_recs.integrations._util import response_body_snippet
from arrivia_recs.integrations.exceptions import (
    MemberNotFoundError,
    UpstreamResponseError,
    UpstreamTransportError,
)
from arrivia_recs.integrations.models import MemberProfile as UpstreamMemberProfile

_DEFAULT_TIMEOUT = httpx.Timeout(5.0)


class MemberAdapter:
    """
    Read-only client for member profile lookups.

    Expected upstream contract: GET {base_url}/members/{member_id} returns JSON
    matching MemberProfile.
    """

    def __init__(
        self,
        base_url: str,
        *,
        client: httpx.AsyncClient | None = None,
        timeout: httpx.Timeout | None = None,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout or _DEFAULT_TIMEOUT
        self._client = client

    async def get_member(self, member_id: str) -> UpstreamMemberProfile:
        safe_id = quote(member_id, safe="")
        url = f"{self._base_url}/members/{safe_id}"
        try:
            if self._client is not None:
                response = await self._client.get(url)
            else:
                async with httpx.AsyncClient(timeout=self._timeout) as client:
                    response = await client.get(url)
        except httpx.TimeoutException as e:
            raise UpstreamTransportError(f"member service timeout for member_id={member_id!r}") from e
        except httpx.RequestError as e:
            raise UpstreamTransportError(
                f"member service request failed for member_id={member_id!r}: {e}"
            ) from e

        if response.status_code == 404:
            raise MemberNotFoundError(
                f"member not found: {member_id!r}",
                status_code=404,
                body_snippet=response_body_snippet(response.text),
            )
        if response.status_code != 200:
            raise UpstreamResponseError(
                f"member service returned {response.status_code} for member_id={member_id!r}",
                status_code=response.status_code,
                body_snippet=response_body_snippet(response.text),
            )
        try:
            return UpstreamMemberProfile.model_validate_json(response.content)
        except ValidationError as e:
            raise UpstreamResponseError(
                f"member service response failed validation for member_id={member_id!r}: {e}",
                status_code=response.status_code,
                body_snippet=response_body_snippet(response.text),
            ) from e


class MemberServiceError(Exception):
    """Member lookup failed in a way callers should surface (HTTP, parse, or not found)."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        code: str | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.code = code


class MemberClient:
    """Read-only client for the member data service."""

    def __init__(
        self,
        base_url: str,
        *,
        client: httpx.AsyncClient | None = None,
        timeout_seconds: float = 10.0,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout_seconds
        self._client = client

    async def _get_member_injected(self, member_id: str) -> MemberProfile:
        client = self._client
        assert client is not None
        try:
            response = await client.get(f"/members/{member_id}")
        except httpx.RequestError as exc:
            raise MemberServiceError(
                f"member service request failed: {exc}",
                status_code=502,
                code="upstream_unreachable",
            ) from exc

        if response.status_code == 404:
            raise MemberServiceError("member not found", status_code=404, code="member_not_found")
        if response.is_error:
            raise MemberServiceError(
                f"member service error: HTTP {response.status_code}",
                status_code=response.status_code,
                code="upstream_error",
            )
        try:
            payload = response.json()
        except ValueError as exc:
            raise MemberServiceError(
                "member service returned invalid JSON",
                status_code=502,
                code="upstream_invalid_payload",
            ) from exc

        try:
            return MemberProfile.model_validate(payload)
        except ValidationError as exc:
            raise MemberServiceError(
                "member service returned invalid member payload",
                status_code=502,
                code="upstream_invalid_payload",
            ) from exc

    async def get_member(self, member_id: str) -> MemberProfile:
        if self._client is not None:
            return await self._get_member_injected(member_id)
        url = f"{self._base_url}/v1/members/{member_id}"
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.get(url)
                response.raise_for_status()
        except httpx.RequestError as exc:
            raise MemberServiceError(
                f"member service request failed: {exc}",
                status_code=502,
                code="upstream_unreachable",
            ) from exc
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 404:
                raise MemberServiceError(
                    "member not found",
                    status_code=404,
                    code="member_not_found",
                ) from exc
            raise MemberServiceError(
                f"member service error: HTTP {exc.response.status_code}",
                status_code=exc.response.status_code,
                code="upstream_error",
            ) from exc

        try:
            payload = response.json()
        except ValueError as exc:
            raise MemberServiceError(
                "member service returned invalid JSON",
                status_code=502,
                code="upstream_invalid_payload",
            ) from exc

        try:
            return MemberProfile.model_validate(payload)
        except ValidationError as exc:
            raise MemberServiceError(
                "member service returned invalid member payload",
                status_code=502,
                code="upstream_invalid_payload",
            ) from exc
