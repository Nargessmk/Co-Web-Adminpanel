"""
Sentry integration module.

Initializes the Sentry SDK with FastAPI-specific configuration.
Mirrors C# Exceptionless setup: captures unhandled exceptions,
performance traces, and integrates with the logging system.

Usage:
    from core.sentry import init_sentry
    init_sentry(settings)
"""

import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.logging import LoggingIntegration

from core.config import Settings


def _is_valid_dsn(dsn: str) -> bool:
    """Check if a DSN string looks like a real Sentry DSN.

    A valid DSN looks like: https://key@org_id.ingest.sentry.io/project_id
    The project_id part must be a numeric value, not a placeholder like 'project-id'.
    """
    if not dsn or not dsn.startswith("https://"):
        return False
    try:
        from urllib.parse import urlparse
        parsed = urlparse(dsn)
        path_parts = parsed.path.strip("/").split("/")
        if not path_parts or not path_parts[-1].isdigit():
            return False
        return True
    except Exception:
        return False


def init_sentry(settings: Settings) -> None:
    """
    Initialize Sentry SDK with configuration from environment.

    Should be called once at application startup, before any other
    code that might raise exceptions. Mirrors C# AddExceptionless().
    """
    if not _is_valid_dsn(settings.sentry_dsn):
        return

    sentry_logging = LoggingIntegration(
        level=None,
        event_level=None,
    )

    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        environment=settings.environment,
        release=f"{settings.app_name}@1.0.0",
        integrations=[
            FastApiIntegration(),
            sentry_logging,
        ],
        traces_sample_rate=settings.sentry_traces_sample_rate,
        send_default_pii=True,
    )
