"""Sentry integration — mirrors Authentication microservice pattern."""

import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.logging import LoggingIntegration

from core.config import Settings


def _is_valid_dsn(dsn: str) -> bool:
    if not dsn or not dsn.startswith("https://"):
        return False
    try:
        from urllib.parse import urlparse
        parsed = urlparse(dsn)
        path_parts = parsed.path.strip("/").split("/")
        return bool(path_parts) and path_parts[-1].isdigit()
    except Exception:
        return False


def init_sentry(settings: Settings) -> None:
    if not _is_valid_dsn(settings.sentry_dsn):
        return

    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        environment=settings.environment,
        release=f"{settings.app_name}@1.0.0",
        integrations=[
            FastApiIntegration(),
            LoggingIntegration(level=None, event_level=None),
        ],
        traces_sample_rate=settings.sentry_traces_sample_rate,
        send_default_pii=True,
    )
