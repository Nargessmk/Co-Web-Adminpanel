"""
Gateway entry point.

Replaces C# Program.cs. Features:
- CORS, JWT auth, rate limiting, compression (GZip)
- Reverse proxy with retry (tenacity = Polly equivalent)
- Sentry, logging, security headers, forwarded headers
- Health checks
- Swagger + Scalar (dev only)

Run with:
    uvicorn main:app --reload --port 6201
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from core.config import get_settings
from core.logging import get_logger, setup_logging
from core.sentry import init_sentry
from middleware.exception_handler import global_exception_handler
from middleware.jwt_auth import JWTAuthMiddleware
from middleware.logging import RequestLoggingMiddleware
from middleware.security import SecurityMiddleware
from middleware.brotli import BrotliCompressionMiddleware
from routes.proxy import router as proxy_router

settings = get_settings()
setup_logging(settings)
init_sentry(settings)
logger = get_logger(__name__)

limiter = Limiter(key_func=get_remote_address)


# --- Forwarded Headers middleware (mirrors C# UseForwardedHeaders) ---
class ForwardedHeadersMiddleware:
    """Process X-Forwarded-For and X-Forwarded-Proto headers."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            headers = dict(scope.get("headers", []))
            if b"x-forwarded-for" in headers:
                scope["client"] = (
                    headers[b"x-forwarded-for"].decode("latin-1").split(",")[0].strip(),
                    0,
                )
            if b"x-forwarded-proto" in headers:
                scope["scheme"] = headers[b"x-forwarded-proto"].decode("latin-1")

        return await self.app(scope, receive, send)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    logger.info("Gateway starting | environment=%s port=%s", settings.environment, settings.gateway_port)
    yield
    logger.info("Gateway shutting down")


app = FastAPI(
    title="Cloudland Gateway",
    description="API Gateway — single entry point for all microservices.",
    version="1.0.0",
    lifespan=lifespan,
)

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept", "X-Request-ID", "X-CSRF-Token", "Origin"],
    expose_headers=["X-Request-ID"],
)

# --- Security headers ---
app.add_middleware(SecurityMiddleware)

# --- JWT validation (defense-in-depth) ---
app.add_middleware(JWTAuthMiddleware)

# --- Forwarded headers (mirrors C# UseForwardedHeaders) ---
app.add_middleware(ForwardedHeadersMiddleware)

# --- Compression (mirrors C# GZipCompressionProvider + BrotliCompressionProvider) ---
app.add_middleware(BrotliCompressionMiddleware, minimum_size=500)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# --- Request logging ---
app.add_middleware(RequestLoggingMiddleware)

# --- Rate limiting ---
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# --- Global exception handler ---
app.add_exception_handler(Exception, global_exception_handler)


@app.get("/gateway-service-status", tags=["Health"])
async def health_check():
    return {"status": "ok", "service": "gateway", "environment": settings.environment}


@app.get("/sentry-debug", tags=["Debug"])
async def trigger_error():
    division_by_zero = 1 / 0


# --- WebSocket endpoint (mirrors C# SignalR real-time capability) ---
class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict) -> None:
        for connection in list(self.active_connections):
            try:
                await connection.send_json(message)
            except Exception:
                self.disconnect(connection)


ws_manager = ConnectionManager()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await ws_manager.broadcast({"type": "echo", "data": data})
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception as exc:
        ws_manager.disconnect(websocket)
        logger.warning("WebSocket error: %s", exc)


# --- Swagger + Scalar (dev only) ---
if settings.environment == "development":
    from fastapi.openapi.docs import get_swagger_ui_html

    @app.get("/openapi.json", include_in_schema=False)
    async def custom_openapi():
        return app.openapi()

    @app.get("/docs", include_in_schema=False)
    async def swagger_ui():
        return get_swagger_ui_html(openapi_url="/openapi.json", title="Gateway API")

    try:
        from scalar_fastapi import get_scalar_api_reference

        @app.get("/scalar", include_in_schema=False)
        async def scalar_docs():
            return get_scalar_api_reference(openapi_url="/openapi.json", title="Gateway API")
    except ImportError:
        pass


app.include_router(proxy_router)
