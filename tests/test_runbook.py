"""Operator runbook contract: docs/plan/runbook.md must stay actionable and aligned with v0 behavior."""

from __future__ import annotations

from pathlib import Path

import pytest

RUNBOOK = Path(__file__).resolve().parent.parent / "docs" / "plan" / "runbook.md"


@pytest.fixture(scope="module")
def runbook_text() -> str:
    assert RUNBOOK.is_file(), "docs/plan/runbook.md must exist"
    return RUNBOOK.read_text(encoding="utf-8")


def test_runbook_covers_local_run_and_health(runbook_text: str) -> None:
    required = [
        "uvicorn",
        "8080",
        "/health",
        "/ready",
        "docker compose",
        "MEMBER_SERVICE_BASE_URL",
        "PARTNER_CONFIG_BASE_URL",
    ]
    missing = [x for x in required if x not in runbook_text]
    assert not missing, f"runbook missing expected operator anchors: {missing}"


def test_runbook_documents_failures_and_tenant_audit(runbook_text: str) -> None:
    required = [
        "upstream_unreachable",
        "policy_audit",
        "read-only",
        "WireMock",
        "mocks",
    ]
    missing = [x for x in required if x not in runbook_text]
    assert not missing, f"runbook missing expected incident/audit phrases: {missing}"


def test_runbook_avoids_hardcoded_user_paths(runbook_text: str) -> None:
    assert "C:\\Users\\" not in runbook_text
    assert "C:/Users/" not in runbook_text
