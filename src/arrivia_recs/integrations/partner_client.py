import httpx

from arrivia_recs.domain.partner_policy import PartnerPolicy


class PartnerConfigError(Exception):
    """Partner policy lookup failed (HTTP, parse, or missing policy)."""


class PartnerClient:
    """Read-only client for partner configuration (rules are enforced, never written)."""

    def __init__(
        self,
        base_url: str,
        *,
        client: httpx.AsyncClient | None = None,
        timeout_seconds: float = 10.0,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._owns_client = client is None
        self._client = client or httpx.AsyncClient(
            base_url=self._base_url,
            timeout=timeout_seconds,
        )

    async def aclose(self) -> None:
        if self._owns_client:
            await self._client.aclose()

    async def get_policy(self, partner_id: str) -> PartnerPolicy:
        try:
            response = await self._client.get(f"/partners/{partner_id}/policy")
        except httpx.RequestError as exc:
            raise PartnerConfigError(f"partner config request failed: {exc}") from exc

        if response.status_code == 404:
            raise PartnerConfigError("partner policy not found")
        if response.is_error:
            raise PartnerConfigError(
                f"partner config error: HTTP {response.status_code}",
            )
        try:
            payload = response.json()
        except ValueError as exc:
            raise PartnerConfigError("partner config returned invalid JSON") from exc

        max_raw = payload.get("max_recommendations_per_session")
        max_per: int | None
        if max_raw is None:
            max_per = None
        else:
            max_per = int(max_raw)

        return PartnerPolicy(
            partner_id=str(payload["partner_id"]),
            max_recommendations_per_session=max_per,
            exclude_cruise=bool(
                payload.get("exclude_cruises", payload.get("exclude_cruise", False)),
            ),
        )
