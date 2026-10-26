"""
Structured logging configuration for the service.

This module is the single place where logging is configured. Every other
module should simply call `get_logger(__name__)` and use the standard
logging API — no other module should call logging.basicConfig() or
add handlers itself.

Behavior:
- development: human-readable, colorized-ish plain text to stdout.
- staging/production: single-line JSON to stdout, suitable for log
  aggregators (ELK, CloudWatch, Grafana Loki, etc.).

A per-request correlation ID (request_id) is attached via a context
variable so that every log line emitted while handling a request can be
tied back to that request, even across nested function calls.
"""

import json
import logging
import sys
import time
import uuid
from contextvars import ContextVar

import sentry_sdk
from sentry_sdk import capture_message, set_tag

from core.config import Settings

# Holds the current request's correlation ID for the duration of that request.
# Set by RequestLoggingMiddleware; read by JsonFormatter / TextFormatter.
request_id_ctx: ContextVar[str] = ContextVar("request_id", default="-")


class _RequestIdFilter(logging.Filter):
    """Injects the current request_id (if any) into every log record."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_ctx.get()
        return True


class JsonFormatter(logging.Formatter):
    """Renders each log record as a single-line JSON object."""

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": getattr(record, "request_id", "-"),
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


class TextFormatter(logging.Formatter):
    """Human-readable formatter used in local development."""

    def __init__(self) -> None:
        super().__init__(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | req=%(request_id)s | %(message)s",
            datefmt="%H:%M:%S",
        )


def setup_logging(settings: Settings) -> None:
    """
    Configure the root logger for the whole application.

    Call this once, at application startup, before any other logging occurs.
    Mirrors C# SerilogExtensions: console + Elasticsearch sink.
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO if settings.environment != "development" else logging.DEBUG)

    # Remove any handlers set up by imported libraries to avoid duplicate log lines.
    root_logger.handlers.clear()

    # --- Console handler (always present) ---
    handler = logging.StreamHandler(stream=sys.stdout)
    handler.addFilter(_RequestIdFilter())

    if settings.environment == "development":
        handler.setFormatter(TextFormatter())
    else:
        handler.setFormatter(JsonFormatter())

    root_logger.addHandler(handler)

    # --- Elasticsearch handler (like Serilog ES sink) ---
    if settings.elasticsearch_url:
        es_handler = ElasticsearchHandler(
            es_url=settings.elasticsearch_url,
            es_username=settings.elasticsearch_username,
            es_password=settings.elasticsearch_password,
            app_name=settings.app_name,
            environment=settings.environment,
        )
        es_handler.setLevel(logging.INFO)
        root_logger.addHandler(es_handler)

    # --- Sentry handler (like C# Exceptionless logging) ---
    if settings.sentry_dsn:
        sentry_handler = SentryHandler(level=logging.WARNING)
        root_logger.addHandler(sentry_handler)

    # Quiet down noisy third-party loggers unless we're debugging.
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Return a module-level logger.

    Usage:
        logger = get_logger(__name__)
        logger.info("User %s logged in", user_id)
    """
    return logging.getLogger(name)


def new_request_id() -> str:
    """Generate a short, unique correlation ID for a single request."""
    return uuid.uuid4().hex[:12]


class Timer:
    """Small helper for measuring elapsed time in milliseconds, used by the request logging middleware."""

    def __init__(self) -> None:
        self._start = time.perf_counter()

    def elapsed_ms(self) -> float:
        return round((time.perf_counter() - self._start) * 1000, 2)


class ElasticsearchHandler(logging.Handler):
    """
    Logging handler that ships WARNING+ logs to Elasticsearch.

    Mirrors C# SerilogExtensions ElasticsearchSink:
    - Index format: {app_name}-{environment}-{yyyy.MM}
    - Fire-and-forget with graceful degradation
    - Excludes DEBUG/INFO (only WARNING+ sent)
    """

    def __init__(
        self,
        es_url: str,
        es_username: str = "",
        es_password: str = "",
        app_name: str = "cloudland-auth",
        environment: str = "development",
    ) -> None:
        super().__init__(level=logging.WARNING)
        self._es_url = es_url.rstrip("/")
        self._es_username = es_username
        self._es_password = es_password
        self._app_name = app_name
        self._environment = environment
        self._client = None

    def _get_client(self):
        if self._client is None:
            import httpx
            auth = (self._es_username, self._es_password) if self._es_username else None
            self._client = httpx.Client(
                base_url=self._es_url,
                auth=auth,
                timeout=5.0,
            )
        return self._client

    def emit(self, record: logging.LogRecord) -> None:
        try:
            client = self._get_client()
            index = f"{self._app_name}-{self._environment}-{time.strftime('%Y.%m')}"
            doc = {
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                "level": record.levelname,
                "logger": record.name,
                "message": record.getMessage(),
                "request_id": getattr(record, "request_id", "-"),
            }
            if record.exc_info:
                doc["exception"] = logging.Formatter().formatException(record.exc_info)
            client.post(f"/{index}/_doc", json=doc)
        except Exception:
            pass


class SentryHandler(logging.Handler):
    """
    Logging handler that sends WARNING+ logs to Sentry.

    Mirrors C# Exceptionless logging integration:
    - Captures structured events with request_id
    - Sends exceptions with full traceback
    - Fire-and-forget with graceful degradation
    """

    def __init__(self, level: int = logging.WARNING) -> None:
        super().__init__(level=level)

    def emit(self, record: logging.LogRecord) -> None:
        try:
            request_id = getattr(record, "request_id", "-")
            set_tag("request_id", request_id)
            set_tag("logger", record.name)

            if record.exc_info and record.exc_info[0] is not None:
                with sentry_sdk.new_scope() as scope:
                    scope.set_tag("request_id", request_id)
                    scope.set_tag("logger", record.name)
                    scope.set_level(record.levelname)
                    sentry_sdk.capture_exception(record.exc_info[1])
            else:
                capture_message(
                    record.getMessage(),
                    level=record.levelname.lower(),
                )
        except Exception:
            self.handleError(record)