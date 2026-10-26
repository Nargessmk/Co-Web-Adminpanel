"""
Request/response logging middleware.

Mirrors C# LogRequestResponseFilter.cs — logs IP, path, method, status, duration.
"""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from core.logging import Timer, get_logger, new_request_id, request_id_ctx

logger = get_logger("app.request")


def get_client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


class RequestLoggingMiddleware(BaseHTTPMiddleware):
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
                request.method, request.url.path, client_ip,
            )
            raise
        finally:
            request_id_ctx.reset(token)

        response.headers["X-Request-ID"] = request_id
        logger.info(
            "method=%s path=%s status=%s duration_ms=%s client_ip=%s",
            request.method, request.url.path, response.status_code,
            timer.elapsed_ms(), client_ip,
        )
        return response
