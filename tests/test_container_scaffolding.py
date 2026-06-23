"""Contract tests for local container scaffolding (Dockerfile + compose)."""

from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
_DOCKERFILE = _ROOT / "Dockerfile"
_COMPOSE = _ROOT / "docker-compose.yml"
_MEMBER_MAPPINGS = _ROOT / "mocks" / "member-service" / "mappings"
_PARTNER_MAPPINGS = _ROOT / "mocks" / "partner-config-service" / "mappings"


def test_dockerfile_sets_runtime_safety_env() -> None:
    text = _DOCKERFILE.read_text(encoding="utf-8")
    assert "PYTHONUNBUFFERED" in text
    assert "PYTHONDONTWRITEBYTECODE" in text


def test_dockerfile_runs_as_non_root() -> None:
    text = _DOCKERFILE.read_text(encoding="utf-8")
    assert "USER " in text
    assert "appuser" in text
    assert "useradd" in text


def test_dockerfile_has_healthcheck() -> None:
    text = _DOCKERFILE.read_text(encoding="utf-8")
    assert "HEALTHCHECK" in text
    assert "/health" in text


def test_compose_api_has_healthcheck_and_hardening() -> None:
    text = _COMPOSE.read_text(encoding="utf-8")
    assert "healthcheck:" in text
    assert "security_opt:" in text
    assert "no-new-privileges" in text
    assert "/health" in text
    assert "./.data:/app/.data" in text


def test_compose_declares_shared_network() -> None:
    text = _COMPOSE.read_text(encoding="utf-8")
    assert "networks:" in text
    assert "driver: bridge" in text


def test_compose_optional_mock_upstreams() -> None:
    text = _COMPOSE.read_text(encoding="utf-8")
    assert "member-service:" in text
    assert "partner-config-service:" in text
    assert "profiles:" in text
    assert "mocks" in text
    assert "wiremock/wiremock:" in text


def test_compose_mounts_wiremock_stub_directories() -> None:
    text = _COMPOSE.read_text(encoding="utf-8")
    assert "./mocks/member-service" in text
    assert "./mocks/partner-config-service" in text
    assert _MEMBER_MAPPINGS.is_dir()
    assert _PARTNER_MAPPINGS.is_dir()
