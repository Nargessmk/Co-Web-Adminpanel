"""Product catalogs (PDF/brochure files) — public list + admin CRUD."""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, Request

from .. import db, storage
from ..errors import ApiError
from ..helpers import extract_file, page_limit, pagination, read_body
from ..responses import failure, success
from ..security import AdminContext, require_admin

logger = logging.getLogger("cloudland.catalogs")

router = APIRouter(prefix="/api/catalogs", tags=["Catalogs"])


@router.get("/admin")
async def admin_get_all_catalogs(
    request: Request,
    _admin: AdminContext = Depends(require_admin),
):
    try:
        query = request.query_params
        page, limit, offset = page_limit(query.get("page"), query.get("limit"), 20, 100)

        total = int(await db.fetchval("SELECT COUNT(*) FROM product_catalogs") or 0)
        rows = await db.fetch(
            "SELECT\n"
            "  pc.id,\n"
            "  pc.product_id,\n"
            "  pc.title,\n"
            "  pc.file_url,\n"
            "  pc.created_at,\n"
            "  p.title AS product_title,\n"
            "  p.slug AS product_slug,\n"
            "  p.is_active AS product_is_active\n"
            "FROM product_catalogs pc\n"
            "INNER JOIN products p ON pc.product_id = p.id\n"
            "ORDER BY pc.created_at DESC\n"
            "LIMIT $1 OFFSET $2",
            limit,
            offset,
        )

        return success(
            data=[dict(row) for row in rows],
            pagination=pagination(page, limit, total),
        )
    except Exception:  # noqa: BLE001
        logger.exception("Admin get catalogs error")
        return failure("Failed to fetch catalogs", 500)


@router.get("/admin/product/{product_id}")
async def admin_get_catalogs_by_product_id(
    product_id: int,
    _admin: AdminContext = Depends(require_admin),
):
    try:
        product = await db.fetchrow(
            "SELECT id, title, slug FROM products WHERE id = $1", product_id
        )
        if product is None:
            return failure("Product not found", 404)

        rows = await db.fetch(
            "SELECT pc.id, pc.product_id, pc.title, pc.file_url, pc.created_at\n"
            "FROM product_catalogs pc\n"
            "WHERE pc.product_id = $1\n"
            "ORDER BY pc.created_at DESC",
            product_id,
        )

        return success(
            data={
                "product": dict(product),
                "catalogs": [dict(row) for row in rows],
            }
        )
    except Exception:  # noqa: BLE001
        logger.exception("Admin get catalogs by product error")
        return failure("Failed to fetch catalogs", 500)


@router.get("/product/{slug}")
async def get_catalogs_by_product_slug(slug: str):
    try:
        rows = await db.fetch(
            "SELECT pc.id, pc.product_id, pc.title, pc.file_url, pc.created_at\n"
            "FROM product_catalogs pc\n"
            "INNER JOIN products p ON pc.product_id = p.id\n"
            "WHERE p.slug = $1 AND p.is_active = true\n"
            "ORDER BY pc.created_at DESC",
            slug,
        )
        return success(data=[dict(row) for row in rows])
    except Exception:  # noqa: BLE001
        logger.exception("Error fetching product catalogs")
        return failure("Failed to fetch product catalogs", 500)


@router.post("/admin/product/{product_id}")
async def create_catalog(
    product_id: int,
    request: Request,
    admin: AdminContext = Depends(require_admin),
):
    try:
        body, files = await read_body(request)
        # The old controller always read product_id from the body payload.
        target_product = body.get("product_id") or product_id
        title = body.get("title")

        if not target_product or not title:
            return failure("عنوان و محصول الزامی هستند", 400)

        product = await db.fetchrow(
            "SELECT id FROM products WHERE id = $1", int(target_product)
        )
        if product is None:
            return failure("Product not found", 404)

        file_url = None
        upload = await extract_file(files, "file")
        if upload is not None:
            stored = await storage.upload_file(
                buffer=upload.buffer,
                originalname=upload.originalname,
                mimetype=upload.mimetype,
                folder="catalogs",
                token=admin.token,
                title=title,
                record_id=target_product,
            )
            file_url = storage.stored_value(stored)
            logger.info("[catalogs] file stored via %s: %s", stored["source"], file_url)
        elif body.get("file_url"):
            file_url = storage.to_object_key(body.get("file_url"))

        if not file_url:
            return failure("آپلود فایل یا لینک فایل الزامی است", 400)

        row = await db.fetchrow(
            "INSERT INTO product_catalogs (product_id, title, file_url) "
            "VALUES ($1, $2, $3) RETURNING *",
            int(target_product),
            title,
            file_url,
        )
        try:
            from .media import register_media
            await register_media(
                file_url=file_url,
                folder="catalogs",
                original_name=upload.originalname if upload else title,
                file_type="document",
                size_bytes=len(upload.buffer) if upload else 0,
                mimetype=upload.mimetype if upload else "application/pdf",
            )
        except Exception as exc:
            logger.debug("Failed to register catalog in media_files: %s", exc)

        return success(message="Catalog created", data=row, status_code=201)
    except ApiError as error:
        return failure(error.message, error.status_code)
    except Exception:  # noqa: BLE001
        logger.exception("Create catalog error")
        return failure("Failed to create catalog", 500)


@router.put("/admin/{catalog_id}")
async def update_catalog(
    catalog_id: int,
    request: Request,
    admin: AdminContext = Depends(require_admin),
):
    try:
        body, files = await read_body(request)
        title = body.get("title")

        existing = await db.fetchrow(
            "SELECT id, file_url FROM product_catalogs WHERE id = $1", catalog_id
        )
        if existing is None:
            return failure("Catalog not found", 404)

        previous_file = existing["file_url"]
        file_url = previous_file

        upload = await extract_file(files, "file")
        if upload is not None:
            stored = await storage.upload_file(
                buffer=upload.buffer,
                originalname=upload.originalname,
                mimetype=upload.mimetype,
                folder="catalogs",
                token=admin.token,
                title=title,
            )
            file_url = storage.stored_value(stored)
            logger.info("[catalogs] file replaced via %s: %s", stored["source"], file_url)
            # Remove the replaced file (best effort — never blocks the update).
            if previous_file and previous_file != file_url:
                await storage.remove_stored_file(previous_file, admin.token, admin.app_id)
        elif "file_url" in body:
            file_url = storage.to_object_key(body.get("file_url"))

        row = await db.fetchrow(
            "UPDATE product_catalogs SET\n"
            "  title = COALESCE($2, title),\n"
            "  file_url = $3\n"
            "WHERE id = $1\n"
            "RETURNING *",
            catalog_id,
            title or None,
            file_url,
        )
        return success(message="Catalog updated", data=row)
    except ApiError as error:
        return failure(error.message, error.status_code)
    except Exception:  # noqa: BLE001
        logger.exception("Update catalog error")
        return failure("Failed to update catalog", 500)


@router.delete("/admin/{catalog_id}")
async def delete_catalog(
    catalog_id: int,
    admin: AdminContext = Depends(require_admin),
):
    try:
        row = await db.fetchrow(
            "DELETE FROM product_catalogs WHERE id = $1 RETURNING id, title, file_url",
            catalog_id,
        )
        if row is None:
            return failure("Catalog not found", 404)

        await storage.remove_stored_file(row["file_url"], admin.token, admin.app_id)
        return success(message="Catalog deleted", data=row)
    except Exception:  # noqa: BLE001
        logger.exception("Delete catalog error")
        return failure("Failed to delete catalog", 500)
