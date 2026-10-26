"""
Application configuration module.

Loads and validates all environment-based settings using Pydantic Settings.
This is the single source of truth for configuration across the service —
no other module should call os.getenv() directly.
"""

from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Centralized application settings, loaded from environment variables
    or a .env file.

    Field names below are lowercase (PEP 8 convention for Python attributes).
    pydantic-settings automatically matches them against uppercase env var
    names (e.g. field `fusionauth_base_url` <-> env var `FUSIONAUTH_BASE_URL`)
    as long as case_sensitive is left at its default (False).
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        # NOTE: case_sensitive is intentionally NOT set to True.
        # Leaving it at the default (False) lets pydantic-settings match
        # lowercase field names to uppercase .env variable names.
    )

    # --- FusionAuth ---
    fusionauth_base_url: str = Field(..., description="Base URL of the FusionAuth instance")
    fusionauth_api_key: str = Field(..., description="Server-side API key for FusionAuth")

    # --- JWT (issued by this microservice) ---
    jwt_secret_key: str = Field(..., description="Secret key used to sign JWT access tokens")
    jwt_issuer: str = Field(..., description="JWT issuer claim (iss)")
    jwt_audience: str = Field(..., description="JWT audience claim (aud)")
    jwt_algorithm: str = Field(..., description="Signing algorithm for JWTs issued by this service")
    access_token_expire_minutes: int = Field(default=30, gt=0)
    refresh_token_expire_days: int = Field(default=7, gt=0)

    # --- Redis ---
    redis_host: str = Field(default="localhost", description="Redis host")
    redis_port: int = Field(default=6379, description="Redis port")
    redis_db: int = Field(default=0, description="Redis database number")
    redis_password: str | None = Field(default=None, description="Redis password")
    redis_ssl: bool = Field(default=False, description="Use SSL for Redis connection")

    # --- Elasticsearch (audit logging + Serilog sink) ---
    elasticsearch_url: str = Field(default="", description="Elasticsearch URL for audit logs and Serilog sink")
    elasticsearch_username: str = Field(default="", description="Elasticsearch username")
    elasticsearch_password: str = Field(default="", description="Elasticsearch password")

    # --- RabbitMQ (MassTransit message bus) ---
    rabbitmq_host: str = Field(..., description="RabbitMQ host")
    rabbitmq_port: int = Field(..., description="RabbitMQ port")
    rabbitmq_username: str = Field(..., description="RabbitMQ username")
    rabbitmq_password: str = Field(..., description="RabbitMQ password")
    rabbitmq_vhost: str = Field(..., description="RabbitMQ virtual host")

    # --- App-level ---
    environment: str = Field(default="development")
    port: int = Field(default=6202)
    allowed_origins: str = Field(default="http://localhost:3000")
    app_name: str = Field(default="cloudland-auth", description="Application name for log indices")

    # --- Elasticsearch audit ---
    audit_index_prefix: str = Field(default="cloudland-auth-audit", description="ES index prefix for audit logs")

    # --- File upload ---
    upload_path: str = Field(default="uploads/profile-images", description="Directory for profile image uploads")
    upload_base_url: str = Field(default="/uploads/profile-images", description="Base URL path for uploaded images")
    upload_allowed_extensions: str = Field(default=".jpg,.jpeg,.png,.gif", description="Allowed file extensions")
    upload_max_file_size_mb: int = Field(default=5, description="Max file size in MB")

    # --- Sentry (error tracking) ---
    sentry_dsn: str = Field(default="", description="Sentry DSN for error tracking")
    sentry_traces_sample_rate: float = Field(default=1.0, ge=0.0, le=1.0, description="Sentry performance tracing sample rate")

    # --- CSRF Protection ---
    csrf_cookie_name: str = Field(default="csrftoken", description="Name of the CSRF cookie")
    csrf_header_name: str = Field(default="X-CSRF-Token", description="Header name for CSRF token")
    csrf_token_length: int = Field(default=32, description="Length of generated CSRF tokens")

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, value: str) -> str:
        """Ensure environment is one of the recognized deployment stages."""
        allowed = {"development", "staging", "production"}
        if value not in allowed:
            raise ValueError(f"environment must be one of {allowed}, got '{value}'")
        return value

    @property
    def cors_origins_list(self) -> list[str]:
        """Return ALLOWED_ORIGINS as a clean list of origin strings."""
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    """
    Return a cached Settings instance.

    Using lru_cache ensures the .env file is parsed only once per process,
    and the same Settings object is reused everywhere via dependency injection.
    """
    return Settings()