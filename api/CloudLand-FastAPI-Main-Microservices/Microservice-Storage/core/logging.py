import json
import logging
import sys
import time
import uuid
from contextvars import ContextVar
import sentry_sdk
from sentry_sdk import capture_message, set_tag
from core.config import Settings

request_id_ctx: ContextVar[str] = ContextVar("request_id", default="-")


class _RequestIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_ctx.get()
        return True


class JsonFormatter(logging.Formatter):
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
    def __init__(self) -> None:
        super().__init__(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | req=%(request_id)s | %(message)s",
            datefmt="%H:%M:%S",
        )


def setup_logging(settings: Settings) -> None:
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO if settings.environment != "development" else logging.DEBUG)
    root_logger.handlers.clear()

    handler = logging.StreamHandler(stream=sys.stdout)
    handler.addFilter(_RequestIdFilter())

    if settings.environment == "development":
        handler.setFormatter(TextFormatter())
    else:
        handler.setFormatter(JsonFormatter())

    root_logger.addHandler(handler)

    if settings.sentry_dsn:
        sentry_handler = SentryHandler(level=logging.WARNING)
        root_logger.addHandler(sentry_handler)

    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("botocore").setLevel(logging.WARNING)
    logging.getLogger("aiobotocore").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


class SentryHandler(logging.Handler):
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
                    level_name = record.levelname.lower()
                    if level_name in {"fatal", "critical", "error", "warning", "info", "debug"}:
                        scope.set_level(level_name)  # type: ignore[arg-type]
                    sentry_sdk.capture_exception(record.exc_info[1])
            else:
                level_name = record.levelname.lower()
                if level_name in {"fatal", "critical", "error", "warning", "info", "debug"}:
                    capture_message(record.getMessage(), level=level_name)  # type: ignore[arg-type]
        except Exception:
            self.handleError(record)
