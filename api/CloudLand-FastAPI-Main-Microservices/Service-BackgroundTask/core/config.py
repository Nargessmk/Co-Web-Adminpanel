import os
from functools import lru_cache
from typing import List, Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.env"))


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_PATH,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- App-level ---
    environment: str = Field(default="development")
    port: int = Field(default=6205)
    allowed_origins: str = Field(default="http://localhost:6201,http://localhost:6200")
    app_name: str = Field(default="cloudland-background-task")

    # --- Database ---
    database_url: str = Field(..., description="SQLAlchemy connection string")

    # --- JWT ---
    jwt_secret_key: str = Field(..., description="Secret key used to sign/verify JWT tokens")
    jwt_issuer: str = Field(default="APM_jwt", description="JWT Issuer claim")
    jwt_audience: str = Field(default="ailand.ai", description="JWT Audience claim")
    jwt_algorithm: str = Field(default="HS256", description="JWT Signing Algorithm")
    jwt_access_token_expiration_minutes: int = Field(default=30)
    jwt_refresh_token_expiration_days: int = Field(default=7)

    # --- Elasticsearch ---
    elasticsearch_url: str = Field(default="", description="Elasticsearch URL")
    elasticsearch_username: str = Field(default="", description="Elasticsearch username")
    elasticsearch_password: str = Field(default="", description="Elasticsearch password")

    # --- RabbitMQ ---
    rabbitmq_host: str = Field(..., description="RabbitMQ host")
    rabbitmq_port: int = Field(..., description="RabbitMQ port")
    rabbitmq_username: str = Field(..., description="RabbitMQ username")
    rabbitmq_password: str = Field(..., description="RabbitMQ password")
    rabbitmq_vhost: str = Field(..., description="RabbitMQ virtual host")

    # --- Sentry ---
    sentry_dsn: str = Field(default="")
    sentry_traces_sample_rate: float = Field(default=1.0, ge=0.0, le=1.0)

    # --- Redis ---
    redis_host: str = Field(default="localhost")
    redis_port: int = Field(default=6379)
    redis_db: int = Field(default=0)
    redis_password: Optional[str] = Field(default=None)
    redis_ssl: bool = Field(default=False)

    # --- Cron Schedule ---
    reindex_cron_day_of_week: str = Field(default="fri")
    reindex_cron_hour: int = Field(default=16)
    reindex_cron_minute: int = Field(default=0)

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, value: str) -> str:
        allowed = {"development", "staging", "production"}
        if value not in allowed:
            raise ValueError(f"environment must be one of {allowed}, got '{value}'")
        return value

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
