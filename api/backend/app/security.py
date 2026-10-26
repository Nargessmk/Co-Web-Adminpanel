"""JWT authentication dependency.

Verifies the token issued by the FastAPI authentication microservice
(gateway -> auth -> FusionAuth) exactly like the old ``middleware/auth.js``:

* ``Authorization: Bearer <token>`` is required
* HS256 signature with ``MICROSERVICE_JWT_SECRET``
* the payload's ``type`` must be ``access``
* ``sub`` -> admin id, ``roles`` -> roles, ``app_id`` -> tenant
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Optional

import jwt
from fastapi import Request

from . import config
from .errors import ApiError

# Tolerance for integer-second rounding of iat/exp claims (both are written by
# the same clock, so no real clock skew needs to be accommodated here).
_LIFETIME_LEEWAY_SECONDS = 5


@dataclass
class AdminContext:
    id: Any = None
    roles: list[str] = field(default_factory=list)
    app_id: Optional[str] = None
    token: Optional[str] = None


def _bearer_token(request: Request) -> Optional[str]:
    header = request.headers.get("authorization") or ""
    if not header.lower().startswith("bearer "):
        return None
    parts = header.split(" ")
    return parts[1] if len(parts) > 1 else None


async def require_admin(request: Request) -> AdminContext:
    """FastAPI dependency mirroring ``authenticateAdmin``."""
    header = request.headers.get("authorization") or ""
    if not header.lower().startswith("bearer "):
        raise ApiError(401, "Access denied. No token provided.")

    token = _bearer_token(request)
    if not token:
        raise ApiError(401, "Access denied. No token provided.")

    if not config.MICROSERVICE_JWT_SECRET:
        raise ApiError(401, "Invalid or expired token")

    # PyJWT >= 2 refuses any token that carries an `aud` claim unless the
    # expected audience is passed here (InvalidAudienceError) — which is what
    # made every admin route return 401 with a perfectly valid token. The auth
    # service always issues tokens with iss: APM_jwt / aud: ailand.ai, so both
    # are verified whenever they are configured.
    decode_kwargs: dict[str, Any] = {
        "algorithms": [config.MICROSERVICE_JWT_ALGORITHM],
    }
    if config.MICROSERVICE_JWT_AUDIENCE:
        decode_kwargs["audience"] = config.MICROSERVICE_JWT_AUDIENCE
    else:
        decode_kwargs["options"] = {"verify_aud": False}
    if config.MICROSERVICE_JWT_ISSUER:
        decode_kwargs["issuer"] = config.MICROSERVICE_JWT_ISSUER

    try:
        payload: dict[str, Any] = jwt.decode(
            token,
            config.MICROSERVICE_JWT_SECRET,
            **decode_kwargs,
        )
    except jwt.PyJWTError as error:
        raise ApiError(401, "Invalid or expired token") from error

    if payload.get("type") != "access":
        raise ApiError(401, "Invalid token type")

    # Enforce the 30-minute admin session: require an exp claim and cap the
    # token's lifetime, so a longer-lived token signed with the same secret is
    # rejected instead of silently accepted.
    exp = payload.get("exp")
    if not isinstance(exp, (int, float)):
        raise ApiError(401, "Invalid or expired token")

    iat = payload.get("iat")
    if isinstance(iat, (int, float)):
        lifetime = exp - iat
    else:
        lifetime = exp - time.time()
    max_lifetime = config.ACCESS_TOKEN_MAX_AGE_MINUTES * 60
    if lifetime > max_lifetime + _LIFETIME_LEEWAY_SECONDS:
        raise ApiError(401, "Invalid or expired token")

    return AdminContext(
        id=payload.get("sub"),
        roles=payload.get("roles") or [],
        app_id=payload.get("app_id"),
        token=token,
    )


__all__ = ["AdminContext", "require_admin", "_bearer_token"]
