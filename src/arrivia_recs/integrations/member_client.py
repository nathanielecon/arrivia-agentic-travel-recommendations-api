"""HTTP clients for the member data service (read-only)."""

from __future__ import annotations

from urllib.parse import quote

import httpx
from pydantic import ValidationError

from arrivia_recs.domain.models import MemberProfile
from arrivia_recs.integrations._util import response_body_snippet
from arrivia_recs.integrations.circuit_breaker import (
    AsyncCircuitBreaker,
    CircuitOpenError,
)
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
        circuit_failure: bool = False,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.circuit_failure = circuit_failure


class MemberClient:
    """Read-only client for the member data service."""

    def __init__(
        self,
        base_url: str,
        *,
        client: httpx.AsyncClient | None = None,
        timeout_seconds: float | None = None,
        timeout: httpx.Timeout | None = None,
        circuit: AsyncCircuitBreaker | None = None,
    ) -> None:
        if timeout_seconds is not None and timeout is not None:
            raise ValueError("timeout_seconds and timeout are mutually exclusive")
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout or (
            httpx.Timeout(timeout_seconds)
            if timeout_seconds is not None
            else httpx.Timeout(connect=0.25, read=1.0, write=0.25, pool=0.25)
        )
        self._owns_client = client is None
        self._client = client or httpx.AsyncClient(base_url=self._base_url, timeout=self._timeout)
        self._member_path_prefix = "/v1/members" if self._owns_client else "/members"
        self.circuit = circuit or AsyncCircuitBreaker("member")

    async def aclose(self) -> None:
        if self._owns_client:
            await self._client.aclose()

    async def _request_member(self, member_id: str) -> MemberProfile:
        try:
            response = await self._client.get(
                f"{self._member_path_prefix}/{quote(member_id, safe='')}",
                timeout=self._timeout,
            )
        except httpx.TimeoutException as exc:
            raise MemberServiceError(
                "member service request timed out",
                status_code=502,
                code="upstream_timeout",
                circuit_failure=True,
            ) from exc
        except httpx.RequestError as exc:
            raise MemberServiceError(
                f"member service request failed: {exc}",
                status_code=502,
                code="upstream_unreachable",
                circuit_failure=True,
            ) from exc

        if response.status_code == 404:
            raise MemberServiceError("member not found", status_code=404, code="member_not_found")
        if response.is_error:
            raise MemberServiceError(
                f"member service error: HTTP {response.status_code}",
                status_code=response.status_code,
                code="upstream_error",
                circuit_failure=response.status_code == 429 or response.status_code >= 500,
            )
        try:
            payload = response.json()
        except ValueError as exc:
            raise MemberServiceError(
                "member service returned invalid JSON",
                status_code=502,
                code="upstream_invalid_payload",
                circuit_failure=True,
            ) from exc

        try:
            return MemberProfile.model_validate(payload)
        except ValidationError as exc:
            raise MemberServiceError(
                "member service returned invalid member payload",
                status_code=502,
                code="upstream_invalid_payload",
                circuit_failure=True,
            ) from exc

    async def get_member(self, member_id: str) -> MemberProfile:
        try:
            return await self.circuit.call(
                lambda: self._request_member(member_id),
                is_failure=lambda exc: bool(getattr(exc, "circuit_failure", False)),
            )
        except CircuitOpenError as exc:
            raise MemberServiceError(
                str(exc),
                status_code=502,
                code="upstream_circuit_open",
            ) from exc
