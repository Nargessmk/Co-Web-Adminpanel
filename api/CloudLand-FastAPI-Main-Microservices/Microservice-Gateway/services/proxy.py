"""
Reverse proxy service — replaces Ocelot for request forwarding.

Features matching C# Ocelot + Polly:
- Retry with exponential backoff (replaces Polly retry)
- X-Forwarded-For + X-Forwarded-Proto headers
- Backend health awareness via error logging
"""

import logging

import httpx
from fastapi import APIRouter, Request, Response
from fastapi.responses import JSONResponse
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
)

from core.config import Settings, get_settings
from core.logging import get_logger
from middleware.cache import response_cache

logger = get_logger("app.proxy")

_BACKEND_TIMEOUT = httpx.Timeout(30.0, connect=5.0)

# Retry config — mirrors Polly retry with exponential backoff
_MAX_RETRIES = 3
_RETRY_WAIT_MIN = 0.5
_RETRY_WAIT_MAX = 4.0

ROUTE_MAP: dict[str, str] = {
    # --- Auth service (port 4002) ---
    "/auth": "auth_service_url",
    "/users": "auth_service_url",
    "/applications": "auth_service_url",
    "/groups": "auth_service_url",

    # --- App Management service (port 4004) ---
    "/contract": "app_management_url",
    "/contractfood": "app_management_url",
    "/contractlocation": "app_management_url",
    "/contractfoodcalendar": "app_management_url",
    "/contractfoodlocation": "app_management_url",
    "/organizationalposition": "app_management_url",
    "/organizationalchart": "app_management_url",
    "/personnel": "app_management_url",
    "/food": "app_management_url",
    "/contractor": "app_management_url",
    "/vehicle": "app_management_url",
    "/vehicledriver": "app_management_url",
    "/location": "app_management_url",
    "/meal": "app_management_url",
    "/room": "app_management_url",
    "/bed": "app_management_url",
    "/accountnumber": "app_management_url",
    "/reservationrequestheader": "app_management_url",
    "/reservationrequestletter": "app_management_url",
    "/reservationrequestperson": "app_management_url",
    "/reservationrequestbed": "app_management_url",
    "/reservationfoodcalendar": "app_management_url",
    "/constantsmart": "app_management_url",
    "/projectprofile": "app_management_url",
    "/projectproposal": "app_management_url",
    "/projecttimeline": "app_management_url",
    "/testdefinition": "app_management_url",
    "/testquestion": "app_management_url",
    "/questionoption": "app_management_url",
    "/testresult": "app_management_url",
    "/baseprofile": "app_management_url",
    "/certification": "app_management_url",
    "/document": "app_management_url",
    "/educationalbackground": "app_management_url",
    "/employer": "app_management_url",
    "/portfolio": "app_management_url",
    "/skill": "app_management_url",
    "/workbackground": "app_management_url",

    # --- Core App Management endpoints ---
    "/constant": "app_management_url",
    "/calendar": "app_management_url",
    "/entity-file-attachments": "app_management_url",
    "/reindex": "app_management_url",
    "/constantpermission": "app_management_url",
    "/module-permissions": "app_management_url",

    # --- Background Task service (port 4005) ---
    "/background-tasks": "background_task_url",
    "/background-tasks-service-status": "background_task_url",

    # --- Storage service (port 4003) ---
    "/buckets-objects": "storage_service_url",
}

_BACKEND_PATH_PREFIXES: dict[str, str] = {
    "auth_service_url": "/api/v1",
    "app_management_url": "/api/v1",
    "storage_service_url": "/api/v1",
    "background_task_url": "/api/v1",
}

_SPECIAL_ROUTES: dict[str, tuple[str, str]] = {
    "/auth/health": ("auth_service_url", "/api/health"),
    "/api/health": ("app_management_url", "/api/health"),
    "/storage/health": ("storage_service_url", "/api/health"),
    "/background-tasks-service-status": ("background_task_url", "/background-tasks-service-status"),
}

