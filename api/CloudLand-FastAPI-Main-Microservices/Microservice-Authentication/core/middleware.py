"""
ASGI middleware for structured request/response logging.

Logs one line per incoming request with method, path, status code,
elapsed time, and client IP — and attaches a correlation ID (request_id)
that is also returned to the client via the X-Request-ID response header,
so a user-reported issue can be traced back to the exact log line.
"""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from core.logging import Timer, get_logger, new_request_id, request_id_ctx

logger = get_logger("app.request")


def get_client_ip(request: Request) -> str:
    """
    Resolve the real client IP, honoring the X-Forwarded-For header
    when the service sits behind a reverse proxy or load balancer.
    """
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Logs every request/response pair and propagates a correlation ID."""

    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = new_request_id()
        token = request_id_ctx.set(request_id)
        timer = Timer()
        client_ip = get_client_ip(request)

        try:
            response = await call_next(request)
        except Exception:
            logger.exception(
                "Unhandled exception | method=%s path=%s client_ip=%s",
                request.method,
                request.url.path,
                client_ip,
            )
            raise
        finally:
            request_id_ctx.reset(token)

        response.headers["X-Request-ID"] = request_id
        logger.info(
            "method=%s path=%s status=%s duration_ms=%s client_ip=%s",
            request.method,
            request.url.path,
            response.status_code,
            timer.elapsed_ms(),
            client_ip,
        )
        return response