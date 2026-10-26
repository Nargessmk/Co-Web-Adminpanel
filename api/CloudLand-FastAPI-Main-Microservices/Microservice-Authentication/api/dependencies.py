"""
FastAPI dependency providers.

Router functions import from here (not directly from services/ or core/) to
keep a single, consistent place where all Depends() targets are defined.
"""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from core.security import InvalidTokenError, TokenPayload, TokenType, decode_token
from services.fusionauth_client import FusionAuthSDKClient, get_fusionauth_client

_bearer_scheme = HTTPBearer(auto_error=True)


def get_fusionauth() -> FusionAuthSDKClient:
    return get_fusionauth_client()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer_scheme),
) -> TokenPayload:
    """
    Verify JWT and return typed claims. Raises 401 on any failure.
    """
    try:
        return decode_token(credentials.credentials, expected_type=TokenType.ACCESS)
    except InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


def require_roles(*allowed_roles: str):
    """
    Dependency factory that checks if the current user has at least one
    of the specified roles. Mirrors C# [Authorize(Roles = "admin")] pattern.

    Usage:
        @router.get("/admin-only")
        async def admin_endpoint(
            user: TokenPayload = Depends(require_roles("admin")),
        ):
            ...
    """
    def _check(current_user: TokenPayload = Depends(get_current_user)) -> TokenPayload:
        if not any(role in current_user.roles for role in allowed_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Required roles: {', '.join(allowed_roles)}",
            )
        return current_user
    return _check


CurrentUser = Annotated[TokenPayload, Depends(get_current_user)]
AdminUser = Annotated[TokenPayload, Depends(require_roles("admin"))]
AdminOrUser = Annotated[TokenPayload, Depends(require_roles("admin", "user"))]
# Any authenticated user (valid token) regardless of roles — for self-access endpoints
AuthenticatedUser = Annotated[TokenPayload, Depends(get_current_user)]
