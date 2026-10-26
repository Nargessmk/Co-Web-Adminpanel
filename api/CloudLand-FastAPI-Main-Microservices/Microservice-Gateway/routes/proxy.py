"""
Catch-all proxy router.

Forwards any request to the appropriate backend service based on
path prefix matching. Public routes (login, register) skip auth;
all other routes require JWT.
"""

from fastapi import APIRouter, Depends, Request, Response

from core.config import Settings, get_settings
from services.proxy import proxy_request

router = APIRouter()


@router.api_route(
    "/{path:path}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
)
async def catch_all(
    request: Request,
    path: str,
    settings: Settings = Depends(get_settings),
) -> Response:
    return await proxy_request(request, f"/{path}", settings)
