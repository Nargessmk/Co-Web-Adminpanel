"""
JWT token validation for the Gateway.

Gateway does NOT issue tokens — it only verifies tokens issued by the
Authentication microservice. This mirrors C# JwtExtensions.cs.
"""

from typing import Annotated

from fastapi import Cookie, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from pydantic import BaseModel

from core.config import Settings, get_settings


class TokenPayload(BaseModel):
    sub: str
    app_id: str = ""
    roles: list[str] = []
    type: str = "access"
    iss: str = ""
    aud: str = ""


_bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
    jwt_token: str | None = Cookie(default=None),
    settings: Settings = Depends(get_settings),
) -> TokenPayload:
    """Extract and validate JWT from Bearer header or cookie."""
    token = None
    if credentials:
        token = credentials.credentials
    elif jwt_token:
        token = jwt_token

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
            audience=settings.jwt_audience,
            issuer=settings.jwt_issuer,
        )
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {exc}",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    return TokenPayload.model_validate(payload)


def require_roles(*allowed_roles: str):
    def _check(user: TokenPayload = Depends(get_current_user)) -> TokenPayload:
        if not any(r in user.roles for r in allowed_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Required roles: {', '.join(allowed_roles)}",
            )
        return user
    return _check


CurrentUser = Annotated[TokenPayload, Depends(get_current_user)]
AdminUser = Annotated[TokenPayload, Depends(require_roles("admin"))]
