import pytest

from arrivia_recs.config import Settings

_ENV_KEYS = (
    "APP_NAME",
    "APP_ENV",
    "MEMBER_SERVICE_BASE_URL",
    "PARTNER_CONFIG_BASE_URL",
    "SESSION_BUDGET_STORE_PATH",
)


def _clear_app_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for key in _ENV_KEYS:
        monkeypatch.delenv(key, raising=False)


def test_settings_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    _clear_app_env(monkeypatch)
    s = Settings(_env_file=None)
    assert s.app_name == "arrivia-agentic-travel-recs"
    assert s.app_env == "local"
    assert s.member_service_base_url == "http://member-service:8081"
    assert s.partner_config_base_url == "http://partner-config-service:8082"
    assert s.session_budget_store_path == ".data/session_budget.sqlite3"


@pytest.mark.parametrize(
    ("env_name", "env_value", "attr", "expected"),
    [
        ("APP_NAME", "custom-name", "app_name", "custom-name"),
        ("APP_ENV", "staging", "app_env", "staging"),
        ("MEMBER_SERVICE_BASE_URL", "http://localhost:9001", "member_service_base_url", "http://localhost:9001"),
        (
            "PARTNER_CONFIG_BASE_URL",
            "http://localhost:9002",
            "partner_config_base_url",
            "http://localhost:9002",
        ),
        (
            "SESSION_BUDGET_STORE_PATH",
            ".tmp/custom-session-budget.sqlite3",
            "session_budget_store_path",
            ".tmp/custom-session-budget.sqlite3",
        ),
    ],
)
def test_settings_reads_env_vars(
    monkeypatch: pytest.MonkeyPatch,
    env_name: str,
    env_value: str,
    attr: str,
    expected: str,
) -> None:
    _clear_app_env(monkeypatch)
    monkeypatch.setenv(env_name, env_value)
    s = Settings(_env_file=None)
    assert getattr(s, attr) == expected
