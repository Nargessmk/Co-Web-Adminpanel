"""
Structured logging with console output and optional Elasticsearch sink.

Mirrors C# SerilogExtensions.cs pattern.
"""

import logging
import time
from contextvars import ContextVar
from typing import Any

from core.config import Settings

request_id_ctx: ContextVar[str] = ContextVar("request_id", default="-")


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        import json
        log_entry: dict[str, Any] = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": request_id_ctx.get(),
        }
        if record.exc_info and record.exc_info[0]:
            log_entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_entry, default=str)


class ElasticsearchHandler(logging.Handler):
    """ES handler — mirrors C# Serilog ES sink.

    Filters out ERROR and CRITICAL (Fatal) logs from ES,
    matching the C# Serilog config:
    .Filter.ByExcluding(log => log.Level is LogEventLevel.Error or LogEventLevel.Fatal)
    """

    _EXCLUDED_LEVELS = {logging.ERROR, logging.CRITICAL}

    def __init__(self, es_url: str, username: str, password: str, index_prefix: str):
        super().__init__(level=logging.WARNING)
        self._es_url = es_url.rstrip("/")
        self._auth = (username, password)
        self._index_prefix = index_prefix

    def emit(self, record: logging.LogRecord) -> None:
        if record.levelno in self._EXCLUDED_LEVELS:
            return
        try:
            import httpx
            import time as _time

            index = f"{self._index_prefix}-{_time.strftime('%Y.%m')}"
            doc = {
                "timestamp": _time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                "level": record.levelname,
                "logger": record.name,
                "message": record.getMessage(),
                "request_id": request_id_ctx.get(),
            }
            if record.exc_info and record.exc_info[0]:
                doc["exception"] = logging.Formatter().formatException(record.exc_info)

            httpx.post(
                f"{self._es_url}/{index}/_doc",
                json=doc,
                auth=self._auth,
                timeout=5,
            )
        except Exception:
            pass


class RequestContextFilter(logging.Filter):
    """Inject request_id from context variable into every log record."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_ctx.get()
        return True


def setup_logging(settings: Settings) -> None:
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    ctx_filter = RequestContextFilter()

    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    console.setFormatter(logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | req=%(request_id)s | %(message)s",
        datefmt="%H:%M:%S",
    ))
    console.addFilter(ctx_filter)
    root.addHandler(console)

    if settings.elasticsearch_url:
        es_handler = ElasticsearchHandler(
            es_url=settings.elasticsearch_url,
            username=settings.elasticsearch_username,
            password=settings.elasticsearch_password,
            index_prefix=settings.app_name,
        )
        es_handler.addFilter(ctx_filter)
        root.addHandler(es_handler)


def new_request_id() -> str:
    import uuid
    return uuid.uuid4().hex[:12]


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


class Timer:
    def __init__(self):
        self._start = time.perf_counter()

    def elapsed_ms(self) -> float:
        return round((time.perf_counter() - self._start) * 1000, 2)
