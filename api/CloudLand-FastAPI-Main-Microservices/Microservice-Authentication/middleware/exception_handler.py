"""
Global exception handler for unhandled exceptions.

Mirrors C# GlobalExceptionHandler (ExceptionHandlingMiddleware.cs):
- Logs the exception
- Sends it to Sentry
- Returns a 500 ProblemDetails JSON response

This handler catches exceptions that escape all middleware and route
handlers, providing a consistent error response format.
"""

import sentry_sdk
from fastapi import Request
from fastapi.responses import JSONResponse

from core.logging import get_logger

logger = get_logger("app.exception_handler")


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle uncaught exceptions globally.

    Mirrors C# pattern:
    1. Log the exception
    2. Capture in Sentry
    3. Return 500 ProblemDetails
    """
    logger.error(
        "Unhandled exception | method=%s path=%s | %s: %s",
        request.method,
        request.url.path,
        type(exc).__name__,
        str(exc),
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
