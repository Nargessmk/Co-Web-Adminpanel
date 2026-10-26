"""CloudLand API — FastAPI application entrypoint.

Drop-in replacement for the previous Node/Express server: same routes, same
request formats (JSON *and* multipart) and the same ``{success, data, message,
pagination}`` JSON envelope, so the Quasar frontend works unchanged.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from . import config, db
from .errors import ApiError
from .responses import failure, success
from .routers import (
    about,
    articles,
    auth,
    catalog_page,
    catalogs,
    categories,
    consultations,
    contact,
    home,
    products,
    seo,
    site,
    solutions,
    solutions_page,
    stats,
    team_members,
    uploads,
    media,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("cloudland")


@asynccontextmanager
async def lifespan(_app: FastAPI):
    try:
        await db.init_pool()
        logger.info("PostgreSQL connected successfully")
    except Exception as exc:
        logger.warning("PostgreSQL connection failed (%s). Continuing in degraded mode.", exc)
    logger.info("CloudLand API running on port %s", config.PORT)
    try:
        yield
    finally:
        await db.close_pool()


app = FastAPI(
    title="CloudLand API",
    version="1.0.0",
    description="REST API for CloudLand products, categories, and consultations",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url=None,
    openapi_url="/openapi.json",
    swagger_ui_parameters={"custom_site_title": "CloudLand API Docs"},
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------------------- handlers ----
@app.exception_handler(ApiError)
async def _api_error_handler(_request: Request, exc: ApiError) -> JSONResponse:
    return JSONResponse(
        content={"success": False, "message": exc.message, **exc.extra},
        status_code=exc.status_code,
    )


@app.exception_handler(RequestValidationError)
async def _validation_error_handler(
    _request: Request, exc: RequestValidationError
) -> JSONResponse:
    first = exc.errors()[0] if exc.errors() else {}
    location = ".".join(str(part) for part in first.get("loc", []) if part != "body")
    message = first.get("msg", "Invalid request")
    return JSONResponse(
        content={
            "success": False,
            "message": f"{location}: {message}" if location else message,
        },
        status_code=422,
    )


@app.exception_handler(HTTPException)
async def _http_error_handler(_request: Request, exc: HTTPException) -> JSONResponse:
    if isinstance(exc.detail, dict):
        body = exc.detail
    else:
        body = {"success": False, "message": str(exc.detail)}
    return JSONResponse(content=body, status_code=exc.status_code)


@app.exception_handler(Exception)
async def _unhandled_error_handler(_request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled error: %s", exc)
    return JSONResponse(
        content={"success": False, "message": "Internal server error"},
        status_code=500,
    )


# ----------------------------------------------------------------- routes ----
@app.get("/api/health", tags=["Health"])
async def health():
    return success(message="CloudLand API is running")


for module in (
    stats,
    catalog_page,
    solutions_page,
    contact,
    categories,
    consultations,
    uploads,
    about,
    team_members,
    catalogs,
    solutions,
    articles,
    site,
    home,
    auth,
    products,
    seo,
    media,
):
    app.include_router(module.router)


# ------------------------------------------------ compatibility aliases ----
# Frontend Pinia stores or cached clients requesting /api/site-content/{solutions,catalog}
@app.get("/api/site-content/solutions", tags=["Compatibility Aliases"])
async def site_content_solutions_alias():
    return await solutions_page.get_public()


@app.get("/api/site-content/catalog", tags=["Compatibility Aliases"])
async def site_content_catalog_alias():
    return await catalog_page.get_public()


# ---------------------------------------------------------------- uploads ----
# Legacy/disk fallback files are served from /uploads just like before.
_uploads_dir = Path(config.UPLOADS_DIR)
_uploads_dir.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(_uploads_dir)), name="uploads")


__all__ = ["app"]

