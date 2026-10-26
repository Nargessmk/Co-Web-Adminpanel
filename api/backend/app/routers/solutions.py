"""Solution articles ("راهکارها"): public list/detail + admin CRUD."""

from __future__ import annotations

import logging
import re
import time
import unicodedata

from fastapi import APIRouter, Depends, Request

from .. import db, storage
from ..errors import ApiError
from ..helpers import (
    bool_default_true,
    extract_file,
    int_or_null,
    js_bool,
    page_limit,
    pagination,
    read_body,
)
from ..responses import failure, success
from ..security import AdminContext, require_admin
from .. import config

logger = logging.getLogger("cloudland.solutions")

router = APIRouter(prefix="/api/solutions", tags=["Solutions"])

SELECT_COLUMNS = """
  a.id,
  a.title,
  a.slug,
  a.summary,
  a.content,
  a.image_url,
  a.source_title,
  a.source_url,
  a.category,
  a.read_time,
  a.topic,
  a.tags,
  a.related_product_id,
  a.author_id,
  a.is_active,
  a.created_at,
  a.updated_at,
  p.id                 AS product_id,
  p.title              AS product_title,
  p.slug               AS product_slug,
  p.image_url          AS product_image_url,
  p.short_description  AS product_short_description,
  t.id                 AS author_id_public,
  t.full_name          AS author_name,
  t.role               AS author_role,
  t.image_url          AS author_image_url,
  t.linkedin_url       AS author_linkedin_url
"""

ADMIN_JOINS = """
  FROM solution_articles a
  LEFT JOIN products p ON a.related_product_id = p.id
  LEFT JOIN team_members t ON a.author_id = t.id
"""

PUBLIC_JOINS = """
  FROM solution_articles a
  LEFT JOIN products p ON a.related_product_id = p.id AND p.is_active = true
  LEFT JOIN team_members t ON a.author_id = t.id AND t.is_active = true
"""


def slugify(value: object) -> str:
    """Latin-only slug; Persian titles fall back to a generated one."""
    text_value = unicodedata.normalize("NFKD", str(value or "").lower())
    text_value = re.sub(r"[^a-z0-9]+", "-", text_value)
    text_value = re.sub(r"^-+|-+$", "", text_value)
    return text_value[:180]


async def unique_slug(base: str, exclude_id: int | None = None) -> str:
    root = base or f"solution-{int(time.time() * 1000)}"
    candidate = root
    counter = 2

    while True:
        if exclude_id is None:
            row = await db.fetchrow("SELECT id FROM solution_articles WHERE slug = $1", candidate)
        else:
            row = await db.fetchrow(
                "SELECT id FROM solution_articles WHERE slug = $1 AND id <> $2",
                candidate,
                exclude_id,
            )
        if row is None:
            return candidate
        candidate = f"{root}-{counter}"
        counter += 1


async def _store_cover(body: dict, files: dict, admin: AdminContext) -> None:
    upload = await extract_file(
        files,
        "image",
        max_mb=config.MAX_SOLUTION_IMAGE_MB,
        size_message=config.SIZE_LIMIT_MESSAGE,
    )
    if upload is None:
        return
    stored = await storage.upload_file(
        buffer=upload.buffer,
        originalname=upload.originalname,
        mimetype=upload.mimetype,
        folder="solutions",
        token=admin.token,
    )
    body["image_url"] = storage.stored_value(stored)


@router.get("/admin/all")
async def admin_get_all(_admin: AdminContext = Depends(require_admin)):
    try:
        rows = await db.fetch(
            f"SELECT {SELECT_COLUMNS} {ADMIN_JOINS} ORDER BY a.created_at DESC, a.id DESC"
        )
        return success(data=[dict(row) for row in rows])
    except Exception:  # noqa: BLE001
        logger.exception("Admin get solution articles error")
        return failure("Failed to fetch solution articles", 500)


