"""Products: public catalogue + full admin CRUD (images, videos, gallery)."""

from __future__ import annotations

import logging
import os
import subprocess
import tempfile

from asyncpg.exceptions import UniqueViolationError
from fastapi import APIRouter, Depends, Request

from .. import config, db, storage
from ..errors import ApiError
from ..helpers import (
    extract_file,
    js_bool,
    optional_bool,
    page_limit,
    pagination,
    read_body,
    to_int,
)
from ..repositories.product_repo import ProductRepository
from ..responses import failure, success
from ..schemas.product import ProductCreateDTO, ProductUpdateDTO
from ..security import AdminContext, require_admin

logger = logging.getLogger("cloudland.products")


def extract_video_thumbnail(video_buffer: bytes) -> bytes | None:
    """Extract a thumbnail JPEG frame at 1s using ffmpeg if available on the system."""
    try:
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp_in:
            tmp_in.write(video_buffer)
            tmp_in_path = tmp_in.name

        tmp_out_path = tmp_in_path + ".jpg"
        try:
            res = subprocess.run(
                [
                    "ffmpeg", "-y", "-ss", "00:00:01", "-i", tmp_in_path,
                    "-vframes", "1", "-q:v", "2", "-f", "image2", tmp_out_path
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=15,
            )
            if res.returncode == 0 and os.path.exists(tmp_out_path):
                with open(tmp_out_path, "rb") as f:
                    return f.read()
        finally:
            if os.path.exists(tmp_in_path):
                try:
                    os.remove(tmp_in_path)
                except OSError:
                    pass
            if os.path.exists(tmp_out_path):
                try:
                    os.remove(tmp_out_path)
                except OSError:
                    pass
    except Exception:
        logger.warning("Auto-thumbnail extraction with ffmpeg failed or ffmpeg not installed", exc_info=True)
    return None

# NOTE: route ORDER matters — the literal /admin/... paths are declared before
# the parameterised ones (FastAPI matches in declaration order), and the
# /admin/videos|images/reorder routes before /admin/videos|images/{id}.
router = APIRouter(prefix="/api/products", tags=["Products"])

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


async def _store_image(files: dict, field: str, folder: str, admin: AdminContext, title: str | None = None):
    upload = await extract_file(files, field)
    if upload is None:
        return None
    stored = await storage.upload_file(
        buffer=upload.buffer,
        originalname=upload.originalname,
        mimetype=upload.mimetype,
        folder=folder,
        token=admin.token,
        title=title,
    )
    logger.info("[products] image stored via %s: %s", stored["source"], stored["url"])
    # The object key goes to Postgres, not the public URL.
    return storage.stored_value(stored)


@router.get("", tags=["Products - Public"])
async def get_products(
    request: Request,
    repo: ProductRepository = Depends(),
):
    try:
        query = request.query_params
        category = query.get("category")
        page, limit, offset = page_limit(query.get("page"), query.get("limit"), 6, 50)

        rows, total = await repo.list_public(category, limit, offset)

        return success(
            data=rows,
            pagination=pagination(page, limit, total),
        )
    except Exception:  # noqa: BLE001
        logger.exception("Error fetching products")
        return failure("Failed to fetch products", 500)


@router.get("/admin/all", tags=["Products - Admin"])
async def admin_get_products(
    request: Request,
    _admin: AdminContext = Depends(require_admin),
    repo: ProductRepository = Depends(),
):
    try:
        query = request.query_params
        page, limit, offset = page_limit(query.get("page"), query.get("limit"), 20, 100)

        rows, total = await repo.list_admin(limit, offset)

        return success(
            data=rows,
            pagination=pagination(page, limit, total),
        )
    except Exception:  # noqa: BLE001
        logger.exception("Admin get products error")
        return failure("Failed to fetch products", 500)


@router.get("/admin/{product_id}", tags=["Products - Admin"])
async def admin_get_product_by_id(
    product_id: int,
    _admin: AdminContext = Depends(require_admin),
    repo: ProductRepository = Depends(),
):
    try:
        row = await repo.get_by_id(product_id)
        if row is None:
            return failure("Product not found", 404)
        return success(data=row)
    except Exception:  # noqa: BLE001
        logger.exception("Admin get product error")
        return failure("Failed to fetch product", 500)


@router.post("/admin", tags=["Products - Admin"])
async def create_product(
    request: Request,
    admin: AdminContext = Depends(require_admin),
    repo: ProductRepository = Depends(),
):
    try:
        body, files = await read_body(request)
        title, slug, category_id = body.get("title"), body.get("slug"), body.get("category_id")

        if not title or not slug or not category_id:
            return failure("عنوان، نامک و دسته‌بندی الزامی هستند", 400)

        # Validate with DTO
        dto = ProductCreateDTO(
            title=str(title).strip(),
            slug=str(slug).strip(),
            category_id=to_int(category_id),
            short_description=body.get("short_description") or None,
            description=body.get("description") or None,
            url=body.get("url") or None,
            badge=body.get("badge") or None,
            is_featured=js_bool(body.get("is_featured")),
            is_active=True if body.get("is_active") is None else js_bool(body.get("is_active")),
            metrics_json=body.get("metrics_json") or body.get("metrics"),
            tags_json=body.get("tags_json") or body.get("tags"),
        )

        image_url = storage.to_object_key(body.get("image_url")) or None
        uploaded = await _store_image(files, "image", "products", admin, title=dto.title)
        if uploaded:
            image_url = uploaded
            try:
                from .media import register_media
                await register_media(
                    file_url=uploaded,
                    folder="products",
                    original_name=dto.title,
                    file_type="image",
                )
            except Exception:
                pass

        try:
            row = await repo.create(
                title=dto.title,
                slug=dto.slug,
                category_id=dto.category_id,
                short_description=dto.short_description,
                description=dto.description,
                image_url=image_url,
                is_featured=dto.is_featured,
                is_active=dto.is_active,
                url=dto.url,
                badge=dto.badge,
                metrics_json=dto.metrics_json,
                tags_json=dto.tags_json,
            )
        except UniqueViolationError:
            return failure("A product with this slug already exists", 409)

        return success(message="Product created", data=row, status_code=201)
    except ApiError as error:
        return failure(error.message, error.status_code)
    except Exception:  # noqa: BLE001
        logger.exception("Create product error")
        return failure("Failed to create product", 500)


@router.put("/admin/{product_id}", tags=["Products - Admin"])
async def update_product(
    product_id: int,
    request: Request,
    admin: AdminContext = Depends(require_admin),
):
    try:
        body, files = await read_body(request)

        existing = await db.fetchrow(
            "SELECT id, image_url FROM products WHERE id = $1", product_id
        )
        if existing is None:
            return failure("Product not found", 404)

        # Keep the old image unless a new file (or an explicit image_url) arrives.
        previous_image = existing["image_url"]
        image_url = previous_image
        uploaded = await _store_image(
            files, "image", "products", admin, title=body.get("title")
        )
        if uploaded:
            image_url = uploaded
            try:
                from .media import register_media
                await register_media(
                    file_url=uploaded,
                    folder="products",
                    original_name=body.get("title") or "product",
                    file_type="image",
                )
            except Exception:
                pass
            if previous_image and previous_image != image_url:
                await storage.remove_stored_file(previous_image, admin.token, admin.app_id)
        elif "image_url" in body:
            image_url = storage.to_object_key(body.get("image_url"))

        title, slug = body.get("title"), body.get("slug")
        short_description, description = body.get("short_description"), body.get("description")
        category_id, url = body.get("category_id"), body.get("url")
        is_featured, is_active = body.get("is_featured"), body.get("is_active")
        badge = body.get("badge")

        metrics_val = body.get("metrics_json") or body.get("metrics")
        if isinstance(metrics_val, (dict, list)):
            import json
            metrics_val = json.dumps(metrics_val, ensure_ascii=False)

        tags_val = body.get("tags_json") or body.get("tags")
        if isinstance(tags_val, (dict, list)):
            import json
            tags_val = json.dumps(tags_val, ensure_ascii=False)

        try:
            row = await db.fetchrow(
                "UPDATE products SET\n"
                "  title = COALESCE($2, title),\n"
                "  slug = COALESCE($3, slug),\n"
                "  short_description = COALESCE($4, short_description),\n"
                "  description = COALESCE($5, description),\n"
                "  image_url = $6,\n"
                "  category_id = COALESCE($7, category_id),\n"
                "  is_featured = COALESCE($8, is_featured),\n"
                "  is_active = COALESCE($9, is_active),\n"
                "  url = COALESCE($10, url),\n"
                "  badge = COALESCE($11, badge),\n"
                "  metrics_json = COALESCE($12, metrics_json),\n"
                "  tags_json = COALESCE($13, tags_json),\n"
                "  updated_at = CURRENT_TIMESTAMP\n"
                "WHERE id = $1\n"
                "RETURNING *",
                product_id,
                title or None,
                slug or None,
                short_description if short_description is not None else None,
                description if description is not None else None,
                image_url,
                to_int(category_id) if category_id not in (None, "") else None,
                None if is_featured is None else js_bool(is_featured),
                optional_bool(is_active),
                (url or None) if url is not None else None,
                (badge or None) if badge is not None else None,
                (metrics_val or None) if metrics_val is not None else None,
                (tags_val or None) if tags_val is not None else None,
            )
        except UniqueViolationError:
            return failure("A product with this slug already exists", 409)

        return success(message="Product updated", data=row)
    except ApiError as error:
        return failure(error.message, error.status_code)
    except Exception:  # noqa: BLE001
        logger.exception("Update product error")
        return failure("Failed to update product", 500)


@router.put("/admin/videos/reorder", tags=["Products - Admin"])
async def reorder_product_videos(
    request: Request,
    admin: AdminContext = Depends(require_admin),
):
    try:
        body, _files = await read_body(request)
        videos = body.get("videos")

        if not isinstance(videos, list) or not videos:
            return failure("videos array is required", 400)

        async with db.pool().acquire() as connection:
            async with connection.transaction():
                for item in videos:
                    if not isinstance(item, dict):
                        continue
                    if not item.get("id") or item.get("sort_order") is None:
                        continue
                    await connection.execute(
                        "UPDATE product_videos SET sort_order = $1 WHERE id = $2",
                        to_int(item.get("sort_order")),
                        to_int(item.get("id")),
                    )

        return success(message="Videos reordered")
    except Exception:  # noqa: BLE001
        logger.exception("Reorder product videos error")
        return failure("Failed to reorder videos", 500)


@router.put("/admin/videos/{video_id}", tags=["Products - Admin"])
async def update_product_video(
    video_id: int,
    request: Request,
    admin: AdminContext = Depends(require_admin),
):
    try:
        body, files = await read_body(request)

        existing = await db.fetchrow(
            "SELECT * FROM product_videos WHERE id = $1", video_id
        )
        if existing is None:
            return failure("Video not found", 404)

        current = dict(existing)
        video_url = current["video_url"]

        # Optional: replace the video file. Upload the new object FIRST so a
        # failure leaves the old file intact.
        upload = await extract_file(
            files,
            "video",
            max_mb=config.MAX_PRODUCT_VIDEO_MB,
        )
        if upload is not None:
            stored = await storage.upload_file(
                buffer=upload.buffer,
                originalname=upload.originalname,
                mimetype=upload.mimetype,
                folder="products/videos",
                token=admin.token,
                title=f"product-{current['product_id']}",
            )
            await storage.remove_stored_file(
                current["video_url"], admin.token, admin.app_id
            )
            video_url = storage.stored_value(stored)

        title = body.get("title")
        if title is None or title == "":
            title = current.get("title")

        row = await db.fetchrow(
            "UPDATE product_videos SET video_url = $1, title = $2 WHERE id = $3 RETURNING *",
            video_url,
            title,
            video_id,
        )
        return success(message="Video updated", data=row)
    except ApiError as error:
        return failure(error.message, error.status_code)
    except Exception:  # noqa: BLE001
        logger.exception("Update product video error")
        return failure("Failed to update video", 500)


@router.delete("/admin/videos/{video_id}", tags=["Products - Admin"])
async def delete_product_video(
    video_id: int,
    admin: AdminContext = Depends(require_admin),
):
    try:
        row = await db.fetchrow(
            "DELETE FROM product_videos WHERE id = $1 RETURNING id, video_url, thumbnail_url, product_id",
            video_id,
        )
        if row is None:
            return failure("Video not found", 404)

        await storage.remove_stored_file(row["video_url"], admin.token, admin.app_id)
        if row.get("thumbnail_url"):
            await storage.remove_stored_file(row["thumbnail_url"], admin.token, admin.app_id)
        return success(message="Video deleted")
    except Exception:  # noqa: BLE001
        logger.exception("Delete product video error")
        return failure("Failed to delete video", 500)


@router.put("/admin/images/reorder", tags=["Products - Admin"])
async def reorder_product_images(
    request: Request,
    admin: AdminContext = Depends(require_admin),
):
    try:
        body, _files = await read_body(request)
        images = body.get("images")

        if not isinstance(images, list) or not images:
            return failure("images array is required", 400)

        async with db.pool().acquire() as connection:
            async with connection.transaction():
                for item in images:
                    if not isinstance(item, dict):
                        continue
                    if not item.get("id") or item.get("sort_order") is None:
                        continue
                    await connection.execute(
                        "UPDATE product_images SET sort_order = $1 WHERE id = $2",
                        to_int(item.get("sort_order")),
                        to_int(item.get("id")),
                    )

        return success(message="Images reordered")
    except Exception:  # noqa: BLE001
        logger.exception("Reorder product images error")
        return failure("Failed to reorder images", 500)


@router.put("/admin/images/{image_id}", tags=["Products - Admin"])
async def update_product_image(
    image_id: int,
    request: Request,
    admin: AdminContext = Depends(require_admin),
):
    try:
        _body, files = await read_body(request)

        existing = await db.fetchrow(
            "SELECT * FROM product_images WHERE id = $1", image_id
        )
        if existing is None:
            return failure("Image not found", 404)

        upload = await extract_file(files, "image")
        if upload is None:
            return failure("No image file provided", 400)

        current = dict(existing)

        # Upload the new object FIRST so a failure leaves the old file intact.
        stored = await storage.upload_file(
            buffer=upload.buffer,
            originalname=upload.originalname,
            mimetype=upload.mimetype,
            folder="products/gallery",
            token=admin.token,
            title=f"product-{current['product_id']}",
        )

        row = await db.fetchrow(
            "UPDATE product_images SET image_url = $1 WHERE id = $2 RETURNING *",
            storage.stored_value(stored),
            image_id,
        )
        await storage.remove_stored_file(
            current["image_url"], admin.token, admin.app_id
        )

        return success(message="Image updated", data=row)
    except ApiError as error:
        return failure(error.message, error.status_code)
    except Exception:  # noqa: BLE001
        logger.exception("Update product image error")
        return failure("Failed to update image", 500)


@router.delete("/admin/images/{image_id}", tags=["Products - Admin"])
async def delete_product_image(
    image_id: int,
    admin: AdminContext = Depends(require_admin),
):
    try:
        row = await db.fetchrow(
            "DELETE FROM product_images WHERE id = $1 RETURNING id, image_url, product_id",
            image_id,
        )
        if row is None:
            return failure("Image not found", 404)

        await storage.remove_stored_file(row["image_url"], admin.token, admin.app_id)
        return success(message="Image deleted")
    except Exception:  # noqa: BLE001
        logger.exception("Delete product image error")
        return failure("Failed to delete image", 500)


@router.post("/admin/{product_id}/images", tags=["Products - Admin"])
async def upload_product_image(
    product_id: int,
    request: Request,
    admin: AdminContext = Depends(require_admin),
):
    try:
        _body, files = await read_body(request)

        existing = await db.fetchrow(
            "SELECT id FROM products WHERE id = $1", product_id
        )
        if existing is None:
            return failure("Product not found", 404)

        upload = await extract_file(files, "image")
        if upload is None:
            return failure("No image file provided", 400)

        stored = await storage.upload_file(
            buffer=upload.buffer,
            originalname=upload.originalname,
            mimetype=upload.mimetype,
            folder="products/gallery",
            token=admin.token,
            title=f"product-{product_id}",
        )

        next_order = await db.fetchval(
            "SELECT COALESCE(MAX(sort_order), -1) + 1 FROM product_images WHERE product_id = $1",
            product_id,
        )
        val = storage.stored_value(stored)
        row = await db.fetchrow(
            "INSERT INTO product_images (product_id, image_url, sort_order) "
            "VALUES ($1, $2, $3) RETURNING *",
            product_id,
            val,
            int(next_order or 0),
        )
        try:
            from .media import register_media
            await register_media(
                file_url=val,
                folder="products",
                original_name=upload.originalname,
                file_type="image",
                size_bytes=len(upload.buffer),
                mimetype=upload.mimetype,
            )
        except Exception as exc:
            logger.debug("Failed to register image in media_files: %s", exc)

        return success(message="Image uploaded", data=row, status_code=201)
    except ApiError as error:
        return failure(error.message, error.status_code)
    except Exception:  # noqa: BLE001
        logger.exception("Upload product image error")
        return failure("Failed to upload image", 500)


@router.post("/admin/{product_id}/videos", tags=["Products - Admin"])
async def upload_product_video(
    product_id: int,
    request: Request,
    admin: AdminContext = Depends(require_admin),
):
    try:
        body, files = await read_body(request)

        existing = await db.fetchrow(
            "SELECT id FROM products WHERE id = $1", product_id
        )
        if existing is None:
            return failure("Product not found", 404)

        upload = await extract_file(
            files, "video", max_mb=config.MAX_PRODUCT_VIDEO_MB
        )
        if upload is None:
            return failure("No video file provided", 400)

        stored = await storage.upload_file(
            buffer=upload.buffer,
            originalname=upload.originalname,
            mimetype=upload.mimetype,
            folder="products/videos",
            token=admin.token,
            title=f"product-{product_id}",
        )

        # Check if an explicit thumbnail image was sent, or auto-extract with ffmpeg
        thumb_upload = await extract_file(files, "thumbnail", max_mb=10)
        thumbnail_url = None

        if thumb_upload is not None:
            stored_thumb = await storage.upload_file(
                buffer=thumb_upload.buffer,
                originalname=thumb_upload.originalname,
                mimetype=thumb_upload.mimetype,
                folder="products/thumbnails",
                token=admin.token,
                title=f"product-{product_id}-thumb",
            )
            thumbnail_url = storage.stored_value(stored_thumb)
        else:
            extracted_thumb_bytes = extract_video_thumbnail(upload.buffer)
            if extracted_thumb_bytes:
                stored_thumb = await storage.upload_file(
                    buffer=extracted_thumb_bytes,
                    originalname=f"thumb-{upload.originalname}.jpg",
                    mimetype="image/jpeg",
                    folder="products/thumbnails",
                    token=admin.token,
                    title=f"product-{product_id}-thumb",
                )
                thumbnail_url = storage.stored_value(stored_thumb)

        next_order = await db.fetchval(
            "SELECT COALESCE(MAX(sort_order), -1) + 1 FROM product_videos WHERE product_id = $1",
            product_id,
        )
        val = storage.stored_value(stored)
        row = await db.fetchrow(
            "INSERT INTO product_videos (product_id, video_url, thumbnail_url, sort_order, title) "
            "VALUES ($1, $2, $3, $4, $5) RETURNING *",
            product_id,
            val,
            thumbnail_url,
            int(next_order or 0),
            body.get("title") or "Product Video",
        )
        try:
            from .media import register_media
            await register_media(
                file_url=val,
                folder="products",
                original_name=upload.originalname,
                file_type="video",
                size_bytes=len(upload.buffer),
                mimetype=upload.mimetype,
            )
            if thumbnail_url:
                await register_media(
                    file_url=thumbnail_url,
                    folder="products",
                    original_name=f"thumb-{upload.originalname}",
                    file_type="image",
                    mimetype="image/jpeg",
                )
        except Exception as exc:
            logger.debug("Failed to register video in media_files: %s", exc)

        return success(message="Video uploaded", data=row, status_code=201)
    except ApiError as error:
        return failure(error.message, error.status_code)
    except Exception:  # noqa: BLE001
        logger.exception("Upload product video error")
        return failure("Failed to upload video", 500)


@router.delete("/admin/{product_id}/image", tags=["Products - Admin"])
async def delete_product_profile_image(
    product_id: int,
    admin: AdminContext = Depends(require_admin),
):
    try:
        row = await db.fetchrow(
            "UPDATE products SET image_url = NULL, updated_at = CURRENT_TIMESTAMP "
            "WHERE id = $1 RETURNING id, image_url",
            product_id,
        )
        if row is None:
            return failure("Product not found", 404)

        old_url = row["image_url"]
        if old_url:
            await storage.remove_stored_file(old_url, admin.token, admin.app_id)

        return success(message="Product image deleted")
    except Exception:  # noqa: BLE001
        logger.exception("Delete product profile image error")
        return failure("Failed to delete product image", 500)


@router.delete("/admin/{product_id}", tags=["Products - Admin"])
async def delete_product(
    product_id: int,
    admin: AdminContext = Depends(require_admin),
):
    try:
        # Remove the associated catalog files first (MinIO objects or disk files).
        catalogs = await db.fetch(
            "SELECT file_url FROM product_catalogs WHERE product_id = $1", product_id
        )
        for catalog in catalogs:
            await storage.remove_stored_file(catalog["file_url"], admin.token, admin.app_id)
        await db.execute("DELETE FROM product_catalogs WHERE product_id = $1", product_id)

        row = await db.fetchrow(
            "DELETE FROM products WHERE id = $1 RETURNING id, title, image_url",
            product_id,
        )
        if row is None:
            return failure("Product not found", 404)

        await storage.remove_stored_file(row["image_url"], admin.token, admin.app_id)
        return success(message="Product deleted", data=row)
    except Exception:  # noqa: BLE001
        logger.exception("Delete product error")
        return failure("Failed to delete product", 500)


@router.get("/{product_id}/images", tags=["Products - Public"])
async def list_product_images(product_id: int):
    try:
        rows = await db.fetch(
            "SELECT id, image_url, sort_order FROM product_images WHERE product_id = $1 "
            "ORDER BY sort_order ASC, created_at ASC",
            product_id,
        )
        return success(data=[dict(row) for row in rows])
    except Exception:  # noqa: BLE001
        logger.exception("List product images error")
        return failure("Failed to fetch product images", 500)


@router.get("/{product_id}/videos", tags=["Products - Public"])
async def list_product_videos(product_id: int):
    try:
        rows = await db.fetch(
            "SELECT id, video_url, thumbnail_url, sort_order, title FROM product_videos WHERE product_id = $1 "
            "ORDER BY sort_order ASC, created_at ASC",
            product_id,
        )
        return success(data=[dict(row) for row in rows])
    except Exception:  # noqa: BLE001
        logger.exception("List product videos error")
        return failure("Failed to fetch product videos", 500)


@router.get("/{slug}", tags=["Products - Public"])
async def get_product_by_slug(slug: str):
    try:
        row = await db.fetchrow(
            f"SELECT {PRODUCT_SELECT} {PRODUCT_FROM} WHERE p.slug = $1 AND p.is_active = true",
            slug,
        )
        if row is None:
            return failure("Product not found", 404)
        return success(data=row)
    except Exception:  # noqa: BLE001
        logger.exception("Error fetching product")
        return failure("Failed to fetch product", 500)
