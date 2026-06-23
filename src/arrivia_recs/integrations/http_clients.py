import httpx
from pydantic import ValidationError

from arrivia_recs.schemas.recommendations import MemberProfile, PartnerRules


class MemberServiceError(Exception):
    def __init__(self, message: str, *, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class PartnerConfigError(Exception):
    def __init__(self, message: str, *, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class MemberServiceClient:
    def __init__(
        self,
        base_url: str,
        *,
        timeout_s: float = 10.0,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self._base = base_url.rstrip("/")
        self._timeout = timeout_s
        self._client = client

    async def get_member(self, member_id: str) -> MemberProfile:
        url = f"{self._base}/members/{member_id}"
        try:
            if self._client is not None:
                r = await self._client.get(url)
            else:
                async with httpx.AsyncClient(timeout=self._timeout) as client:
                    r = await client.get(url)
        except httpx.RequestError as e:
            raise MemberServiceError("member service unreachable", status_code=502) from e
        if r.status_code == 404:
            raise MemberServiceError("member not found", status_code=404)
        if r.status_code >= 400:
            raise MemberServiceError(
                f"member service error: HTTP {r.status_code}", status_code=r.status_code
            )
        try:
            data = r.json()
        except ValueError as e:
            raise MemberServiceError(
                "member service returned invalid JSON",
                status_code=502,
            ) from e
        if isinstance(data, dict) and "member_id" not in data:
            data = {**data, "member_id": member_id}
        try:
            return MemberProfile.model_validate(data)
        except ValidationError as e:
            raise MemberServiceError(
                "member service returned invalid member payload",
                status_code=502,
            ) from e


class PartnerConfigClient:
    def __init__(
        self,
        base_url: str,
        *,
        timeout_s: float = 10.0,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self._base = base_url.rstrip("/")
        self._timeout = timeout_s
        self._client = client

    async def get_rules(self, partner_id: str) -> PartnerRules:
        url = f"{self._base}/partners/{partner_id}/rules"
        try:
            if self._client is not None:
                r = await self._client.get(url)
            else:
                async with httpx.AsyncClient(timeout=self._timeout) as client:
                    r = await client.get(url)
        except httpx.RequestError as e:
            raise PartnerConfigError("partner config unreachable", status_code=502) from e
        if r.status_code == 404:
            raise PartnerConfigError("partner rules not found", status_code=404)
        if r.status_code >= 400:
            raise PartnerConfigError(
                f"partner config error: HTTP {r.status_code}", status_code=r.status_code
            )
        try:
            data = r.json()
        except ValueError as e:
            raise PartnerConfigError(
                "partner config returned invalid JSON",
                status_code=502,
            ) from e
        if isinstance(data, dict) and "partner_id" not in data:
            data = {**data, "partner_id": partner_id}
        try:
            return PartnerRules.model_validate(data)
        except ValidationError as e:
            raise PartnerConfigError(
                "partner config returned invalid rules payload",
                status_code=502,
            ) from e
