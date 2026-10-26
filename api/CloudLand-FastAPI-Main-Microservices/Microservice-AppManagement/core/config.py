from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- Database ---
    database_url: str = Field(description="SQL Server connection string (mssql+aioodbc://...)")

    # --- App-level ---
    environment: str = Field(default="development")
    port: int = Field(default=6203)
    allowed_origins: str = Field(default="http://localhost:3000")
    app_name: str = Field(default="cloudland-app-management", description="Application name for log indices")

    # --- Sentry ---
    sentry_dsn: str = Field(default="", description="Sentry DSN for error tracking")
    sentry_traces_sample_rate: float = Field(default=1.0, ge=0.0, le=1.0)

    # --- Elasticsearch audit ---
    elasticsearch_url: str = Field(default="", description="Elasticsearch URL for audit logs")
    elasticsearch_username: str = Field(default="", description="Elasticsearch username")
    elasticsearch_password: str = Field(default="", description="Elasticsearch password")
    audit_index_prefix: str = Field(default="cloudland-app-management-audit")

    # --- Redis ---
    redis_host: str = Field(default="localhost")
    redis_port: int = Field(default=6379)
    redis_db: int = Field(default=0)
    redis_password: str | None = Field(default=None)
    redis_ssl: bool = Field(default=False)

    # --- RabbitMQ ---
    rabbitmq_host: str = Field(..., description="RabbitMQ host")
    rabbitmq_username: str = Field(..., description="RabbitMQ username")
    rabbitmq_password: str = Field(..., description="RabbitMQ password")

    # --- Cron Schedule ---
    reindex_cron_day_of_week: str = Field(default="fri")
    reindex_cron_hour: int = Field(default=16)
    reindex_cron_minute: int = Field(default=0)

    # --- Constants cache (مطابق ConstantsCache در appsettings) ---
    constants_cache_allowed_root_ids: str = Field(default="", description="Comma-separated RootIds eligible for caching")
    constants_cache_expiration_minutes: int = Field(default=30)

    # --- Calendar cache ---
    calendar_cache_expiration_minutes: int = Field(default=1440)

    # --- JWT (JwtSettings در نمونه C#) ---
    jwt_secret_key: str = Field(default="change-me-in-production")
    jwt_issuer: str = Field(default="APM_jwt")
    jwt_audience: str = Field(default="ailand.ai")
    jwt_access_token_expiration_minutes: int = Field(default=30)
    jwt_refresh_token_expiration_days: int = Field(default=7)

    # --- FusionAuth ---
    fusionauth_api_key: str = Field(default="")
    fusionauth_auth_url: str = Field(default="")

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, value: str) -> str:
        allowed = {"development", "staging", "production"}
        if value not in allowed:
            raise ValueError(f"environment must be one of {allowed}, got '{value}'")
        return value

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]

    @property
    def constants_cache_allowed_root_ids_list(self) -> list[str]:
        return [rid.strip() for rid in self.constants_cache_allowed_root_ids.split(",") if rid.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()