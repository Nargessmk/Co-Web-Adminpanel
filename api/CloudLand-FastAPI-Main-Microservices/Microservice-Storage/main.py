import asyncio
import sys
import os

# Ensure system proxy environment variables (e.g. VPN/v2ray on port 10808) do not hijack microservice connections
for _proxy_env in ["HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "http_proxy", "https_proxy"]:
    os.environ.pop(_proxy_env, None)
os.environ["NO_PROXY"] = "*"

from contextlib import asynccontextmanager
from fastapi import FastAPI, Query, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse

# Ensure root workspace directory is in sys.path so `Schema` can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from core.config import get_settings
from core.db import init_db, check_db_connection, close_db
from core.logging import get_logger, setup_logging
from core.sentry import init_sentry
from core.s3 import check_s3_connection
from services.cache import get_cache, close_cache
from middleware.audit import get_audit_logger, close_audit_logger, StorageAuditMiddleware
from api.v1.buckets import router as buckets_router
from api.v1.buckets_objects import router as buckets_objects_router
from api.v1.nas import router as nas_router

settings = get_settings()
setup_logging(settings)
init_sentry(settings)
logger = get_logger(__name__)


async def _startup_check_db():
    if settings.database_url:
        init_db(settings.database_url)
        try:
            connected = await asyncio.wait_for(check_db_connection(), timeout=10.0)
            if connected:
                logger.info("PostgreSQL connection: OK")
            else:
                logger.warning("PostgreSQL connection check failed on startup")
        except Exception as e:
            logger.warning(f"PostgreSQL connection check exception: {str(e)}")
    else:
        logger.warning("database_url not set — Storage running without a database")


async def _startup_check_bg():
    try:
        connected = await asyncio.wait_for(check_s3_connection(), timeout=4.0)
        if connected:
            logger.info("MinIO S3 connection: OK")
        else:
            logger.warning("MinIO S3 connection check failed on startup")
    except Exception as e:
        logger.warning(f"MinIO S3 connection check exception: {str(e)}")


from services.message_bus import get_storage_message_bus, close_storage_message_bus

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up Storage Microservice | environment=%s", settings.environment)
    
    # Initialize Redis connection
    cache = get_cache()
    await cache.connect()
    
    # Initialize RabbitMQ Message Bus
    msg_bus = get_storage_message_bus()
    await msg_bus.connect()
    await msg_bus.start_reconnect_task()

    # Initialize Audit Logger
    get_audit_logger(
        es_url=settings.elasticsearch_url,
        es_username=settings.elasticsearch_username,
        es_password=settings.elasticsearch_password,
        environment=settings.environment,
        index_prefix=settings.audit_index_prefix,
    )

    # Launch startup checks in background so application startup never blocks/hangs
    asyncio.create_task(_startup_check_bg())
    asyncio.create_task(_startup_check_db())
    
    yield
    
    logger.info("Shutting down Storage Microservice...")
    await close_cache()
    await close_storage_message_bus()
    await close_audit_logger()
    await close_db()


app = FastAPI(
    title="Cloudland Storage Microservice",
    description="Storage Microservice integrated with MinIO S3 Server & NAS SFTP",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    StorageAuditMiddleware,
    audit_logger=get_audit_logger(
        es_url=settings.elasticsearch_url,
        es_username=settings.elasticsearch_username,
        es_password=settings.elasticsearch_password,
        environment=settings.environment,
        index_prefix=settings.audit_index_prefix,
    ),
)

# Include Routers
app.include_router(buckets_router)
app.include_router(buckets_objects_router)
app.include_router(nas_router)


from fastapi.openapi.utils import get_openapi

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "HTTPBearer": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Enter your JWT Bearer token",
        }
    }
    # Apply security globally to endpoints (except health)
    for path, path_item in openapi_schema.get("paths", {}).items():
        if path != "/api/health":
            for method in path_item:
                if method in ["get", "post", "put", "patch", "delete"]:
                    path_item[method].setdefault("security", [{"HTTPBearer": []}])

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi


# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": str(exc), "status_code": 500},
    )


@app.get("/api/health", tags=["Health"])
async def health_check():
    cache = get_cache()
    redis_ok = cache.is_connected
    db_ok = await check_db_connection()
    return {
        "status": "ok",
        "environment": settings.environment,
        "service": settings.app_name,
        "redis_connected": redis_ok,
        "database_connected": db_ok,
        "database_configured": bool(settings.database_url),
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=6204, reload=False)
