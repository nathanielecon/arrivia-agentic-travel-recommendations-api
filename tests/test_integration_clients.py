import httpx
import pytest

from arrivia_recs.integrations.member_client import MemberClient, MemberServiceError
from arrivia_recs.integrations.partner_client import PartnerClient, PartnerConfigError


async def test_member_client_parses_success_payload() -> None:
    body = {
        "member_id": "m-9",
        "partner_id": "p-9",
        "loyalty_tier": "Platinum",
        "travel_history": [
            {
                "destination": "SEA",
                "start_date": "2025-03-01",
                "booking_type": "hotel",
            },
        ],
    }

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/members/m-9"
        return httpx.Response(200, json=body)

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport, base_url="http://member") as client:
        mc = MemberClient("http://member", client=client)
        member = await mc.get_member("m-9")

    assert member.member_id == "m-9"
    assert member.partner_id == "p-9"
    assert member.travel_history[0].destination == "SEA"


async def test_member_client_404_is_explicit() -> None:
    transport = httpx.MockTransport(lambda r: httpx.Response(404))
    async with httpx.AsyncClient(transport=transport, base_url="http://member") as client:
        mc = MemberClient("http://member", client=client)
        with pytest.raises(MemberServiceError, match="not found"):
            await mc.get_member("missing")


async def test_member_client_http_error_is_explicit() -> None:
    transport = httpx.MockTransport(lambda r: httpx.Response(502, text="bad gateway"))
    async with httpx.AsyncClient(transport=transport, base_url="http://member") as client:
        mc = MemberClient("http://member", client=client)
        with pytest.raises(MemberServiceError, match="HTTP 502"):
            await mc.get_member("m-1")


async def test_member_client_invalid_json_is_explicit() -> None:
    transport = httpx.MockTransport(lambda r: httpx.Response(200, text="not-json"))
    async with httpx.AsyncClient(transport=transport, base_url="http://member") as client:
        mc = MemberClient("http://member", client=client)
        with pytest.raises(MemberServiceError, match="invalid JSON"):
            await mc.get_member("m-1")


async def test_partner_client_parses_policy() -> None:
    body = {
        "partner_id": "p-1",
        "max_recommendations_per_session": 5,
        "exclude_cruises": True,
    }

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/partners/p-1/policy"
        return httpx.Response(200, json=body)

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport, base_url="http://partner") as client:
        pc = PartnerClient("http://partner", client=client)
        policy = await pc.get_policy("p-1")

    assert policy.partner_id == "p-1"
    assert policy.max_recommendations_per_session == 5
    assert policy.exclude_cruises is True


async def test_partner_client_null_cap_means_unlimited() -> None:
    body = {
        "partner_id": "p-1",
        "max_recommendations_per_session": None,
        "exclude_cruises": False,
    }
    transport = httpx.MockTransport(lambda r: httpx.Response(200, json=body))
    async with httpx.AsyncClient(transport=transport, base_url="http://partner") as client:
        pc = PartnerClient("http://partner", client=client)
        policy = await pc.get_policy("p-1")

    assert policy.max_recommendations_per_session is None


async def test_partner_client_http_error_is_explicit() -> None:
    transport = httpx.MockTransport(lambda r: httpx.Response(503))
    async with httpx.AsyncClient(transport=transport, base_url="http://partner") as client:
        pc = PartnerClient("http://partner", client=client)
        with pytest.raises(PartnerConfigError, match="HTTP 503"):
            await pc.get_policy("p-1")
