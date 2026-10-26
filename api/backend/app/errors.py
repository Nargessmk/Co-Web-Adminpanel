"""Small error type used to short-circuit a request with the API's JSON shape."""

from __future__ import annotations

from typing import Any, Optional


class ApiError(Exception):
    """Raised anywhere in a handler to return ``{"success": false, "message": ...}``."""

    def __init__(
        self,
        status_code: int,
        message: str,
        extra: Optional[dict[str, Any]] = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.message = message
        self.extra = extra or {}


class StorageError(Exception):
    """The Storage microservice could not store/remove a file."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message
