"""
Custom exception hierarchy for this service.

Centralizing exceptions here lets routers and dependencies catch specific,
predictable error types instead of parsing raw httpx or FusionAuth responses
in multiple places.
"""

from typing import Any


class FusionAuthError(Exception):
    """Base class for all FusionAuth-related errors."""

    def __init__(self, message: str, status_code: int | None = None, details: Any = None) -> None:
        self.message = message
        self.status_code = status_code
        self.details = details
        super().__init__(message)


class FusionAuthConnectionError(FusionAuthError):
    """
    Raised when the FusionAuth instance cannot be reached at all
    (network failure, DNS error, connection timeout).

    This is distinct from FusionAuthAPIError: a connection error means
    FusionAuth never got a chance to respond.
    """


class FusionAuthTimeoutError(FusionAuthError):
    """Raised when a request to FusionAuth exceeds the configured timeout."""


class FusionAuthAPIError(FusionAuthError):
    """
    Raised when FusionAuth responds, but the response indicates a failure
    (e.g. 400 validation error, 401 unauthorized, 404 not found, 500 internal error).

    The original FusionAuth response body is preserved in `details` so callers
    can inspect field-level validation errors if needed.
    """


class FusionAuthNotFoundError(FusionAuthAPIError):
    """Raised specifically for 404 responses (e.g. user not found)."""