"""
JWT creation and verification for tokens issued by THIS microservice.

Important distinction from FusionAuth tokens:
FusionAuth authenticates the user and tells us which application(s) they
belong to. We do not hand FusionAuth's own tokens to the frontend. Instead,
after a successful FusionAuth login, we mint our own JWT here and embed the
`application_id` the user just authenticated against as a signed claim
(`app_id`).

Why this matters for multi-tenancy:
The frontend supplies `application_id` only at unauthenticated entry points
(login, register, forgot-password) — see Schema/Authentication/auth.py. FusionAuth itself
validates that value (it rejects login if the user has no registration for
that application). For every request AFTER login, the application_id must
be read from this signed token, never from a client-supplied field again —
otherwise a client could tamper with a request and act as if they belonged
to a different tenant without re-authenticating against it.

This module has no dependency on FusionAuth or on any router — it only
knows how to create and read tokens, so it can be reused identically by
the login flow, the refresh flow, and the get_current_user dependency.
"""

from datetime import datetime, timedelta, timezone
from enum import StrEnum
from typing import Any
import secrets

from jose import JWTError, jwt
from pydantic import BaseModel

from core.config import Settings, get_settings
from core.exceptions import FusionAuthError


class TokenType(StrEnum):
    """Distinguishes access vs refresh tokens inside the `type` claim.

    Kept as a string enum (not just a literal) so the same value can be used
    both when creating a token and when validating it on decode, without the
    two sides drifting out of sync.
    """

    ACCESS = "access"
    REFRESH = "refresh"


class InvalidTokenError(FusionAuthError):
    """Raised when a token is missing, malformed, expired, or fails signature
    verification. Deliberately not a subclass of the FusionAuth-specific
    errors in core.exceptions — this can happen even if FusionAuth is
    perfectly healthy, since verification never calls out to FusionAuth."""


class TokenPayload(BaseModel):
    """Typed view of the claims we put into (and expect back out of) our own JWTs.

    Routers and dependencies should work with this model, not raw dicts,
    so a typo in a claim name fails fast with a validation error instead of
    silently returning None deep inside a handler.
    """

    sub: str  # FusionAuth user id
    app_id: str  # FusionAuth application id the user authenticated against
    roles: list[str] = []
    type: TokenType


def _create_token(
    *,
    settings: Settings,
    user_id: str,
    application_id: str,
    token_type: TokenType,
    expires_delta: timedelta,
    roles: list[str] | None = None,
) -> str:
    """Shared implementation for access and refresh token creation.

    Access and refresh tokens carry the same `sub`/`app_id` shape and differ
    only in `type` and lifetime, so both public functions below delegate here
    rather than duplicating the claims dict.
    """
    now = datetime.now(timezone.utc)
    claims: dict[str, Any] = {
        "sub": user_id,
        "app_id": application_id,
        "roles": roles or [],
        "type": token_type.value,
        "iss": settings.jwt_issuer,
        "aud": settings.jwt_audience,
        "iat": now,
        "exp": now + expires_delta,
    }
    return jwt.encode(claims, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_access_token(
    user_id: str,
    application_id: str,
    roles: list[str] | None = None,
    settings: Settings | None = None,
) -> str:
    """Create a short-lived access token for a user, scoped to one application_id.

    A fresh call to get_settings() is used by default (rather than reading
    a module-level constant) so tests can pass in an override without
    needing to patch global state.
    """
    settings = settings or get_settings()
    return _create_token(
        settings=settings,
        user_id=user_id,
        application_id=application_id,
        token_type=TokenType.ACCESS,
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
        roles=roles,
    )


def create_refresh_token(
    user_id: str,
    application_id: str,
    settings: Settings | None = None,
) -> str:
    """Create a long-lived refresh token, scoped to the same application_id
    as the access token it will be used to renew.

    Deliberately carries no `roles` claim: roles can change between issuance
    and refresh (e.g. an admin revokes a role), so the refresh endpoint
    should re-derive roles from FusionAuth rather than trusting a stale copy.
    """
    settings = settings or get_settings()
    return _create_token(
        settings=settings,
        user_id=user_id,
        application_id=application_id,
        token_type=TokenType.REFRESH,
        expires_delta=timedelta(days=settings.refresh_token_expire_days),
    )


def decode_token(
    token: str,
    expected_type: TokenType,
    settings: Settings | None = None,
) -> TokenPayload:
    """Verify signature/expiry/issuer/audience and return typed claims.

    Args:
        token: The raw JWT string (without the "Bearer " prefix).
        expected_type: Rejects the token if its `type` claim doesn't match —
            this is what stops a refresh token from being used to call a
            regular authenticated endpoint, and vice versa.
        settings: Optional override, mainly for tests.

    Raises:
        InvalidTokenError: On any signature, expiry, claim-shape, or
            token-type mismatch. Callers (e.g. get_current_user) turn this
            into a 401 — decode_token itself has no knowledge of HTTP.
    """
    settings = settings or get_settings()
    try:
        raw_claims = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
            audience=settings.jwt_audience,
            issuer=settings.jwt_issuer,
        )
    except JWTError as exc:
        raise InvalidTokenError(f"Token verification failed: {exc}") from exc

    try:
        payload = TokenPayload.model_validate(raw_claims)
    except Exception as exc:
        raise InvalidTokenError(f"Token has an unexpected claims shape: {exc}") from exc

    if payload.type != expected_type:
        raise InvalidTokenError(
            f"Expected a {expected_type.value} token but got a {payload.type.value} token"
        )

    return payload


def generate_csrf_token(length: int = 32) -> str:
    """Generate a cryptographically random CSRF token."""
    return secrets.token_hex(length)


def validate_csrf_token(cookie_value: str | None, header_value: str | None) -> bool:
    """Validate double-submit CSRF token: cookie value must match header value.

    Both values must be non-empty and identical (constant-time comparison).
    """
    if not cookie_value or not header_value:
        return False
    return secrets.compare_digest(cookie_value, header_value)