@router.get("/admin/{article_id}")
async def admin_get_by_id(
    article_id: int,
    _admin: AdminContext = Depends(require_admin),
):
    try:
        row = await db.fetchrow(
            f"SELECT {SELECT_COLUMNS} {ADMIN_JOINS} WHERE a.id = $1", article_id
        )
        if row is None:
            return failure("Solution article not found", 404)
        return success(data=row)
    except Exception:  # noqa: BLE001
        logger.exception("Admin get solution article error")
        return failure("Failed to fetch solution article", 500)


@router.get("")
async def get_active(request: Request):
    try:
        query = request.query_params
        page, limit, offset = page_limit(query.get("page"), query.get("limit"), 9, 50)

        total = int(
            await db.fetchval(
                "SELECT COUNT(*) FROM solution_articles a WHERE a.is_active = true"
            )
            or 0
        )
        rows = await db.fetch(
            f"SELECT {SELECT_COLUMNS} {PUBLIC_JOINS} "
            f"WHERE a.is_active = true "
            f"ORDER BY a.created_at DESC, a.id DESC LIMIT $1 OFFSET $2",
            limit,
            offset,
        )

        return success(
            data=[dict(row) for row in rows],
            pagination=pagination(page, limit, total),
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning("Get solution articles warning (%s), falling back", exc)
        return success(
            data=[],
            pagination=pagination(1, 9, 0),
        )


@router.get("/{slug}")
async def get_by_slug(slug: str):
    try:
        row = await db.fetchrow(
            f"SELECT {SELECT_COLUMNS} {PUBLIC_JOINS} "
            f"WHERE a.slug = $1 AND a.is_active = true",
            slug,
        )
        if row is None:
            return failure("Solution article not found", 404)
        return success(data=row)
    except Exception:  # noqa: BLE001
        logger.exception("Get solution article error")
        return failure("Failed to fetch solution article", 500)


@router.post("/admin")
async def create_article(
    request: Request,
    admin: AdminContext = Depends(require_admin),
):
    try:
        body, files = await read_body(request)
        await _store_cover(body, files, admin)

        title = body.get("title")
        if not title or not str(title).strip():
            return failure("title is required", 400)

        final_slug = await unique_slug(slugify(body.get("slug")) or slugify(title))

        tags_val = body.get("tags")
        if isinstance(tags_val, (dict, list)):
            import json
            tags_val = json.dumps(tags_val, ensure_ascii=False)

        rel_prod_id = int_or_null(body.get("related_product_id") or body.get("product_id"))
        row = await db.fetchrow(
            "INSERT INTO solution_articles (\n"
            "  title, slug, summary, content, image_url, source_title, source_url,\n"
            "  related_product_id, product_id, author_id, is_active, category, read_time, topic, tags\n"
            ")\n"
            "VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15)\n"
            "RETURNING *",
            str(title).strip(),
            final_slug,
            body.get("summary") or None,
            body.get("content") or None,
            storage.to_object_key(body.get("image_url")),
            body.get("source_title") or None,
            body.get("source_url") or None,
            rel_prod_id,
            rel_prod_id,
            int_or_null(body.get("author_id")),
            bool_default_true(body.get("is_active")),
            body.get("category") or None,
            body.get("read_time") or None,
            body.get("topic") or None,
            tags_val or None,
        )
        return success(data=row, status_code=201)
    except ApiError as error:
        return failure(error.message, error.status_code)
    except Exception as error:  # noqa: BLE001
        logger.exception("Create solution article error")
        return failure(str(error) or "Create failed", 500)


@router.put("/admin/{article_id}")
async def update_article(
    article_id: int,
    request: Request,
    admin: AdminContext = Depends(require_admin),
):
    try:
        body, files = await read_body(request)
        await _store_cover(body, files, admin)

        existing = await db.fetchrow(
            "SELECT id, image_url, slug FROM solution_articles WHERE id = $1", article_id
        )
        if existing is None:
            return failure("Solution article not found", 404)

        title = body.get("title")
        slug = body.get("slug")
        final_slug = existing["slug"]
        if slug is not None and str(slug).strip():
            candidate = slugify(slug) or slugify(title) or final_slug
            if candidate != final_slug:
                final_slug = await unique_slug(candidate, article_id)

        active = body.get("is_active")
        tags_val = body.get("tags")
        if isinstance(tags_val, (dict, list)):
            import json
            tags_val = json.dumps(tags_val, ensure_ascii=False)

        rel_prod_id = int_or_null(body.get("related_product_id") or body.get("product_id"))

        row = await db.fetchrow(
            "UPDATE solution_articles SET\n"
            "  title = $1,\n"
            "  slug = $2,\n"
            "  summary = $3,\n"
            "  content = $4,\n"
            "  image_url = COALESCE($5, image_url),\n"
            "  source_title = $6,\n"
            "  source_url = $7,\n"
            "  related_product_id = $8,\n"
            "  product_id = $8,\n"
            "  author_id = $9,\n"
            "  is_active = COALESCE($10, is_active),\n"
            "  category = COALESCE($11, category),\n"
            "  read_time = COALESCE($12, read_time),\n"
            "  topic = COALESCE($13, topic),\n"
            "  tags = COALESCE($14, tags),\n"
            "  updated_at = CURRENT_TIMESTAMP\n"
            "WHERE id = $15\n"
            "RETURNING *",
            (str(title).strip() if title is not None and str(title).strip() else None),
            final_slug,
            body.get("summary") or None,
            body.get("content") or None,
            storage.to_object_key(body.get("image_url")),
            body.get("source_title") or None,
            body.get("source_url") or None,
            rel_prod_id,
            int_or_null(body.get("author_id")),
            None if active is None else js_bool(active),
            body.get("category") if "category" in body else None,
            body.get("read_time") if "read_time" in body else None,
            body.get("topic") if "topic" in body else None,
            tags_val if "tags" in body else None,
            article_id,
        )
        return success(data=row)
    except ApiError as error:
        return failure(error.message, error.status_code)
    except Exception as error:  # noqa: BLE001
        logger.exception("Update solution article error")
        return failure(str(error) or "Update failed", 500)


@router.delete("/admin/{article_id}/image")
async def delete_article_image(
    article_id: int,
    admin: AdminContext = Depends(require_admin),
):
    try:
        existing = await db.fetchrow(
            "SELECT id, image_url FROM solution_articles WHERE id = $1", article_id
        )
        if existing is None:
            return failure("Solution article not found", 404)

        current_image = existing["image_url"]
        if not current_image:
            return failure("Solution article has no image", 404)

        await db.execute(
            "UPDATE solution_articles SET image_url = NULL, updated_at = CURRENT_TIMESTAMP "
            "WHERE id = $1",
            article_id,
        )
        await storage.remove_stored_file(current_image, admin.token, admin.app_id)

        return success(message="Solution article image deleted")
    except Exception:  # noqa: BLE001
        logger.exception("Delete solution article image error")
        return failure("Failed to delete solution article image", 500)


@router.delete("/admin/{article_id}")
async def remove_article(
    article_id: int,
    admin: AdminContext = Depends(require_admin),
):
    try:
        existing = await db.fetchrow(
            "SELECT image_url FROM solution_articles WHERE id = $1", article_id
        )
        if existing is None:
            return failure("Solution article not found", 404)

        image_url = existing["image_url"]
        if image_url:
            await storage.remove_stored_file(image_url, admin.token, admin.app_id)

        await db.execute("DELETE FROM solution_articles WHERE id = $1", article_id)
        return success(message="Solution article deleted")
    except Exception:  # noqa: BLE001
        logger.exception("Delete solution article error")
        return failure("Failed to delete solution article", 500)
