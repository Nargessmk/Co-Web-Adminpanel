"""Global exception handler — mirrors C# ExceptionHandlingMiddleware."""

import sentry_sdk
from fastapi import Request
from fastapi.responses import JSONResponse

from core.logging import get_logger

logger = get_logger("app.exception_handler")


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error(
        "Unhandled exception | method=%s path=%s | %s: %s",
        request.method, request.url.path,
        type(exc).__name__, str(exc),
        exc_info=True,
    )
    sentry_sdk.capture_exception(exc)
    return JSONResponse(
        status_code=500,
        content={
            "type": "https://tools.ietf.org/html/rfc7807",
            "title": "Server error",
            "status": 500,
            "detail": "An unexpected error occurred.",
        },
    )