_CANONICAL_PREFIX: dict[str, str] = {
    "/reindex": "/Reindex",
    "/constantpermission": "/ConstantPermission",
}


def _resolve_backend(path: str, settings: Settings) -> tuple[str, str] | None:
    if path in _SPECIAL_ROUTES:
        service_key, downstream_path = _SPECIAL_ROUTES[path]
        base_url = getattr(settings, service_key)
        return base_url, downstream_path

    path_lower = path.lower()
    for prefix in sorted(ROUTE_MAP.keys(), key=len, reverse=True):
        if path_lower == prefix or path_lower.startswith(prefix + "/"):
            service_key = ROUTE_MAP[prefix]
            base_url = getattr(settings, service_key)
            backend_prefix = _BACKEND_PATH_PREFIXES.get(service_key, "")
            canonical_prefix = _CANONICAL_PREFIX.get(prefix, prefix)
            remaining = path[len(prefix) :]
            downstream_path = f"{backend_prefix}{canonical_prefix}{remaining}"
            return base_url, downstream_path
    return None


@retry(
    stop=stop_after_attempt(_MAX_RETRIES),
    wait=wait_exponential(multiplier=1, min=_RETRY_WAIT_MIN, max=_RETRY_WAIT_MAX),
    retry=retry_if_exception_type((httpx.ConnectError, httpx.TimeoutException)),
    before_sleep=before_sleep_log(logger, logging.WARNING),
    reraise=True,
)
async def _do_backend_request(
    client: httpx.AsyncClient,
    method: str,
    url: str,
    headers: dict,
    content: bytes | None,
) -> httpx.Response:
    """Execute backend request with retry — mirrors Polly retry policy."""
    return await client.request(
        method=method,
        url=url,
        headers=headers,
        content=content,
    )


async def proxy_request(
    request: Request,
    path: str,
    settings: Settings | None = None,
) -> Response:
    settings = settings or get_settings()
    resolved = _resolve_backend(path, settings)
    if not resolved:
        return JSONResponse(status_code=404, content={"detail": f"Unknown route: {path}"})

    base_url, downstream_path = resolved

    # Check cache for GET requests (mirrors C# OutputCache 10min TTL)
    if request.method == "GET":
        cached = response_cache.get("GET", path, request.url.query)
        if cached is not None:
            return cached

    url = f"{base_url}{downstream_path}"

    if request.url.query:
        url += f"?{request.url.query}"

    # Build headers with forwarded-for + forwarded-proto
    headers = {}
    for name in ("authorization", "content-type", "accept", "x-request-id", "x-csrf-token"):
        if name in request.headers:
            headers[name] = request.headers[name]

    client_ip = request.client.host if request.client else "unknown"
    headers["X-Forwarded-For"] = client_ip
    headers["X-Forwarded-Proto"] = request.url.scheme

    body = await request.body()

    try:
        async with httpx.AsyncClient(timeout=_BACKEND_TIMEOUT) as client:
            resp = await _do_backend_request(
                client, request.method, url, headers, body if body else None,
            )
    except (httpx.ConnectError, httpx.TimeoutException) as exc:
        status = 502 if isinstance(exc, httpx.ConnectError) else 504
        detail = "Backend service unavailable" if isinstance(exc, httpx.ConnectError) else "Backend service timeout"
        logger.error("%s: %s", detail, base_url)
        return JSONResponse(status_code=status, content={"detail": detail})

    excluded_headers = {"content-length", "content-encoding", "transfer-encoding", "connection"}
    response_headers = {
        k: v for k, v in resp.headers.items()
        if k.lower() not in excluded_headers
    }

    result = Response(
        content=resp.content,
        status_code=resp.status_code,
        headers=response_headers,
        media_type=resp.headers.get("content-type"),
    )

    # Cache successful GET responses
    if request.method == "GET" and 200 <= resp.status_code < 300:
        response_cache.set("GET", path, request.url.query, result)

    return result
