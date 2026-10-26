"""JSON response builders.

Every successful/unsuccessful answer keeps the historical shape the Quasar
frontend already consumes::

    {"success": true,  "data": ..., "message": "...", "pagination": {...}}
    {"success": false, "message": "..."}
"""

from __future__ import annotations

from typing import Any, Optional

from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from .storage import expand_file_keys

_UNSET: Any = object()


def _records(data: Any) -> Any:
    """Convert asyncpg Records (and nested ones) into plain dicts.

    asyncpg 0.30 dropped `Record._asdict()`, so duck-typing on that method no
    longer matched and a Record fell through unchanged. That meant
    `expand_file_keys()` never saw the row, and every stored object key went to
    the browser as a bare key (`solutions/abc.png`) instead of a URL. A Record
    is a read-only mapping, so match on `items()` instead.
    """
    if data is None:
        return None
    if isinstance(data, (list, tuple)):
        return [_records(item) for item in data]
    as_dict = getattr(data, "_asdict", None)
    if callable(as_dict):
        return {key: _records(value) for key, value in as_dict().items()}
    items = getattr(data, "items", None)
    if callable(items):
        return {key: _records(value) for key, value in items()}
    return data


def success(
    data: Any = _UNSET,
    message: Optional[str] = None,
    status_code: int = 200,
    pagination: Optional[dict[str, Any]] = None,
    **extra: Any,
) -> JSONResponse:
    body: dict[str, Any] = {"success": True}
    if message is not None:
        body["message"] = message
    if data is not _UNSET:
        body["data"] = data
    if pagination is not None:
        body["pagination"] = pagination
    body.update(extra)
    # Stored files leave the database as object keys; the browser gets a URL.
    return JSONResponse(
        content=jsonable_encoder(expand_file_keys(_records(body))),
        status_code=status_code,
    )


def failure(message: str, status_code: int = 400, **extra: Any) -> JSONResponse:
    body: dict[str, Any] = {"success": False, "message": message}
    body.update(extra)
    return JSONResponse(content=jsonable_encoder(body), status_code=status_code)


__all__ = ["success", "failure"]
