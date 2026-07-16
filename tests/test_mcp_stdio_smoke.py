from __future__ import annotations

import json
import threading
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

from arrivia_recs.api.deps import get_recommendation_service
from arrivia_recs.integrations.member_client import MemberClient
from arrivia_recs.integrations.partner_config_client import PartnerConfigClient
from arrivia_recs.main import app
from arrivia_recs.services.recommendations import RecommendationService
from arrivia_recs.services.session_budget import SessionRecommendationBudget

ROOT = Path(__file__).resolve().parent.parent


def _json_handler(routes: dict[str, dict[str, object]]):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802
            payload = routes.get(self.path)
            if payload is None:
                self.send_response(404)
                self.end_headers()
                return

            body = json.dumps(payload).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, format: str, *args: object) -> None:  # noqa: A003
            return

    return Handler


@contextmanager
def _serve_json(routes: dict[str, dict[str, object]]):
    server = ThreadingHTTPServer(("127.0.0.1", 0), _json_handler(routes))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        host, port = server.server_address
        yield f"http://{host}:{port}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


@pytest.mark.asyncio
async def test_mcp_stdio_server_supports_external_client_smoke(tmp_path: Path) -> None:
    member_routes = {
        "/v1/members/m1": {
            "member_id": "m1",
            "partner_id": "p1",
            "loyalty_tier": "Gold",
            "travel_history": [
                {
                    "destination": "Paris",
                    "start_date": "2024-01-01",
                    "end_date": "2024-01-05",
                    "booking_type": "hotel",
                }
            ],
        }
    }
    partner_routes = {
        "/v1/partners/p1/policy": {
            "partner_id": "p1",
            "max_recommendations_per_session": 3,
            "exclude_cruise": True,
        }
    }
    # Never open the Compose bind-mounted DB from the Windows host (BF-007).
    db_path = tmp_path / "mcp-stdio-smoke.sqlite3"

    with _serve_json(member_routes) as member_url, _serve_json(partner_routes) as partner_url:
        server = StdioServerParameters(
            command="python",
            args=["-m", "arrivia_recs.mcp.server"],
            cwd=str(ROOT),
            env={
                "PYTHONPATH": str(ROOT / "src"),
                "MEMBER_SERVICE_BASE_URL": member_url,
                "PARTNER_CONFIG_BASE_URL": partner_url,
                "SESSION_BUDGET_STORE_PATH": str(db_path),
            },
        )

        async with stdio_client(server) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()

                tools = await session.list_tools()
                assert "get_travel_recommendations" in {tool.name for tool in tools.tools}

                result = await session.call_tool(
                    "get_travel_recommendations",
                    {"member_id": "m1", "session_id": "review-session-1"},
                )

        text_content = [item.text for item in result.content if hasattr(item, "text")]
        assert text_content
        body = json.loads(text_content[0])
        assert body["partner_id"] == "p1"
        assert body["member_id"] == "m1"
        assert body["audit"]["policy_source"] == "partner-config-service"
        assert all(item["offer_type"] != "cruise" for item in body["recommendations"])


@pytest.mark.asyncio
async def test_rest_and_mcp_share_same_machine_session_budget(tmp_path: Path) -> None:
    member_routes = {
        "/v1/members/m1": {
            "member_id": "m1",
            "partner_id": "p1",
            "loyalty_tier": "Gold",
            "travel_history": [
                {
                    "destination": "Paris",
                    "start_date": "2024-01-01",
                    "end_date": "2024-01-05",
                    "booking_type": "hotel",
                }
            ],
        }
    }
    partner_routes = {
        "/v1/partners/p1/policy": {
            "partner_id": "p1",
            "max_recommendations_per_session": 1,
            "exclude_cruise": True,
        }
    }
    db_path = tmp_path / "shared-session-budget.sqlite3"

    with _serve_json(member_routes) as member_url, _serve_json(partner_routes) as partner_url:
        service = RecommendationService(
            MemberClient(member_url),
            PartnerConfigClient(partner_url),
            session_budget=SessionRecommendationBudget(db_path=db_path),
        )
        app.dependency_overrides[get_recommendation_service] = lambda: service
        try:
            with TestClient(app) as client:
                response = client.post(
                    "/v1/recommendations",
                    json={"member_id": "m1", "session_id": "shared-review-session"},
                )
        finally:
            app.dependency_overrides.clear()

        assert response.status_code == 200
        assert len(response.json()["recommendations"]) == 1

        server = StdioServerParameters(
            command="python",
            args=["-m", "arrivia_recs.mcp.server"],
            cwd=str(ROOT),
            env={
                "PYTHONPATH": str(ROOT / "src"),
                "MEMBER_SERVICE_BASE_URL": member_url,
                "PARTNER_CONFIG_BASE_URL": partner_url,
                "SESSION_BUDGET_STORE_PATH": str(db_path),
            },
        )

        async with stdio_client(server) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                result = await session.call_tool(
                    "get_travel_recommendations",
                    {"member_id": "m1", "session_id": "shared-review-session"},
                )

        text_content = [item.text for item in result.content if hasattr(item, "text")]
        assert text_content
        body = json.loads(text_content[0])
        assert body["partner_id"] == "p1"
        assert body["recommendations"] == []
