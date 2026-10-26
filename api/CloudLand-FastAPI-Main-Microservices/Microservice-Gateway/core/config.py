"""
Gateway configuration.

All environment-specific settings are loaded from environment variables /
.env file. No hardcoded service URLs, ports, or credentials.
"""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- App ---
    environment: str = Field(...)
    app_name: str = Field(default="cloudland-gateway")
    gateway_port: int = Field(...)

    # --- JWT (must match Authentication service exactly) ---
    jwt_secret_key: str = Field(...)
    jwt_issuer: str = Field(...)
    jwt_audience: str = Field(...)
    jwt_algorithm: str = Field(...)

    # --- CORS ---
    allowed_origins: str = Field(...)

    # --- Rate Limiting ---
    rate_limit_per_minute: int = Field(default=100)

    # --- Backend Services (all required — no hardcoded fallbacks) ---
    auth_service_url: str = Field(...)
    app_management_url: str = Field(...)
    storage_service_url: str = Field(...)
    background_task_url: str = Field(...)

    # --- Sentry ---
    sentry_dsn: str = Field(default="")
    sentry_traces_sample_rate: float = Field(default=1.0, ge=0.0, le=1.0)

    # --- Elasticsearch (audit logs) ---
    elasticsearch_url: str = Field(...)
    elasticsearch_username: str = Field(...)
    elasticsearch_password: str = Field(...)

    # --- Redis (caching) ---
    redis_host: str = Field(default="localhost")
    redis_port: int = Field(default=6379)
    redis_db: int = Field(default=0)

    # --- IP Geolocation ---
    ip_api_enabled: bool = Field(default=True)

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
