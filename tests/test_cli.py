from __future__ import annotations

import json
from argparse import Namespace

import httpx
import pytest

from arrivia_recs import cli


def test_cli_parser_requires_member_id() -> None:
    parser = cli.build_parser()
    args = parser.parse_args(["--member-id", "m1"])
    assert args.member_id == "m1"
    assert args.base_url == "http://127.0.0.1:8080"


@pytest.mark.asyncio
async def test_cli_calls_primary_route_and_prints_json(monkeypatch: pytest.MonkeyPatch, capsys) -> None:
    expected = {"partner_id": "p1", "member_id": "m1", "recommendations": [], "audit": {}}

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/v1/recommendations"
        assert json.loads(request.content.decode("utf-8")) == {
            "member_id": "m1",
            "session_id": "review-session-1",
        }
        return httpx.Response(200, json=expected)

    transport = httpx.MockTransport(handler)

    class _PatchedClient(httpx.AsyncClient):
        def __init__(self, *args, **kwargs) -> None:
            kwargs["transport"] = transport
            super().__init__(*args, **kwargs)

    monkeypatch.setattr(cli.httpx, "AsyncClient", _PatchedClient)

    exit_code = await cli._run(
        Namespace(
            member_id="m1",
            session_id="review-session-1",
            base_url="http://127.0.0.1:8080",
        )
    )

    assert exit_code == 0
    assert json.loads(capsys.readouterr().out) == expected
