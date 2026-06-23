"""HTTP adapter for the partner configuration service (read-only)."""

from __future__ import annotations

from urllib.parse import quote

import httpx
from pydantic import ValidationError

from arrivia_recs.domain.partner_policy import PartnerPolicy
from arrivia_recs.integrations._util import response_body_snippet
from arrivia_recs.integrations.exceptions import (
    PartnerRulesNotFoundError,
    UpstreamResponseError,
    UpstreamTransportError,
)
from arrivia_recs.integrations.models import PartnerRules

_DEFAULT_TIMEOUT = httpx.Timeout(5.0)


class PartnerConfigError(Exception):
    """Partner policy lookup failed in a way callers should surface (HTTP, parse, or missing)."""

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


class PartnerConfigAdapter:
    """
    Read-only client for partner rule lookups.

    Expected upstream contract: GET {base_url}/partners/{partner_id}/rules returns JSON
    matching PartnerRules.
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

    async def get_rules(self, partner_id: str) -> PartnerRules:
        safe_id = quote(partner_id, safe="")
        url = f"{self._base_url}/partners/{safe_id}/rules"
        try:
            if self._client is not None:
                response = await self._client.get(url)
            else:
                async with httpx.AsyncClient(timeout=self._timeout) as client:
                    response = await client.get(url)
        except httpx.TimeoutException as e:
            raise UpstreamTransportError(
                f"partner config service timeout for partner_id={partner_id!r}"
            ) from e
        except httpx.RequestError as e:
            raise UpstreamTransportError(
                f"partner config service request failed for partner_id={partner_id!r}: {e}"
            ) from e

        if response.status_code == 404:
            raise PartnerRulesNotFoundError(
                f"partner rules not found: {partner_id!r}",
                status_code=404,
                body_snippet=response_body_snippet(response.text),
            )
        if response.status_code != 200:
            raise UpstreamResponseError(
                f"partner config service returned {response.status_code} "
                f"for partner_id={partner_id!r}",
                status_code=response.status_code,
                body_snippet=response_body_snippet(response.text),
            )
        try:
            return PartnerRules.model_validate_json(response.content)
        except ValidationError as e:
            raise UpstreamResponseError(
                f"partner config response failed validation for partner_id={partner_id!r}: {e}",
                status_code=response.status_code,
                body_snippet=response_body_snippet(response.text),
            ) from e


class PartnerConfigClient:
    """Read-only client for partner configuration (rules are enforced, never written)."""

    def __init__(
        self,
        base_url: str,
        *,
        client: httpx.AsyncClient | None = None,
        timeout_seconds: float = 10.0,
    ) -> None:
        self._base = base_url.rstrip("/")
        self._timeout = timeout_seconds
        self._client = client

    async def get_policy(self, partner_id: str) -> PartnerPolicy:
        if self._client is not None:
            try:
                response = await self._client.get(f"/partners/{partner_id}/policy")
            except httpx.RequestError as exc:
                raise PartnerConfigError(
                    f"partner config request failed: {exc}",
                    status_code=502,
                    code="upstream_unreachable",
                ) from exc
            if response.status_code == 404:
                raise PartnerConfigError(
                    "partner policy not found",
                    status_code=404,
                    code="partner_policy_not_found",
                )
            if response.is_error:
                raise PartnerConfigError(
                    f"partner config error: HTTP {response.status_code}",
                    status_code=response.status_code,
                    code="upstream_error",
                )
            try:
                payload = response.json()
            except ValueError as exc:
                raise PartnerConfigError(
                    "partner config returned invalid JSON",
                    status_code=502,
                    code="upstream_invalid_payload",
                ) from exc
            try:
                return PartnerPolicy.model_validate(payload)
            except ValidationError as exc:
                raise PartnerConfigError(
                    "partner config returned invalid policy payload",
                    status_code=502,
                    code="upstream_invalid_payload",
                ) from exc
        url = f"{self._base}/v1/partners/{partner_id}/policy"
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.get(url)
                response.raise_for_status()
        except httpx.RequestError as exc:
            raise PartnerConfigError(
                f"partner config request failed: {exc}",
                status_code=502,
                code="upstream_unreachable",
            ) from exc
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 404:
                raise PartnerConfigError(
                    "partner policy not found",
                    status_code=404,
                    code="partner_policy_not_found",
                ) from exc
            raise PartnerConfigError(
                f"partner config error: HTTP {exc.response.status_code}",
                status_code=exc.response.status_code,
                code="upstream_error",
            ) from exc

        try:
            payload = response.json()
        except ValueError as exc:
            raise PartnerConfigError(
                "partner config returned invalid JSON",
                status_code=502,
                code="upstream_invalid_payload",
            ) from exc

        try:
            return PartnerPolicy.model_validate(payload)
        except ValidationError as exc:
            raise PartnerConfigError(
                "partner config returned invalid policy payload",
                status_code=502,
                code="upstream_invalid_payload",
            ) from exc
