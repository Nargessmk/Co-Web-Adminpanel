"""Product categories: GET /api/categories (public) + admin CRUD.

Refactored to Clean Architecture with CategoryRepository and Pydantic validation.
"""

from __future__ import annotations

import logging
from typing import Optional

from asyncpg.exceptions import UniqueViolationError
from fastapi import APIRouter, Depends, Request

from ..helpers import read_body, to_int
from ..repositories.category_repo import CategoryRepository
from ..responses import failure, success
from ..schemas.category import CategoryCreateDTO, CategoryUpdateDTO
from ..security import AdminContext, require_admin

logger = logging.getLogger("cloudland.categories")

router = APIRouter(prefix="/api/categories", tags=["Categories"])


@router.get("", tags=["Categories - Public"])
async def get_categories(repo: CategoryRepository = Depends()):
    try:
        categories = await repo.list_all()
        return success(data=categories)
    except Exception:  # noqa: BLE001
        logger.exception("Error fetching categories")
        return failure("Failed to fetch categories", 500)


@router.get("/admin/{category_id}", tags=["Categories - Admin"])
async def get_category_by_id(
    category_id: int,
    _admin: AdminContext = Depends(require_admin),
    repo: CategoryRepository = Depends(),
):
    try:
        category = await repo.get_by_id(category_id)
        if category is None:
            return failure("Category not found", 404)
        return success(data=category)
    except Exception:  # noqa: BLE001
        logger.exception("Get category error")
        return failure("Failed to fetch category", 500)


@router.get("/admin/{category_id}/count", tags=["Categories - Admin"])
async def get_category_product_count(
    category_id: int,
    _admin: AdminContext = Depends(require_admin),
    repo: CategoryRepository = Depends(),
):
    try:
        count = await repo.get_product_count(category_id)
        return success(data={"count": count})
    except Exception:  # noqa: BLE001
        logger.exception("Get category product count error")
        return failure("Failed to get product count", 500)


@router.post("/admin", tags=["Categories - Admin"])
async def create_category(
    request: Request,
    _admin: AdminContext = Depends(require_admin),
    repo: CategoryRepository = Depends(),
):
    try:
        body, _files = await read_body(request)
        name = body.get("name")
        slug = body.get("slug")
        description = body.get("description")

        if not name or not slug:
            return failure("نام و نامک دسته‌بندی الزامی هستند", 400)

        # Validate with DTO
        dto = CategoryCreateDTO(name=name, slug=slug, description=description)

        try:
            row = await repo.create(dto.name, dto.slug, dto.description)
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
    repo: CategoryRepository = Depends(),
):
    try:
        body, _files = await read_body(request)
        existing = await repo.get_by_id(category_id)
        if existing is None:
            return failure("Category not found", 404)

        name = body.get("name")
        slug = body.get("slug")
        description = body.get("description")
        sort_order = body.get("sort_order")

        order = None if sort_order is None or sort_order == "" else to_int(sort_order)
        dto = CategoryUpdateDTO(name=name, slug=slug, description=description)

        try:
            row = await repo.update(
                category_id,
                name=dto.name,
                slug=dto.slug,
                description=dto.description,
                sort_order=order,
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
    repo: CategoryRepository = Depends(),
):
    try:
        existing = await repo.get_by_id(category_id)
        if existing is None:
            return failure("Category not found", 404)

        # Delete products of this category first (cascade), then the category.
        from .. import db
        async with db.pool().acquire() as connection:
            async with connection.transaction():
                await connection.execute(
                    "DELETE FROM products WHERE category_id = $1", category_id
                )
                row = await connection.fetchrow(
                    "DELETE FROM product_categories WHERE id = $1 RETURNING id, name",
                    category_id,
                )

        return success(message="Category and related products deleted", data=dict(row) if row else {})
    except Exception:  # noqa: BLE001
        logger.exception("Delete category error")
        return failure("Failed to delete category", 500)
