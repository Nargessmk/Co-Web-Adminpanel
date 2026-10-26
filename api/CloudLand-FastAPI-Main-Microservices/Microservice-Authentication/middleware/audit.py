"""
Audit logging middleware.

Logs authentication events (login, logout, register, password changes)
to Elasticsearch for security auditing. Mirrors the C# AuditExtensions
Elasticsearch sink pattern.
"""

from __future__ import annotations

import logging
import time
from datetime import datetime, timezone
from typing import Any

import httpx
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("audit")


class AuditLogEntry:
    """Structured audit log entry for auth events."""

    def __init__(
        self,
        event_type: str,
        user_id: str | None = None,
        ip_address: str | None = None,
        path: str = "",
        method: str = "",
        status_code: int = 0,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.timestamp = datetime.now(timezone.utc).isoformat()
        self.event_type = event_type
        self.user_id = user_id
        self.ip_address = ip_address
        self.path = path
        self.method = method
        self.status_code = status_code
        self.details = details or {}

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "event_type": self.event_type,
            "user_id": self.user_id,
            "ip_address": self.ip_address,
            "path": self.path,
            "method": self.method,
            "status_code": self.status_code,
            "details": self.details,
        }


class AuditLogger:
    """Send audit events to Elasticsearch."""

    def __init__(
        self,
        es_url: str = "",
        es_username: str = "",
        es_password: str = "",
        index_prefix: str = "cloudland-auth-audit",
        environment: str = "development",
    ) -> None:
        self._es_url = es_url.rstrip("/")
        self._es_username = es_username
        self._es_password = es_password
        self._index = f"{index_prefix}-{environment}"
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient | None:
        if not self._es_url:
            return None
        if self._client is None:
            auth = (self._es_username, self._es_password) if self._es_username else None
            self._client = httpx.AsyncClient(
                base_url=self._es_url,
                auth=auth,
                timeout=5.0,
            )
        return self._client

    async def log(self, entry: AuditLogEntry) -> None:
        """Send an audit entry to Elasticsearch (fire-and-forget)."""
        client = await self._get_client()
        if not client:
            logger.info("AUDIT: %s", entry.to_dict())
            return
        try:
            await client.post(
                f"/{self._index}/_doc",
                json=entry.to_dict(),
            )
        except Exception as exc:
            logger.warning("Audit log to ES failed: %s", exc)
            logger.info("AUDIT (fallback): %s", entry.to_dict())

    async def close(self) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None


# Auth event paths to audit
_AUTH_EVENT_PATHS = {
    "/api/v1/auth/login": "login",
    "/api/v1/auth/login/two-factor": "login_2fa",
    "/api/v1/auth/logout": "logout",
    "/api/v1/auth/register": "register",
    "/api/v1/auth/forgot-password": "forgot_password",
    "/api/v1/auth/change-password": "change_password",
    "/api/v1/auth/reset-password": "reset_password",
    "/api/v1/auth/verify-security-questions": "verify_security_questions",
}


class AuditMiddleware(BaseHTTPMiddleware):
    """ASGI middleware that captures auth events and sends them to Elasticsearch."""

    def __init__(self, app: Any, audit_logger: AuditLogger) -> None:
        super().__init__(app)
        self._audit = audit_logger

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        start = time.monotonic()
        response = await call_next(request)
        duration_ms = round((time.monotonic() - start) * 1000, 1)

        path = request.url.path
        event_type = _AUTH_EVENT_PATHS.get(path)

        if event_type:
            client_ip = request.headers.get("x-forwarded-for", "")
            if not client_ip and request.client:
                client_ip = request.client.host

            entry = AuditLogEntry(
                event_type=event_type,
                ip_address=client_ip,
                path=path,
                method=request.method,
                status_code=response.status_code,
                details={"duration_ms": duration_ms},
            )
            await self._audit.log(entry)

        return response


# ---------------------------------------------------------------------------
# Singleton management
# ---------------------------------------------------------------------------

_audit_logger: AuditLogger | None = None


def get_audit_logger(
    es_url: str = "",
    es_username: str = "",
    es_password: str = "",
    environment: str = "development",
    index_prefix: str = "cloudland-auth-audit",
) -> AuditLogger:
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = AuditLogger(
            es_url=es_url,
            es_username=es_username,
            es_password=es_password,
            index_prefix=index_prefix,
            environment=environment,
        )
    return _audit_logger


async def close_audit_logger() -> None:
    global _audit_logger
    if _audit_logger is not None:
        await _audit_logger.close()
        _audit_logger = None
