import time
from typing import Any

from core.logging import get_logger
from core.mediator import IPipelineBehavior, Request

logger = get_logger(__name__)


class LoggingBehavior(IPipelineBehavior):
    async def handle(self, request: Request, next_handler) -> Any:
        request_name = type(request).__name__
        start = time.perf_counter()
        logger.info("Handling %s", request_name)
        try:
            response = await next_handler(request)
        except Exception as exc:
            logger.error("Handled %s with error: %s", request_name, exc)
            raise
        elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
        logger.info("Handled %s in %s ms", request_name, elapsed_ms)
        return response
