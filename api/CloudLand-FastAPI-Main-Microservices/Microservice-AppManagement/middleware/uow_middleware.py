from contextvars import ContextVar
from uuid import UUID

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from Structure.session import DatabaseManager, UnitOfWork
from core.logging import get_logger

logger = get_logger(__name__)

_uow_ctx: ContextVar[UnitOfWork | None] = ContextVar("uow", default=None)


def get_current_uow() -> UnitOfWork:
    uow = _uow_ctx.get()
    if uow is None:
        raise RuntimeError("UnitOfWork is not available outside a request context")
    return uow


class UoWMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, db_manager: DatabaseManager):
        super().__init__(app)
        self._db_manager = db_manager

    async def dispatch(self, request: Request, call_next) -> Response:
        application_id = None
        app_id_header = request.headers.get("ApplicationID") or request.headers.get("Application-ID")
        if app_id_header:
            try:
                application_id = UUID(app_id_header)
            except ValueError:
                application_id = None
                logger.warning(
                    "Application ID header was invalid: '%s'", app_id_header
                )

        async with self._db_manager.get_uow(application_id) as uow:
            token = _uow_ctx.set(uow)
            request.state.uow = uow
            try:
                response = await call_next(request)
                return response
            finally:
                _uow_ctx.reset(token)
