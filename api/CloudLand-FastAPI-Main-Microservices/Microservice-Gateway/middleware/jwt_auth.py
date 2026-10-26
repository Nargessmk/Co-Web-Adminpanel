"""
JWT validation middleware for the API Gateway.

Performs lightweight JWT verification at the gateway layer before proxying
requests to backend services. This provides defense-in-depth by rejecting
invalid/expired tokens early, while still allowing each microservice to
perform its own authorization checks.

Public paths (no JWT required):
- /auth/* (login, register, forgot-password, etc.)
- /docs, /scalar, /openapi.json (API documentation)
- /gateway-service-status (health check)
- /sentry-debug (debug endpoint)
- /ws (WebSocket)
"""

import logging
from typing import Callable

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from jose import JWTError, jwt

from core.config import get_settings

logger = logging.getLogger(__name__)

_PUBLIC_PATHS = {
    "/docs",
    "/scalar",
    "/openapi.json",
    "/gateway-service-status",
    "/sentry-debug",
    "/ws",
    "/api/health",
    "/background-tasks-service-status",
    "/storage/health",
}

_PUBLIC_PREFIXES = [
    "/auth/",
]


def _is_public_path(path: str) -> bool:
    if path in _PUBLIC_PATHS:
        return True
    for prefix in _PUBLIC_PREFIXES:
        if path.startswith(prefix):
            return True
    return False


class JWTAuthMiddleware:
    """Validate JWT tokens at the gateway level."""

    def __init__(self, app: Callable) -> None:
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        request = Request(scope, receive=receive)
        path = request.url.path

        if scope["method"] == "OPTIONS":
            return await self.app(scope, receive, send)

        if _is_public_path(path):
            return await self.app(scope, receive, send)

        authorization = request.headers.get("authorization", "")
        if not authorization.startswith("Bearer "):
            response = JSONResponse(
                status_code=401,
                content={"detail": "Missing or invalid Authorization header"},
            )
            return await response(scope, receive, send)

        token = authorization[7:].strip()
        if not token:
            response = JSONResponse(
                status_code=401,
                content={"detail": "Missing or invalid Authorization header"},
            )
            return await response(scope, receive, send)

        settings = get_settings()
        try:
            payload = jwt.decode(
                token,
                settings.jwt_secret_key,
                algorithms=[settings.jwt_algorithm],
                issuer=settings.jwt_issuer,
                audience=settings.jwt_audience,
            )
            scope["jwt_payload"] = payload
        except JWTError as exc:
            logger.warning("Gateway JWT validation failed for %s: %s", path, exc)
            response = JSONResponse(
                status_code=401,
                content={"detail": "Invalid or expired token"},
            )
            return await response(scope, receive, send)

        return await self.app(scope, receive, send)
