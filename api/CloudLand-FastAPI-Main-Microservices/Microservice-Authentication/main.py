"""
Application entry point.

Wires together configuration, logging, FusionAuth SDK, middleware,
rate limiting, compression, and API routers. Run with:

    uvicorn main:app --reload --port 6202
"""

import sys
import os
from pathlib import Path

# Ensure root workspace directory is in sys.path so `Schema` can be imported
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from api.dependencies import get_fusionauth
from api.v1.auth import router as auth_router, protected_router as auth_protected_router
from api.v1.users import router as users_router
from api.v1.applications import router as applications_router
from api.v1.roles import router as roles_router
from api.v1.groups import router as groups_router
from core.config import get_settings
from core.logging import get_logger, setup_logging
from core.middleware import RequestLoggingMiddleware
from core.sentry import init_sentry
from middleware.audit import AuditLogger, AuditMiddleware, get_audit_logger, close_audit_logger
from middleware.exception_handler import global_exception_handler
from middleware.security import SecurityMiddleware
from services.cache import close_cache, get_cache
from services.fusionauth_client import FusionAuthSDKClient, close_fusionauth_client
from services.message_bus import close_message_bus, get_message_bus

settings = get_settings()
setup_logging(settings)
init_sentry(settings)
logger = get_logger(__name__)

limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    logger.info("Starting up | environment=%s", settings.environment)

    cache = get_cache()
    await cache.connect()

    audit = get_audit_logger(
        es_url=settings.elasticsearch_url,
        es_username=settings.elasticsearch_username,
        es_password=settings.elasticsearch_password,
        environment=settings.environment,
        index_prefix=settings.audit_index_prefix,
    )

    client = get_fusionauth()
    if await client.health_check():
        logger.info("FusionAuth connection verified successfully")
    else:
        logger.warning(
            "FusionAuth is not reachable at startup — the service will still "
            "boot, but auth-dependent endpoints will fail until connectivity is restored."
        )

    message_bus = get_message_bus()
    await message_bus.connect()

    yield

    logger.info("Shutting down — closing FusionAuth client, Redis, RabbitMQ, and audit logger")
    await close_fusionauth_client()
    await close_cache()
    await close_message_bus()
    await close_audit_logger()


app = FastAPI(
    title="Cloudland Authentication Microservice",
    description="Authentication microservice integrating FusionAuth as identity provider.",
    version="1.0.0",
    lifespan=lifespan,
)


# --- Custom OpenAPI with Bearer security scheme ---
_PUBLIC_PATHS = {
    "/api/health",
    "/api/v1/auth/login",
    "/api/v1/auth/login/two-factor",
    "/api/v1/auth/register",
    "/api/v1/auth/forgot-password",
    "/api/v1/auth/change-password",
    "/api/v1/auth/verify-security-questions",
    "/api/v1/users/",
}


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    from fastapi.openapi.utils import get_openapi

    schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    # --- Security scheme: only ours ---
    schema.setdefault("components", {})
    schema["components"]["securitySchemes"] = {
        "bearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }

    # --- Strip ALL per-route security FastAPI auto-generated ---
    # (FastAPI may create its own scheme name like "HTTPBearer" that doesn't match ours)
    for path, methods in schema.get("paths", {}).items():
        for method in ("get", "post", "put", "patch", "delete"):
            op = methods.get(method)
            if op and "security" in op:
                del op["security"]

    # --- Apply Bearer globally, then exempt public paths ---
    schema["security"] = [{"bearerAuth": []}]

    for path, methods in schema.get("paths", {}).items():
        canonical = path.rstrip("/") or path
        if canonical in _PUBLIC_PATHS:
            for method in ("get", "post", "put", "patch", "delete"):
                if method in methods:
                    methods[method]["security"] = []

    app.openapi_schema = schema
    return app.openapi_schema


app.openapi = custom_openapi

# --- Rate limiting ---
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# --- Global exception handler (mirrors C# GlobalExceptionHandler) ---
app.add_exception_handler(Exception, global_exception_handler)

# --- Middleware (order: last added = first to run) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type", "Accept", "X-CSRF-Token", "X-Request-ID"],
    expose_headers=["X-Request-ID"],
)
app.add_middleware(
    SecurityMiddleware,
    cookie_name=settings.csrf_cookie_name,
    header_name=settings.csrf_header_name,
)
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(
    AuditMiddleware,
    audit_logger=get_audit_logger(
        es_url=settings.elasticsearch_url,
        es_username=settings.elasticsearch_username,
        es_password=settings.elasticsearch_password,
        environment=settings.environment,
        index_prefix=settings.audit_index_prefix,
    ),
)


@app.get("/api/health", tags=["Health"], summary="Service health check")
async def health_check(client: FusionAuthSDKClient = Depends(get_fusionauth)) -> dict[str, object]:
    fusionauth_ok = await client.health_check()
    cache = get_cache()
    redis_ok = cache.is_connected
    message_bus = get_message_bus()
    rabbitmq_ok = message_bus.is_connected
    return {
        "status": "ok",
        "environment": settings.environment,
        "fusionauth_connected": fusionauth_ok,
        "redis_connected": redis_ok,
        "rabbitmq_connected": rabbitmq_ok,
        "elasticsearch_configured": bool(settings.elasticsearch_url),
    }


@app.get("/sentry-debug", tags=["Debug"], summary="Trigger Sentry error for testing")
async def trigger_error():
    division_by_zero = 1 / 0


# --- API Versioned Routers ---
app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication v1"])
app.include_router(auth_protected_router, prefix="/api/v1/auth", tags=["Authentication v1 (Protected)"])
app.include_router(users_router, prefix="/api/v1/users", tags=["Users v1"])
app.include_router(applications_router, prefix="/api/v1/applications", tags=["Applications v1"])
app.include_router(roles_router, prefix="/api/v1/applications", tags=["Roles v1"])
app.include_router(groups_router, prefix="/api/v1/groups", tags=["Groups v1"])
