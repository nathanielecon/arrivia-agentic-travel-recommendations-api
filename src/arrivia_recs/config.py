from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "arrivia-agentic-travel-recs"
    app_env: str = "local"
    member_service_base_url: str = "http://member-service:8081"
    partner_config_base_url: str = "http://partner-config-service:8082"
    session_budget_store_path: str = ".data/session_budget.sqlite3"
    session_budget_ttl_seconds: int = Field(default=1800, ge=1)
    session_budget_max_sessions: int = Field(default=10_000, ge=1)
    upstream_connect_timeout_seconds: float = Field(default=0.25, gt=0)
    upstream_read_timeout_seconds: float = Field(default=1.0, gt=0)
    upstream_write_timeout_seconds: float = Field(default=0.25, gt=0)
    upstream_pool_timeout_seconds: float = Field(default=0.25, gt=0)
    upstream_circuit_failure_threshold: int = Field(default=3, ge=1)
    upstream_circuit_open_seconds: float = Field(default=30.0, gt=0)
    metrics_enabled: bool = True
    log_level: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
