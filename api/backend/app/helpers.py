"""Request parsing + JavaScript-compatible value coercion helpers.

The old Express API accepted both ``application/json`` and
``multipart/form-data`` on the same route (Express only ran multer when the
client sent multipart). Several endpoints — for example
``PUT /api/products/admin/{id}`` (the "featured" toggle sends JSON, the edit
dialog sends multipart) — rely on that, so the port must accept both too.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Optional

from fastapi import Request
from starlette.datastructures import UploadFile as StarletteUploadFile

from . import config
from .errors import ApiError
from .storage import ALLOWED_TYPES, ALLOWED_TYPES_MESSAGE


@dataclass
class UploadedFile:
    """Minimal stand-in for multer's ``req.file``."""

    buffer: bytes
    originalname: str
    mimetype: str


async def read_body(
    request: Request,
) -> tuple[dict[str, Any], dict[str, StarletteUploadFile]]:
    """Return ``(fields, files)`` for JSON, urlencoded and multipart bodies."""
    content_type = (request.headers.get("content-type") or "").lower()
    fields: dict[str, Any] = {}
    files: dict[str, StarletteUploadFile] = {}

    if "application/json" in content_type:
        try:
            payload = await request.json()
        except Exception:  # noqa: BLE001 — malformed body behaves like an empty one
            return fields, files
        if isinstance(payload, dict):
            fields = payload
        return fields, files

    if (
        "multipart/form-data" in content_type
        or "application/x-www-form-urlencoded" in content_type
    ):
        try:
            form = await request.form()
        except Exception:  # noqa: BLE001
            return fields, files
        for key, value in form.multi_items():
            if isinstance(value, StarletteUploadFile):
                files[key] = value
            else:
                fields[key] = value
    return fields, files


async def extract_file(
    files: dict[str, StarletteUploadFile],
    field: str,
    max_mb: int = config.MAX_UPLOAD_MB,
    size_message: Optional[str] = None,
) -> Optional[UploadedFile]:
    """Validate + read an uploaded file exactly like the multer config did."""
    upload = files.get(field)
    if upload is None:
        return None

    mimetype = upload.content_type or ""
    if mimetype not in ALLOWED_TYPES:
        raise ApiError(400, ALLOWED_TYPES_MESSAGE)

    buffer = await upload.read()
    if len(buffer) > max_mb * 1024 * 1024:
        raise ApiError(400, size_message or "File too large")

    return UploadedFile(
        buffer=buffer, originalname=upload.filename or "file", mimetype=mimetype
    )


# ------------------------------------------------------------------ values ---
def text(value: Any) -> Optional[str]:
    """Port of the JS ``text()`` helper: trim, empty becomes ``None``."""
    if value is None:
        return None
    trimmed = str(value).strip()
    return trimmed or None


def js_bool(value: Any) -> bool:
    """``value === true || value === 'true'``."""
    return value is True or value == "true"


def optional_bool(value: Any) -> Optional[bool]:
    """Boolean or ``None`` (for ``COALESCE($n, column)`` parameters)."""
    if value is None or value == "":
        return None
    if value is True or value is False:
        return value
    lowered = str(value).strip().lower()
    if lowered in ("true", "t", "1", "yes", "on"):
        return True
    if lowered in ("false", "f", "0", "no", "off"):
        return False
    return None


def bool_default_true(value: Any) -> bool:
    """JS ``value === undefined ? true : (value === true || value === 'true')``."""
    if value is None:
        return True
    return js_bool(value)


def to_int(value: Any, default: Optional[int] = None) -> Optional[int]:
    """Port of ``parseInt(value, 10) || default``."""
    if value is None or value == "":
        return default
    try:
        return int(float(str(value).strip()))
    except (TypeError, ValueError):
        return default


def int_or_null(value: Any) -> Optional[int]:
    """JS ``intOrNull``: ``undefined``/``null``/``''``/NaN become ``None``."""
    if value is None or value == "":
        return None
    try:
        return int(float(str(value).strip()))
    except (TypeError, ValueError):
        return None


def optional_order(value: Any) -> Optional[int]:
    """JS ``optionalOrder``: ``undefined``/``null``/``''`` become ``None``."""
    if value is None or value == "":
        return None
    try:
        return int(float(str(value).strip()))
    except (TypeError, ValueError):
        return None


def page_limit(
    page_raw: Any,
    limit_raw: Any,
    default_limit: int,
    max_limit: int,
) -> tuple[int, int, int]:
    """Port of the pagination math used across the controllers."""
    page = max(1, to_int(page_raw, 1) or 1)
    limit = min(max_limit, max(1, to_int(limit_raw, default_limit) or default_limit))
    return page, limit, (page - 1) * limit


def pagination(page: int, limit: int, total: int) -> dict[str, int]:
    return {
        "page": page,
        "limit": limit,
        "total": total,
        "totalPages": math.ceil(total / limit) if limit else 0,
    }


def upsert_columns(
    body: dict[str, Any],
    columns: list[str],
    icon_defaults: Optional[dict[str, str]] = None,
) -> tuple[list[str], list[Any]]:
    """Collect the provided settings columns + values (absent keys are skipped)."""
    provided: list[str] = []
    values: list[Any] = []
    icon_defaults = icon_defaults or {}

    for column in columns:
        if column not in body:
            continue
        value = text(body.get(column)) or icon_defaults.get(column) or None
        provided.append(column)
        values.append(value)

    return provided, values


__all__ = [
    "UploadedFile",
    "read_body",
    "extract_file",
    "text",
    "js_bool",
    "optional_bool",
    "bool_default_true",
    "to_int",
    "int_or_null",
    "optional_order",
    "page_limit",
    "pagination",
    "upsert_columns",
]