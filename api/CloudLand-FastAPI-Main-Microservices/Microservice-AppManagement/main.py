import os
import sys

# Ensure system proxy environment variables do not hijack microservice connections
for _proxy_env in ["HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "http_proxy", "https_proxy"]:
    os.environ.pop(_proxy_env, None)
os.environ["NO_PROXY"] = "*"

from pathlib import Path
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse

from api.v1.constants import router as constants_router
from api.v1.calendars import router as calendars_router
from api.v1.permissions import router as permissions_router
from api.v1.reindex import router as reindex_router
from api.v1.entity_file_attachments import router as entity_file_attachments_router
from api.v1.module_permissions import router as module_permissions_router
from core.config import get_settings
from core.logging import get_logger, setup_logging
from core.sentry import init_sentry
from core.mediator import get_mediator
from application.behaviors.logging_behavior import LoggingBehavior
from application.registry import register_all_handlers
from middleware.exception_handler import global_exception_handler
from middleware.uow_middleware import UoWMiddleware
from core.exceptions import AppManagementError, NotFoundError
from Structure.session import get_db_manager
from services.rabbitmq_consumer import launch_consumer_task, stop_consumer_task

settings = get_settings()
setup_logging(settings)
init_sentry(settings)
logger = get_logger(__name__)  # AppManagement service logger


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    logger.info("Starting up | environment=%s", settings.environment)

    db_manager = get_db_manager(settings.database_url)
    await db_manager.create_tables()

    mediator = get_mediator()
    mediator.add_behavior(LoggingBehavior())
    register_all_handlers(mediator)

    launch_consumer_task()

    yield

    logger.info("Shutting down")
    stop_consumer_task()
    await db_manager.close()


app = FastAPI(
    title="Cloudland App Management Microservice",
    description="Manages constants, calendar, and permissions for Cloudland applications.",
    version="1.0.0",
    lifespan=lifespan,
)

db_manager = get_db_manager(settings.database_url)

app.add_exception_handler(Exception, global_exception_handler)


from fastapi.encoders import jsonable_encoder


def _clean_error_obj(obj):
    if isinstance(obj, bytes):
        return obj.decode("utf-8", errors="replace")
    elif isinstance(obj, dict):
        return {k: _clean_error_obj(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [_clean_error_obj(x) for x in obj]
    return obj


@app.exception_handler(AppManagementError)
async def app_management_exception_handler(request: Request, exc: AppManagementError):
    status_code = exc.status_code or 400
    if isinstance(exc, NotFoundError):
        status_code = 404
    return JSONResponse(
        status_code=status_code,
        content={
            "status": status_code,
            "title": str(exc.message or exc),
            "detail": str(exc.message or exc),
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    cleaned_errors = _clean_error_obj(exc.errors())
    return JSONResponse(
        status_code=400,
        content={
            "status": 400,
            "title": "خطا در اعتبارسنجی اطلاعات ارسالی",
            "model": jsonable_encoder(cleaned_errors),
            "message": "اطلاعات ارسالی نامعتبر است",
        },
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type", "Accept", "X-CSRF-Token", "X-Request-ID"],
    expose_headers=["X-Request-ID"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(UoWMiddleware, db_manager=db_manager)


@app.get("/api/health", tags=["Health"], summary="Service health check")
async def health_check() -> dict[str, object]:
    return {
        "status": "ok",
        "environment": settings.environment,
    }


@app.get("/sentry-debug", tags=["Debug"], summary="Trigger Sentry error for testing")
async def trigger_error():
    division_by_zero = 1 / 0


app.include_router(constants_router, prefix="/api/v1/constant", tags=["Constants v1"])
app.include_router(calendars_router, prefix="/api/v1/calendar", tags=["Calendars v1"])
app.include_router(permissions_router, prefix="/api/v1/ConstantPermission", tags=["Permissions v1"])
app.include_router(reindex_router, prefix="/api/v1/Reindex", tags=["Reindex v1"])
app.include_router(entity_file_attachments_router, prefix="/api/v1/entity-file-attachments", tags=["File Attachments v1"])
app.include_router(module_permissions_router, prefix="/api/v1/module-permissions", tags=["Module Permissions v1"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=6203, reload=True)