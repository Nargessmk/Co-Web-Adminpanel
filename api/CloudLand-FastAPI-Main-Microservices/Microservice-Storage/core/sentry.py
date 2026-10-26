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
        if not path_parts or not path_parts[-1].isdigit():
            return False
        return True
    except Exception:
        return False


def init_sentry(settings: Settings) -> None:
    if not _is_valid_dsn(settings.sentry_dsn):
        return

    import logging
    # Mute urllib3 connection pool retry warnings (e.g. proxy 127.0.0.1:10808 failures)
    logging.getLogger("urllib3.connectionpool").setLevel(logging.ERROR)

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
        http_proxy=None,
        https_proxy=None,
    )
