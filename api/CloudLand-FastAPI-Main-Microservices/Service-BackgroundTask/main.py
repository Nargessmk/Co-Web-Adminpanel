import sys
import os
from pathlib import Path

# Ensure root workspace directory is in sys.path so `Schema` can be imported
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.v1.reindex import router as reindex_router
from core.config import get_settings
from core.elastic import close_es_client, get_es_client
from core.scheduler import shutdown_scheduler, start_scheduler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("background_task.main")
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing Service-BackgroundTask...")
    get_es_client()
    start_scheduler()
    yield
    logger.info("Shutting down Service-BackgroundTask...")
    shutdown_scheduler()
    await close_es_client()


app = FastAPI(
    title="Cloudland Background Task Service",
    description="Background Scheduled Tasks & Reindex Worker Service matching C# Cloudland.APM.BackgroundTask",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(reindex_router)


@app.get("/background-tasks-service-status", tags=["Health"])
async def background_tasks_service_status():
    """Health check endpoint matching C# MapHealthChecks('/background-tasks-service-status')."""
    return {
        "status": "Healthy",
        "service": settings.app_name,
        "environment": settings.environment,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=settings.port, reload=True)
