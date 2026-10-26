"""Shared "singleton settings row" upsert used by all editable pages.

The old controllers each repeated the same dynamic ``INSERT ... ON CONFLICT``
boilerplate. Table and column names are internal constants (never user input),
so they are inlined while the values always travel as bound parameters.
"""

from __future__ import annotations

from typing import Any, Optional, Sequence

from . import db
from .errors import ApiError
from .helpers import upsert_columns


def _select_list(columns: Sequence[str]) -> str:
    return ", ".join(["id", *columns, "updated_at"])


settings_select = _select_list


async def read_settings(
    table: str,
    columns: Sequence[str],
    key: str = "settings",
) -> dict[str, Any]:
    """Read the singleton row and wrap it the way the frontend expects."""
    row = await db.fetchrow(f"SELECT {_select_list(columns)} FROM {table} WHERE id = 1")
    return {key: dict(row) if row else None}


async def upsert_settings(
    table: str,
    columns: Sequence[str],
    body: dict[str, Any],
    icon_defaults: Optional[dict[str, str]] = None,
) -> Any:
    """Upsert the singleton row (``id = 1``) with only the provided columns."""
    provided, values = upsert_columns(body, list(columns), icon_defaults)
    if not provided:
        raise ApiError(400, "No settings provided")

    placeholders = [f"${index + 1}" for index in range(len(provided))]
    updates = [f"{column} = EXCLUDED.{column}" for column in provided]

    query = (
        f"INSERT INTO {table} (id, {', '.join(provided)}, updated_at)\n"
        f"VALUES (1, {', '.join(placeholders)}, CURRENT_TIMESTAMP)\n"
        f"ON CONFLICT (id) DO UPDATE SET\n"
        f"  {', '.join(updates)},\n"
        f"  updated_at = CURRENT_TIMESTAMP\n"
        f"RETURNING {_select_list(columns)}"
    )
    return await db.fetchrow(query, *values)


__all__ = ["read_settings", "upsert_settings", "settings_select"]
