"""Category repository isolating SQL operations for product_categories."""

from __future__ import annotations

from typing import Any, Optional

from .base import BaseRepository

LIST_COLUMNS = "id, name, slug, description, sort_order, created_at"


class CategoryRepository(BaseRepository):
    """Encapsulates all database interactions for product categories."""

    async def list_all(self) -> list[dict[str, Any]]:
        rows = await self.fetch(
            f"SELECT {LIST_COLUMNS} FROM product_categories "
            f"ORDER BY sort_order ASC NULLS LAST, id ASC"
        )
        return [dict(r) for r in rows]

    async def get_by_id(self, category_id: int) -> Optional[dict[str, Any]]:
        row = await self.fetchrow(
            "SELECT id, name, slug, description, sort_order, created_at, updated_at "
            "FROM product_categories WHERE id = $1",
            category_id,
        )
        return dict(row) if row else None

    async def get_product_count(self, category_id: int) -> int:
        count = await self.fetchval(
            "SELECT COUNT(*) FROM products WHERE category_id = $1", category_id
        )
        return int(count or 0)

    async def create(
        self, name: str, slug: str, description: Optional[str] = None
    ) -> dict[str, Any]:
        row = await self.fetchrow(
            "INSERT INTO product_categories (name, slug, description, sort_order) "
            "VALUES ($1, $2, $3, (SELECT COALESCE(MAX(sort_order), -1) + 1 FROM product_categories)) "
            "RETURNING *",
            name,
            slug,
            description,
        )
        return dict(row) if row else {}

    async def update(
        self,
        category_id: int,
        name: Optional[str] = None,
        slug: Optional[str] = None,
        description: Optional[str] = None,
        sort_order: Optional[int] = None,
    ) -> Optional[dict[str, Any]]:
        fields: list[str] = []
        params: list[Any] = []

        if name is not None:
            params.append(name)
            fields.append(f"name = ${len(params)}")
        if slug is not None:
            params.append(slug)
            fields.append(f"slug = ${len(params)}")
        if description is not None:
            params.append(description)
            fields.append(f"description = ${len(params)}")
        if sort_order is not None:
            params.append(sort_order)
            fields.append(f"sort_order = ${len(params)}")

        if not fields:
            return await self.get_by_id(category_id)

        params.append(category_id)
        id_param = len(params)

        row = await self.fetchrow(
            f"UPDATE product_categories SET {', '.join(fields)}, updated_at = NOW() "
            f"WHERE id = ${id_param} RETURNING *",
            *params,
        )
        return dict(row) if row else None

    async def reorder(self, orders: list[dict[str, int]]) -> None:
        for item in orders:
            cat_id = item.get("id")
            sort_order = item.get("sort_order")
            if cat_id is not None and sort_order is not None:
                await self.execute(
                    "UPDATE product_categories SET sort_order = $1 WHERE id = $2",
                    int(sort_order),
                    int(cat_id),
                )

    async def delete(self, category_id: int) -> bool:
        row = await self.fetchrow(
            "DELETE FROM product_categories WHERE id = $1 RETURNING id",
            category_id,
        )
        return row is not None
