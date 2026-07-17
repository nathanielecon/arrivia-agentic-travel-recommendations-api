"""HTTP adapter for the partner configuration service (read-only)."""

from __future__ import annotations

from urllib.parse import quote

import httpx
from pydantic import ValidationError

from arrivia_recs.domain.partner_policy import PartnerPolicy
from arrivia_recs.integrations._util import response_body_snippet
from arrivia_recs.integrations.circuit_breaker import (
    AsyncCircuitBreaker,
    CircuitOpenError,
)
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
        circuit_failure: bool = False,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.circuit_failure = circuit_failure


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
        timeout_seconds: float | None = None,
        timeout: httpx.Timeout | None = None,
        circuit: AsyncCircuitBreaker | None = None,
    ) -> None:
        if timeout_seconds is not None and timeout is not None:
            raise ValueError("timeout_seconds and timeout are mutually exclusive")
        self._base = base_url.rstrip("/")
        self._timeout = timeout or (
            httpx.Timeout(timeout_seconds)
            if timeout_seconds is not None
            else httpx.Timeout(connect=0.25, read=1.0, write=0.25, pool=0.25)
        )
        self._owns_client = client is None
        self._client = client or httpx.AsyncClient(base_url=self._base, timeout=self._timeout)
        self._policy_path_prefix = "/v1/partners" if self._owns_client else "/partners"
        self.circuit = circuit or AsyncCircuitBreaker("partner_config")

    async def aclose(self) -> None:
        if self._owns_client:
            await self._client.aclose()

    async def _request_policy(self, partner_id: str) -> PartnerPolicy:
        try:
            response = await self._client.get(
                f"{self._policy_path_prefix}/{quote(partner_id, safe='')}/policy",
                timeout=self._timeout,
            )
        except httpx.TimeoutException as exc:
            raise PartnerConfigError(
                "partner config request timed out",
                status_code=502,
                code="upstream_timeout",
                circuit_failure=True,
            ) from exc
        except httpx.RequestError as exc:
            raise PartnerConfigError(
                f"partner config request failed: {exc}",
                status_code=502,
                code="upstream_unreachable",
                circuit_failure=True,
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
                circuit_failure=response.status_code == 429 or response.status_code >= 500,
            )

        try:
            payload = response.json()
        except ValueError as exc:
            raise PartnerConfigError(
                "partner config returned invalid JSON",
                status_code=502,
                code="upstream_invalid_payload",
                circuit_failure=True,
            ) from exc

        try:
            policy = PartnerPolicy.model_validate(payload)
        except ValidationError as exc:
            raise PartnerConfigError(
                "partner config returned invalid policy payload",
                status_code=502,
                code="upstream_invalid_payload",
                circuit_failure=True,
            ) from exc
        if policy.partner_id != partner_id:
            raise PartnerConfigError(
                "partner config returned a policy for a different partner",
                status_code=502,
                code="upstream_invalid_payload",
                circuit_failure=True,
            )
        return policy

    async def get_policy(self, partner_id: str) -> PartnerPolicy:
        try:
            return await self.circuit.call(
                lambda: self._request_policy(partner_id),
                is_failure=lambda exc: bool(getattr(exc, "circuit_failure", False)),
            )
        except CircuitOpenError as exc:
            raise PartnerConfigError(
                str(exc),
                status_code=502,
                code="upstream_circuit_open",
            ) from exc
