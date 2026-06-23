"""README is the seeded product and reviewer guidance; keep these checks in sync with intentional doc contracts."""

from __future__ import annotations

from pathlib import Path

import pytest

README = Path(__file__).resolve().parent.parent / "README.md"


@pytest.fixture(scope="module")
def readme_text() -> str:
    assert README.is_file(), "README.md must exist at repository root"
    return README.read_text(encoding="utf-8")


def test_readme_documents_constraints_and_scope(readme_text: str) -> None:
    required_phrases = [
        "Prompt.md",
        "read-only",
        "Four-week",
        "containerized",
        "Multi-tenant",
        "MCP",
        "WireMock",
        "8080",
        "pytest",
        "ruff",
    ]
    missing = [p for p in required_phrases if p not in readme_text]
    assert not missing, f"README missing expected guidance phrases: {missing}"


def test_readme_has_v0_later_and_reviewer_sections(readme_text: str) -> None:
    required_headers = [
        "## Fastest Reviewer Path",
        "## MCP Quick Start",
        "## Judge Proof",
        "## What Ships In v0",
        "## What Comes Later",
        "## Four-Week Delivery Plan",
        "## Ralphy And Codex Workflow",
    ]
    missing = [header for header in required_headers if header not in readme_text]
    assert not missing, f"README missing expected sections: {missing}"


def test_readme_fastest_path_is_actionable(readme_text: str) -> None:
    required = [
        "Copy-Item .env.example .env -Force",
        "docker compose --profile mocks up --build",
        'http://127.0.0.1:8080/v1/recommendations',
        "arrivia-recs-demo --member-id m1 --session-id review-session-1",
        '"member_id":"m1"',
        '"session_id":"review-session-1"',
        "partner_id` is `p1`",
        "audit",
    ]
    missing = [item for item in required if item not in readme_text]
    assert not missing, f"README missing expected reviewer commands or assertions: {missing}"


def test_readme_documents_mcp_and_ralphy_codex_flow(readme_text: str) -> None:
    required = [
        "python -m arrivia_recs.mcp.server",
        "python -m pytest tests/test_mcp_stdio_smoke.py -q",
        "python -m pytest tests/test_mcp_stdio_smoke.py tests/test_scope_contracts.py -q",
        "get_travel_recommendations",
        "docs/examples/mcp-stdio-transcript.md",
        "docs/examples/judge-proof.md",
        "Primary HTTP contract: `POST /v1/recommendations`",
        "single active API replica",
        "same-machine shared state",
        "Horizontal scale is deferred",
        "docs/examples/codex-ralphy-review.yaml",
        "ralphy --codex --yaml docs/examples/codex-ralphy-review.yaml --parallel --max-parallel 3 -v",
        "parallel_group",
        "127.0.0.1:8081",
        "127.0.0.1:8082",
    ]
    missing = [item for item in required if item not in readme_text]
    assert not missing, f"README missing expected MCP or Ralphy guidance: {missing}"


def test_readme_avoids_hardcoded_user_paths(readme_text: str) -> None:
    assert "C:\\Users\\" not in readme_text
    assert "C:/Users/" not in readme_text
