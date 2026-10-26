"""Product categories: GET /api/categories (public) + admin CRUD."""

from __future__ import annotations

import logging

from asyncpg.exceptions import UniqueViolationError
from fastapi import APIRouter, Depends, Request

from .. import db
from ..helpers import read_body, to_int
from ..responses import failure, success
from ..security import AdminContext, require_admin

logger = logging.getLogger("cloudland.categories")

router = APIRouter(prefix="/api/categories", tags=["Categories"])

LIST_COLUMNS = "id, name, slug, description, sort_order, created_at"


@router.get("", tags=["Categories - Public"])
async def get_categories():
    try:
        rows = await db.fetch(
            f"SELECT {LIST_COLUMNS} FROM product_categories "
            f"ORDER BY sort_order ASC NULLS LAST, id ASC"
        )
        return success(data=[dict(row) for row in rows])
    except Exception:  # noqa: BLE001
        logger.exception("Error fetching categories")
        return failure("Failed to fetch categories", 500)


@router.get("/admin/{category_id}", tags=["Categories - Admin"])
async def get_category_by_id(
    category_id: int,
    _admin: AdminContext = Depends(require_admin),
):
    try:
        row = await db.fetchrow(
            "SELECT id, name, slug, description, created_at, updated_at "
            "FROM product_categories WHERE id = $1",
            category_id,
        )
        if row is None:
            return failure("Category not found", 404)
        return success(data=row)
    except Exception:  # noqa: BLE001
        logger.exception("Get category error")
        return failure("Failed to fetch category", 500)


@router.get("/admin/{category_id}/count", tags=["Categories - Admin"])
async def get_category_product_count(
    category_id: int,
    _admin: AdminContext = Depends(require_admin),
):
    try:
        count = await db.fetchval(
            "SELECT COUNT(*) FROM products WHERE category_id = $1", category_id
        )
        return success(data={"count": int(count or 0)})
    except Exception:  # noqa: BLE001
        logger.exception("Get category product count error")
        return failure("Failed to get product count", 500)


@router.post("/admin", tags=["Categories - Admin"])
async def create_category(
    request: Request,
    _admin: AdminContext = Depends(require_admin),
):
    try:
        body, _files = await read_body(request)
        name = body.get("name")
        slug = body.get("slug")
        description = body.get("description")

        if not name or not slug:
            return failure("نام و نامک دسته‌بندی الزامی هستند", 400)

        try:
            row = await db.fetchrow(
                "INSERT INTO product_categories (name, slug, description, sort_order) "
                "VALUES ($1, $2, $3, (SELECT COALESCE(MAX(sort_order), -1) + 1 "
                "FROM product_categories)) RETURNING *",
                name,
                slug,
                description or None,
            )
        except UniqueViolationError:
            return failure("A category with this slug already exists", 409)

        return success(message="Category created", data=row, status_code=201)
    except Exception:  # noqa: BLE001
        logger.exception("Create category error")
        return failure("Failed to create category", 500)


@router.put("/admin/{category_id}", tags=["Categories - Admin"])
async def update_category(
    category_id: int,
    request: Request,
    _admin: AdminContext = Depends(require_admin),
):
    try:
        body, _files = await read_body(request)
        name = body.get("name")
        slug = body.get("slug")
        description = body.get("description")
        sort_order = body.get("sort_order")

        existing = await db.fetchrow(
            "SELECT id FROM product_categories WHERE id = $1", category_id
        )
        if existing is None:
            return failure("Category not found", 404)

        order = None if sort_order is None or sort_order == "" else to_int(sort_order)

        try:
            row = await db.fetchrow(
                "UPDATE product_categories SET\n"
                "  name = COALESCE($2, name),\n"
                "  slug = COALESCE($3, slug),\n"
                "  description = COALESCE($4, description),\n"
                "  sort_order = COALESCE($5, sort_order),\n"
                "  updated_at = CURRENT_TIMESTAMP\n"
                "WHERE id = $1\n"
                "RETURNING *",
                category_id,
                name or None,
                slug or None,
                description if description is not None else None,
                order,
            )
        except UniqueViolationError:
            return failure("A category with this slug already exists", 409)

        return success(message="Category updated", data=row)
    except Exception:  # noqa: BLE001
        logger.exception("Update category error")
        return failure("Failed to update category", 500)


@router.delete("/admin/{category_id}", tags=["Categories - Admin"])
async def delete_category(
    category_id: int,
    _admin: AdminContext = Depends(require_admin),
):
    try:
        existing = await db.fetchrow(
            "SELECT id, name FROM product_categories WHERE id = $1", category_id
        )
        if existing is None:
            return failure("Category not found", 404)

        # Delete products of this category first (cascade), then the category.
        async with db.pool().acquire() as connection:
            async with connection.transaction():
                await connection.execute(
                    "DELETE FROM products WHERE category_id = $1", category_id
                )
                row = await connection.fetchrow(
                    "DELETE FROM product_categories WHERE id = $1 RETURNING id, name",
                    category_id,
                )

        return success(message="Category and related products deleted", data=row)
    except Exception:  # noqa: BLE001
        logger.exception("Delete category error")
        return failure("Failed to delete category", 500)
