"""Product repository isolating SQL operations for products, images, videos, and catalogs."""

from __future__ import annotations

import json
from typing import Any, Optional

from .base import BaseRepository

PRODUCT_SELECT = """
  p.id,
  p.title,
  p.slug,
  p.short_description,
  p.description,
  p.image_url,
  p.url,
  p.badge,
  p.metrics_json,
  p.tags_json,
  p.is_featured,
  p.is_active,
  p.created_at,
  p.updated_at,
  pc.id   AS category_id,
  pc.name AS category_name,
  pc.slug AS category_slug
"""

PRODUCT_FROM = """
  FROM products p
  LEFT JOIN product_categories pc ON p.category_id = pc.id
"""


class ProductRepository(BaseRepository):
    """Encapsulates all database interactions for products and their gallery."""

    async def list_public(
        self, category_slug: Optional[str], limit: int, offset: int
    ) -> tuple[list[dict[str, Any]], int]:
        conditions = ["p.is_active = true"]
        params: list[Any] = []

        if category_slug:
            params.append(category_slug)
            conditions.append(f"pc.slug = ${len(params)}")

        where_clause = "WHERE " + " AND ".join(conditions)

        total = int(
            await self.fetchval(
                f"SELECT COUNT(*) {PRODUCT_FROM} {where_clause}", *params
            )
            or 0
        )

        params.append(limit)
        limit_param = len(params)
        params.append(offset)
        offset_param = len(params)

        rows = await self.fetch(
            f"SELECT {PRODUCT_SELECT} {PRODUCT_FROM} {where_clause} "
            f"ORDER BY p.created_at DESC LIMIT ${limit_param} OFFSET ${offset_param}",
            *params,
        )
        return [dict(r) for r in rows], total

    async def list_admin(self, limit: int, offset: int) -> tuple[list[dict[str, Any]], int]:
        total = int(await self.fetchval("SELECT COUNT(*) FROM products") or 0)
        rows = await self.fetch(
            f"SELECT {PRODUCT_SELECT} {PRODUCT_FROM} "
            f"ORDER BY p.created_at DESC LIMIT $1 OFFSET $2",
            limit,
            offset,
        )
        return [dict(r) for r in rows], total

    async def get_by_id(self, product_id: int) -> Optional[dict[str, Any]]:
        row = await self.fetchrow(
            f"SELECT {PRODUCT_SELECT} {PRODUCT_FROM} WHERE p.id = $1", product_id
        )
        return dict(row) if row else None

    async def get_by_slug(self, slug: str) -> Optional[dict[str, Any]]:
        row = await self.fetchrow(
            f"SELECT {PRODUCT_SELECT} {PRODUCT_FROM} WHERE p.slug = $1", slug
        )
        return dict(row) if row else None

    async def create(
        self,
        title: str,
        slug: str,
        category_id: Optional[int],
        short_description: Optional[str] = None,
        description: Optional[str] = None,
        image_url: Optional[str] = None,
        is_featured: bool = False,
        is_active: bool = True,
        url: Optional[str] = None,
        badge: Optional[str] = None,
        metrics_json: Optional[Any] = None,
        tags_json: Optional[Any] = None,
    ) -> dict[str, Any]:
        if isinstance(metrics_json, (dict, list)):
            metrics_json = json.dumps(metrics_json, ensure_ascii=False)
        if isinstance(tags_json, (dict, list)):
            tags_json = json.dumps(tags_json, ensure_ascii=False)

        row = await self.fetchrow(
            "INSERT INTO products (title, slug, short_description, description, "
            "image_url, category_id, is_featured, is_active, url, badge, metrics_json, tags_json) "
            "VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12) RETURNING *",
            title,
            slug,
            short_description,
            description,
            image_url,
            category_id,
            is_featured,
            is_active,
            url,
            badge,
            metrics_json,
            tags_json,
        )
        return dict(row) if row else {}

    async def update(
        self,
        product_id: int,
        **kwargs: Any,
    ) -> Optional[dict[str, Any]]:
        fields: list[str] = []
        params: list[Any] = []

        for key, value in kwargs.items():
            if value is None:
                continue
            if key in ("metrics_json", "tags_json") and isinstance(value, (dict, list)):
                value = json.dumps(value, ensure_ascii=False)
            params.append(value)
            fields.append(f"{key} = ${len(params)}")

        if not fields:
            return await self.get_by_id(product_id)

        params.append(product_id)
        id_param = len(params)

        row = await self.fetchrow(
            f"UPDATE products SET {', '.join(fields)}, updated_at = NOW() "
            f"WHERE id = ${id_param} RETURNING *",
            *params,
        )
        return dict(row) if row else None

    async def delete(self, product_id: int) -> bool:
        row = await self.fetchrow(
            "DELETE FROM products WHERE id = $1 RETURNING id",
            product_id,
        )
        return row is not None

    async def get_gallery(self, product_id: int) -> dict[str, list[dict[str, Any]]]:
        images = await self.fetch(
            "SELECT * FROM product_images WHERE product_id = $1 ORDER BY sort_order ASC, id ASC",
            product_id,
        )
        videos = await self.fetch(
            "SELECT * FROM product_videos WHERE product_id = $1 ORDER BY sort_order ASC, id ASC",
            product_id,
        )
        catalogs = await self.fetch(
            "SELECT * FROM product_catalogs WHERE product_id = $1 ORDER BY created_at DESC",
            product_id,
        )
        return {
            "images": [dict(r) for r in images],
            "videos": [dict(r) for r in videos],
            "catalogs": [dict(r) for r in catalogs],
        }
