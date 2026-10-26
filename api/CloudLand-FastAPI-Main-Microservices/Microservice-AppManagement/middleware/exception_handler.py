from fastapi import Request
from fastapi.responses import JSONResponse

from core.logging import get_logger

logger = get_logger(__name__)


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error(
        "Unhandled exception | path=%s | method=%s | error=%s",
        request.url.path,
        request.method,
        str(exc),
        exc_info=True,
    )
    return JSONResponse(
        status_code=500,
        content={
            "status": 500,
            "title": "Server error",
        },
    )
