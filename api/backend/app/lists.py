"""Replace-in-place helper for the ordered list tables (home / site content).

Both the home page and the header/footer editors replace whole lists inside a
single transaction, so the order the admin sees is the order the page renders.
Table and column names come from internal specs, never from the request.
"""

from __future__ import annotations

from typing import Any, Optional

import asyncpg


async def replace_lists(
    connection: asyncpg.Connection,
    lists: dict[str, Optional[list[dict[str, Any]]]],
    specs: dict[str, dict[str, Any]],
) -> None:
    for key, items in lists.items():
        if items is None:
            continue

        spec = specs[key]
        table: str = spec["table"]
        columns: list[str] = spec["columns"]
        where: Optional[str] = spec.get("where")
        with_active: bool = bool(spec.get("active_column"))

        await connection.execute(f"DELETE FROM {table}" + (f" WHERE {where}" if where else ""))

        insert_columns = list(columns) + ["sort_order"] + (["is_active"] if with_active else [])

        for index, item in enumerate(items):
            params: list[Any] = [item.get(column) for column in columns]
            params.append(index)
            if with_active:
                params.append(item.get("is_active"))

            placeholders = [f"${position + 1}" for position in range(len(params))]
            await connection.execute(
                f"INSERT INTO {table} ({', '.join(insert_columns)}) "
                f"VALUES ({', '.join(placeholders)})",
                *params,
            )


__all__ = ["replace_lists"]
