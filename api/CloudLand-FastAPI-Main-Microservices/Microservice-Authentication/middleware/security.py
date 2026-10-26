"""
Security middleware providing CSRF protection and security response headers.

CSRF Protection (double-submit cookie pattern):
- Validates X-CSRF-Token header against csrftoken cookie on state-changing requests
- Only applies to cookie-authenticated endpoints (refresh, logout)
- Bearer-only endpoints are not affected (browser doesn't auto-attach Bearer tokens)

Security Headers:
- Strict-Transport-Security (HSTS)
- X-Content-Type-Options
- X-Frame-Options
- X-XSS-Protection
- Referrer-Policy
- Permissions-Policy
"""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from core.logging import get_logger
from core.security import validate_csrf_token

logger = get_logger("app.security")

# HTTP methods that change state and need CSRF validation
_STATE_CHANGING_METHODS = frozenset({"POST", "PUT", "PATCH", "DELETE"})


class SecurityMiddleware(BaseHTTPMiddleware):
    """Combines CSRF validation and security response headers."""

    def __init__(self, app, *, cookie_name: str, header_name: str):
        super().__init__(app)
        self._cookie_name = cookie_name
        self._header_name = header_name

    async def dispatch(self, request: Request, call_next) -> Response:
        # --- CSRF validation (before response) ---
        if request.method in _STATE_CHANGING_METHODS:
            cookie_val = request.cookies.get(self._cookie_name)
            header_val = request.headers.get(self._header_name)

            if cookie_val and not validate_csrf_token(cookie_val, header_val):
                logger.warning(
                    "CSRF token mismatch | method=%s path=%s client_ip=%s",
                    request.method,
                    request.url.path,
                    request.client.host if request.client else "unknown",
                )
                return Response(
                    content='{"detail":"CSRF token missing or invalid"}',
                    status_code=403,
                    media_type="application/json",
                )

        response = await call_next(request)

        # --- Security headers (after response) ---
        response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"

        return response
