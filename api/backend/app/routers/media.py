"""Media library router — /api/media.

Provides endpoints to list, upload, search, and delete media files (images,
videos, documents, catalogs) with automatic filesystem synchronization.
"""

from __future__ import annotations

import io
import logging
import mimetypes
import os
from pathlib import Path
import time
from typing import Any, Optional
from urllib.parse import unquote, urlparse

import httpx

from fastapi import APIRouter, Depends, Query, Request

from .. import config, db, storage
from ..errors import ApiError
from ..helpers import extract_file, read_body
from ..responses import failure, success
from ..security import AdminContext, require_admin

logger = logging.getLogger("cloudland.media")

router = APIRouter(prefix="/api/media", tags=["Media"])

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".bmp", ".ico", ".avif"}
VIDEO_EXTS = {".mp4", ".webm", ".ogg", ".mov", ".avi", ".mkv", ".m4v", ".3gp"}
DOC_EXTS = {".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".txt", ".csv", ".zip", ".rar"}


def detect_file_type(mimetype: Optional[str], filename: str) -> str:
    ext = Path(filename).suffix.lower()
    if mimetype:
        mtype = mimetype.lower()
        if mtype.startswith("image/"):
            return "image"
        if mtype.startswith("video/"):
            return "video"
        if mtype in ("application/pdf", "application/msword", "text/csv") or "officedocument" in mtype:
            return "document"

    if ext in IMAGE_EXTS:
        return "image"
    if ext in VIDEO_EXTS:
        return "video"
    if ext in DOC_EXTS:
        return "document"
    return "other"


def format_file_size(size_bytes: int) -> str:
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"


async def register_media(
    file_url: str,
    folder: str = "general",
    original_name: Optional[str] = None,
    file_type: Optional[str] = None,
    size_bytes: int = 0,
    mimetype: Optional[str] = None,
) -> None:
    """Register a single media file into media_files library."""
    if not file_url or not str(file_url).strip():
        return
    f_url = str(file_url).strip()
    fname = Path(f_url).name or f"media-{int(time.time())}"
    orig = original_name or fname
    if not mimetype:
        mimetype, _ = mimetypes.guess_type(fname)
    if not file_type or file_type == "other":
        file_type = detect_file_type(mimetype, fname)

    if size_bytes <= 0:
        local_p = _resolve_media_path(f_url)
        if local_p and local_p.is_file():
            try:
                size_bytes = local_p.stat().st_size
            except Exception:
                size_bytes = 0
        if size_bytes <= 0:
            if file_type == "video":
                size_bytes = 2_500_000
            elif file_type == "image":
                size_bytes = 150_000
            elif file_type == "document":
                size_bytes = 350_000

    try:
        await db.execute(
            """
            INSERT INTO media_files (
                filename, original_name, file_url, file_type, mimetype, file_size, folder
            ) VALUES ($1, $2, $3, $4, $5, $6, $7)
            ON CONFLICT (file_url) DO UPDATE SET
                folder = COALESCE(NULLIF(media_files.folder, 'general'), EXCLUDED.folder),
                file_size = CASE WHEN media_files.file_size = 0 THEN EXCLUDED.file_size ELSE media_files.file_size END
            """,
            fname,
            orig,
            f_url,
            file_type,
            mimetype or "application/octet-stream",
            size_bytes,
            folder,
        )
    except Exception as exc:
        logger.debug("[register_media] Insert media file warning for %s: %s", f_url, exc)


async def sync_all_media() -> int:
    """Comprehensive media scanner that indexes:
    1. Disk files in config.UPLOADS_DIR
    2. Product gallery images (product_images)
    3. Product videos and video thumbnails (product_videos)
    4. Product profile images (products)
    5. Product catalogs (product_catalogs)
    6. Solution/Article images (solution_articles)
    7. Team member images (team_members)
    """
    try:
        existing_rows = await db.fetch("SELECT file_url FROM media_files")
        existing_urls = {r["file_url"] for r in existing_rows}
    except Exception as exc:
        logger.warning("[sync_all_media] Failed to fetch existing rows: %s", exc)
        return 0

    to_insert: list[tuple[Any, ...]] = []

    def add_item(file_url: Any, folder: str, original_name: Optional[str] = None, file_type: Optional[str] = None, size_bytes: int = 0, mimetype: Optional[str] = None) -> None:
        if not file_url or not str(file_url).strip():
            return
        f_url = str(file_url).strip()
        if f_url in existing_urls:
            return
        fname = Path(f_url).name or f"file-{len(to_insert)}"
        orig = original_name or fname
        if not mimetype:
            mimetype, _ = mimetypes.guess_type(fname)
        f_type = file_type or detect_file_type(mimetype, fname)
        if size_bytes <= 0:
            local_p = _resolve_media_path(f_url)
            if local_p and local_p.is_file():
                try:
                    size_bytes = local_p.stat().st_size
                except Exception:
                    size_bytes = 0
            if size_bytes <= 0:
                if f_type == "video":
                    size_bytes = 2_500_000
                elif f_type == "image":
                    size_bytes = 150_000
                elif f_type == "document":
                    size_bytes = 350_000
                else:
                    size_bytes = 50_000

        to_insert.append((
            fname,
            orig,
            f_url,
            f_type,
            mimetype or "application/octet-stream",
            size_bytes,
            folder,
        ))
        existing_urls.add(f_url)

    # 1. Scan filesystem uploads directory
    uploads_dir = Path(config.UPLOADS_DIR)
    if uploads_dir.exists():
        for path in uploads_dir.rglob("*"):
            if not path.is_file() or path.name.startswith(".") or path.name.endswith(".tmp"):
                continue
            try:
                rel = path.relative_to(uploads_dir).as_posix()
                file_url = f"/uploads/{rel}"
                folder = rel.split("/")[0] if "/" in rel else "general"
                mimetype, _ = mimetypes.guess_type(path.name)
                f_type = detect_file_type(mimetype, path.name)
                size = path.stat().st_size
                add_item(file_url, folder, path.name, f_type, size, mimetype)
            except Exception as err:
                logger.debug("[sync_all_media] Error processing disk file %s: %s", path, err)

    # 2. Scan product gallery images
    try:
        p_imgs = await db.fetch("SELECT image_url FROM product_images WHERE image_url IS NOT NULL AND TRIM(image_url) != ''")
        for r in p_imgs:
            add_item(r["image_url"], "products", file_type="image")
    except Exception as exc:
        logger.debug("[sync_all_media] Error querying product_images: %s", exc)

    # 3. Scan product videos and thumbnails
    try:
        p_vids = await db.fetch("SELECT video_url, thumbnail_url, title FROM product_videos WHERE (video_url IS NOT NULL AND TRIM(video_url) != '') OR (thumbnail_url IS NOT NULL AND TRIM(thumbnail_url) != '')")
        for r in p_vids:
            if r.get("video_url"):
                add_item(r["video_url"], "products", original_name=r.get("title"), file_type="video")
            if r.get("thumbnail_url"):
                add_item(r["thumbnail_url"], "products", original_name=f"thumb-{r.get('title') or 'video'}", file_type="image")
    except Exception as exc:
        logger.debug("[sync_all_media] Error querying product_videos: %s", exc)

    # 4. Scan main product profile images
    try:
        p_rows = await db.fetch("SELECT image_url, title FROM products WHERE image_url IS NOT NULL AND TRIM(image_url) != ''")
        for r in p_rows:
            add_item(r["image_url"], "products", original_name=r.get("title"), file_type="image")
    except Exception as exc:
        logger.debug("[sync_all_media] Error querying products: %s", exc)

    # 5. Scan product catalogs
    try:
        p_cats = await db.fetch("SELECT file_url, title FROM product_catalogs WHERE file_url IS NOT NULL AND TRIM(file_url) != ''")
        for r in p_cats:
            add_item(r["file_url"], "catalogs", original_name=r.get("title"), file_type="document")
    except Exception as exc:
        logger.debug("[sync_all_media] Error querying product_catalogs: %s", exc)

    # 6. Scan solution / article images
    try:
        sol_rows = await db.fetch("SELECT image_url, title FROM solution_articles WHERE image_url IS NOT NULL AND TRIM(image_url) != ''")
        for r in sol_rows:
            add_item(r["image_url"], "articles", original_name=r.get("title"), file_type="image")
    except Exception as exc:
        logger.debug("[sync_all_media] Error querying solution_articles: %s", exc)

    # 7. Scan team member avatars
    try:
        tm_rows = await db.fetch("SELECT image_url, full_name FROM team_members WHERE image_url IS NOT NULL AND TRIM(image_url) != ''")
        for r in tm_rows:
            add_item(r["image_url"], "team", original_name=r.get("full_name"), file_type="image")
    except Exception as exc:
        logger.debug("[sync_all_media] Error querying team_members: %s", exc)

    # Bulk insert all newly discovered items
    if to_insert:
        try:
            await db.executemany(
                """
                INSERT INTO media_files (
                    filename, original_name, file_url, file_type, mimetype, file_size, folder
                ) VALUES ($1, $2, $3, $4, $5, $6, $7)
                ON CONFLICT (file_url) DO NOTHING
                """,
                to_insert,
            )
            logger.info("[sync_all_media] Successfully indexed %d media files into library", len(to_insert))
        except Exception as exc:
            logger.warning("[sync_all_media] Bulk insert error: %s", exc)

    return len(to_insert)


# Alias for backwards compatibility
sync_uploads_directory = sync_all_media


@router.post("/sync")
async def trigger_media_sync(admin: AdminContext = Depends(require_admin)):
    """Trigger a comprehensive scan of disk, products, videos, gallery, and catalogs."""
    synced_count = await sync_all_media()
    return success(
        message=f"همگام‌سازی با موفقیت انجام شد ({synced_count} فایل جدید ثبت شد)",
        data={"synced_count": synced_count},
    )


@router.get("")
async def list_media(
    page: int = Query(1, ge=1),
    limit: int = Query(24, ge=1, le=100),
    type: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    folder: Optional[str] = Query(None),
    admin: AdminContext = Depends(require_admin),
):
    """List all uploaded media files with pagination and filtering."""
    # Run sync to catch any newly dropped or legacy files, product images, videos, etc.
    await sync_all_media()

    conditions = []
    args: list[Any] = []

    if type and type != "all":
        args.append(type.lower())
        conditions.append(f"file_type = ${len(args)}")

    if folder and folder != "all":
        args.append(f"%{folder}%")
        conditions.append(f"(folder = ${len(args)} OR folder ILIKE ${len(args)})")

    if search and search.strip():
        term = f"%{search.strip()}%"
        args.append(term)
        conditions.append(f"(filename ILIKE ${len(args)} OR original_name ILIKE ${len(args)})")

    where_sql = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    # Stats
    try:
        stats_row = await db.fetchrow(
            """
            SELECT
                COUNT(*) AS total_files,
                COUNT(*) FILTER (WHERE file_type = 'image') AS total_images,
                COUNT(*) FILTER (WHERE file_type = 'video') AS total_videos,
                COUNT(*) FILTER (WHERE file_type = 'document') AS total_documents,
                COALESCE(SUM(file_size), 0) AS total_size_bytes
            FROM media_files
            """
        )
    except Exception:
        # Fallback for SQLite which doesn't support FILTER (WHERE ...)
        stats_row = await db.fetchrow(
            """
            SELECT
                COUNT(*) AS total_files,
                SUM(CASE WHEN file_type = 'image' THEN 1 ELSE 0 END) AS total_images,
                SUM(CASE WHEN file_type = 'video' THEN 1 ELSE 0 END) AS total_videos,
                SUM(CASE WHEN file_type = 'document' THEN 1 ELSE 0 END) AS total_documents,
                COALESCE(SUM(file_size), 0) AS total_size_bytes
            FROM media_files
            """
        )

    total_files = int(stats_row["total_files"] or 0)
    total_images = int(stats_row["total_images"] or 0)
    total_videos = int(stats_row["total_videos"] or 0)
    total_documents = int(stats_row["total_documents"] or 0)
    total_size_bytes = int(stats_row["total_size_bytes"] or 0)

    # Count for current query
    count_sql = f"SELECT COUNT(*) FROM media_files {where_sql}"
    total = int(await db.fetchval(count_sql, *args) or 0)

    # Paginated query
    offset = (page - 1) * limit
    args_paged = list(args)
    args_paged.append(limit)
    limit_param = f"${len(args_paged)}"
    args_paged.append(offset)
    offset_param = f"${len(args_paged)}"

    items_sql = f"""
        SELECT id, filename, original_name, file_url, file_type, mimetype, file_size, folder, created_at
        FROM media_files
        {where_sql}
        ORDER BY id DESC
        LIMIT {limit_param} OFFSET {offset_param}
    """
    rows = await db.fetch(items_sql, *args_paged)

    data = [
        {
            "id": r["id"],
            "filename": r["filename"],
            "original_name": r["original_name"] or r["filename"],
            "url": storage.public_url(r["file_url"]),
            "raw_url": r["file_url"],
            "file_type": r["file_type"],
            "mimetype": r["mimetype"],
            "file_size": r["file_size"],
            "file_size_formatted": format_file_size(r["file_size"] or 0),
            "folder": r["folder"],
            "created_at": r["created_at"],
        }
        for r in rows
    ]

    total_pages = (total + limit - 1) // limit if total > 0 else 0

    return success(
        data=data,
        pagination={
            "page": page,
            "limit": limit,
            "total": total,
            "totalPages": total_pages,
        },
        stats={
            "total_files": total_files,
            "total_images": total_images,
            "total_videos": total_videos,
            "total_documents": total_documents,
            "total_size_bytes": total_size_bytes,
            "total_size_formatted": format_file_size(total_size_bytes),
        },
    )


@router.post("/upload")
async def upload_media_file(
    request: Request,
    admin: AdminContext = Depends(require_admin),
):
    """Upload one or more files directly into the media library."""
    fields, files = await read_body(request)
    folder = fields.get("folder", "general")

    upload = await extract_file(files, "file")
    if upload is None:
        # Check if sent under 'image' or first available file key
        for key in ("image", "media", "attachment"):
            upload = await extract_file(files, key)
            if upload is not None:
                break

    if upload is None and files:
        first_key = next(iter(files.keys()))
        upload = await extract_file(files, first_key)

    if upload is None:
        raise ApiError(400, "فایلی برای آپلود ارسال نشده است")

    stored = await storage.upload_file(
        buffer=upload.buffer,
        originalname=upload.originalname,
        mimetype=upload.mimetype,
        folder=folder,
        token=admin.token,
    )

    file_url = storage.stored_value(stored)
    file_type = detect_file_type(upload.mimetype, upload.originalname)
    file_size = len(upload.buffer)
    filename = Path(file_url).name if file_url else upload.originalname

    row = await db.fetchrow(
        """
        INSERT INTO media_files (
            filename, original_name, file_url, file_type, mimetype, file_size, folder
        ) VALUES ($1, $2, $3, $4, $5, $6, $7)
        RETURNING id, filename, original_name, file_url, file_type, mimetype, file_size, folder, created_at
        """,
        filename,
        upload.originalname,
        file_url,
        file_type,
        upload.mimetype,
        file_size,
        folder,
    )

    item = {
        "id": row["id"],
        "filename": row["filename"],
        "original_name": row["original_name"],
        "url": storage.public_url(row["file_url"]),
        "raw_url": row["file_url"],
        "file_type": row["file_type"],
        "mimetype": row["mimetype"],
        "file_size": row["file_size"],
        "file_size_formatted": format_file_size(row["file_size"]),
        "folder": row["folder"],
        "created_at": row["created_at"],
    }

    return success(message="فایل با موفقیت آپلود شد", data=item)


@router.delete("/{media_id}")
async def delete_media_file(
    media_id: int,
    admin: AdminContext = Depends(require_admin),
):
    """Delete a media file from disk and database."""
    row = await db.fetchrow("SELECT id, file_url FROM media_files WHERE id = $1", media_id)
    if not row:
        raise ApiError(404, "فایل مورد نظر یافت نشد")

    local_path = _resolve_media_path(row["file_url"])
    if local_path and local_path.is_file():
        try:
            local_path.unlink()
            logger.info("[media delete] Deleted file from disk: %s", local_path)
        except Exception as exc:
            logger.warning("[media delete] Could not delete disk file: %s", exc)

    await db.execute("DELETE FROM media_files WHERE id = $1", media_id)
    return success(message="فایل با موفقیت حذف شد")


@router.post("/batch-delete")
async def batch_delete_media_files(
    request: Request,
    admin: AdminContext = Depends(require_admin),
):
    """Delete multiple media files from disk and database."""
    body, _ = await read_body(request)
    raw_ids = body.get("ids") or body.get("media_ids") or []
    if isinstance(raw_ids, (int, str)):
        raw_ids = [raw_ids]

    clean_ids = []
    for x in raw_ids:
        try:
            clean_ids.append(int(x))
        except (ValueError, TypeError):
            continue

    if not clean_ids:
        raise ApiError(400, "هیچ فایلی برای حذف انتخاب نشده است.")

    deleted_count = 0
    for media_id in clean_ids:
        row = await db.fetchrow("SELECT id, file_url FROM media_files WHERE id = $1", media_id)
        if not row:
            continue
        local_path = _resolve_media_path(row["file_url"])
        if local_path and local_path.is_file():
            try:
                local_path.unlink()
            except Exception as exc:
                logger.warning("[batch-delete] Could not delete disk file: %s", exc)
        await db.execute("DELETE FROM media_files WHERE id = $1", media_id)
        deleted_count += 1

    return success(
        message=f"{deleted_count} فایل با موفقیت حذف شدند.",
        data={"deleted_count": deleted_count},
    )


def _resolve_media_path(file_url: str) -> Optional[Path]:
    """Resolve a file_url to an existing local filesystem Path with support for URL decoding and multiple locations."""
    if not file_url:
        return None

    uploads_dir = Path(config.UPLOADS_DIR)
    if not uploads_dir.exists():
        uploads_dir.mkdir(parents=True, exist_ok=True)

    cleaned_url = str(file_url).split("?")[0].split("#")[0].strip()
    if "://" in cleaned_url:
        cleaned_url = urlparse(cleaned_url).path

    unquoted_url = unquote(cleaned_url)

    candidates = [
        cleaned_url,
        unquoted_url,
    ]
    if cleaned_url.startswith("/uploads/"):
        candidates.append(cleaned_url[len("/uploads/"):].lstrip("/"))
    if unquoted_url.startswith("/uploads/"):
        candidates.append(unquoted_url[len("/uploads/"):].lstrip("/"))

    public_dir = config.BASE_DIR.parent.parent / "style" / "frontend" / "public"

    for cand in candidates:
        cand_rel = cand.lstrip("/")
        # Check in uploads_dir
        p = uploads_dir / cand_rel
        if p.exists() and p.is_file():
            return p
        # Check directly if cand is an existing absolute path
        try:
            ap = Path(cand)
            if ap.is_file():
                return ap
        except Exception:
            pass
        # Check in public_dir
        if public_dir.exists():
            p = public_dir / cand_rel
            if p.exists() and p.is_file():
                return p
            p = public_dir / "assets" / cand_rel
            if p.exists() and p.is_file():
                return p
            if cand_rel.startswith("assets/"):
                p = public_dir / cand_rel
                if p.exists() and p.is_file():
                    return p

    return None


def _url_for_local_path(p: Path) -> str:
    """Determine the web-accessible URL for a local file path."""
    uploads_dir = Path(config.UPLOADS_DIR)
    public_dir = config.BASE_DIR.parent.parent / "style" / "frontend" / "public"
    try:
        rel_up = p.relative_to(uploads_dir).as_posix()
        return f"/uploads/{rel_up}"
    except ValueError:
        pass
    try:
        rel_pub = p.relative_to(public_dir).as_posix()
        return f"/{rel_pub}"
    except ValueError:
        pass
    return f"/uploads/{p.name}"


async def _cascade_update_media_url(old_url: str, new_url: str) -> None:
    """Cascade update an old media URL to its new URL across all database tables."""
    if not old_url or not new_url or old_url == new_url:
        return

    # Build comprehensive pairs of (old_variant, new_variant)
    variants: set[tuple[str, str]] = {(old_url, new_url)}

    # Leading slash variants
    if old_url.startswith("/"):
        variants.add((old_url.lstrip("/"), new_url.lstrip("/")))
    else:
        variants.add((f"/{old_url}", f"/{new_url}"))

    # Uploads vs relative object key
    if "/uploads/" in old_url:
        k_old = old_url.split("/uploads/", 1)[1]
        k_new = new_url.split("/uploads/", 1)[1] if "/uploads/" in new_url else new_url
        variants.add((k_old, k_new))
        variants.add((f"/{k_old}", f"/{k_new}"))
        variants.add((f"uploads/{k_old}", f"uploads/{k_new}"))

    # Public S3 / base URLs
    pub_old = storage.public_url(old_url)
    pub_new = storage.public_url(new_url)
    if pub_old and pub_new and pub_old != old_url:
        variants.add((pub_old, pub_new))

    tables_updates = [
        ("products", "image_url"),
        ("product_images", "image_url"),
        ("product_videos", "thumbnail_url"),
        ("solution_articles", "image_url"),
        ("team_members", "image_url"),
        ("home_works", "image_url"),
        ("home_customers", "logo_url"),
        ("home_reviews", "avatar_url"),
        ("home_features", "icon_src"),
    ]

    for old_v, new_v in variants:
        if not old_v or not new_v or old_v == new_v:
            continue
        for table, col in tables_updates:
            try:
                await db.execute(f"UPDATE {table} SET {col} = $1 WHERE {col} = $2", new_v, old_v)
            except Exception as exc:
                logger.debug("[cascade_update] %s.%s warning: %s", table, col, exc)

        try:
            await db.execute(
                """
                UPDATE site_settings
                SET logo_url = CASE WHEN logo_url = $1 THEN $2 ELSE logo_url END,
                    favicon_url = CASE WHEN favicon_url = $1 THEN $2 ELSE favicon_url END
                WHERE logo_url = $1 OR favicon_url = $1
                """,
                old_v, new_v,
            )
        except Exception:
            pass

        try:
            await db.execute(
                """
                UPDATE home_settings
                SET hero_image_url = CASE WHEN hero_image_url = $1 THEN $2 ELSE hero_image_url END,
                    cta_image_url = CASE WHEN cta_image_url = $1 THEN $2 ELSE cta_image_url END
                WHERE hero_image_url = $1 OR cta_image_url = $1
                """,
                old_v, new_v,
            )
        except Exception:
            pass

        # Update rich HTML text content in solution_articles and products
        for t, col in [("solution_articles", "content"), ("products", "description")]:
            try:
                await db.execute(
                    f"UPDATE {t} SET {col} = REPLACE({col}, $1, $2) WHERE {col} LIKE $3",
                    old_v, new_v, f"%{old_v}%",
                )
            except Exception:
                pass


@router.post("/convert-webp")
async def convert_media_to_webp(
    request: Request,
    admin: AdminContext = Depends(require_admin),
):
    """Convert one or multiple selected image files to modern WebP format."""
    from PIL import Image

    body, _ = await read_body(request)
    raw_ids = body.get("ids") or body.get("media_ids") or []
    if isinstance(raw_ids, (int, str)):
        raw_ids = [raw_ids]
    if not raw_ids and body.get("id"):
        raw_ids = [body.get("id")]

    clean_ids = []
    for x in raw_ids:
        try:
            clean_ids.append(int(x))
        except (ValueError, TypeError):
            continue

    if not clean_ids:
        raise ApiError(400, "هیچ تصویری برای تبدیل به WebP انتخاب نشده است.")

    converted_items = []
    total_saved_bytes = 0
    already_webp_count = 0
    errors: list[str] = []

    for media_id in clean_ids:
        row = await db.fetchrow(
            "SELECT id, filename, original_name, file_url, file_type, mimetype, file_size, folder FROM media_files WHERE id = $1",
            media_id,
        )
        if not row:
            errors.append(f"تصویر با شناسه {media_id} در پایگاه داده یافت نشد")
            continue
        if row["file_type"] != "image":
            errors.append(f"فایل «{row['filename']}» تصویر نیست")
            continue

        filename_lower = str(row["filename"]).lower()
        file_url_lower = str(row["file_url"]).lower()

        # If already WebP, count and skip
        if filename_lower.endswith(".webp") or file_url_lower.endswith(".webp"):
            already_webp_count += 1
            continue

        # Skip SVGs
        if filename_lower.endswith(".svg") or file_url_lower.endswith(".svg"):
            errors.append(f"فرمت SVG برای «{row['filename']}» برداری بوده و نیازی به تبدیل ندارد")
            continue

        local_path = _resolve_media_path(row["file_url"])
        old_file_url = row["file_url"]

        try:
            converted_im = None
            orig_size = 0
            is_local = False

            if local_path and local_path.is_file():
                is_local = True
                orig_size = local_path.stat().st_size
                with Image.open(local_path) as im:
                    im.load()
                    if im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info):
                        converted_im = im.convert("RGBA")
                    else:
                        converted_im = im.convert("RGB")
            else:
                # Try fetching remote / MinIO image data
                pub_url = storage.public_url(old_file_url)
                if pub_url and (pub_url.startswith("http://") or pub_url.startswith("https://")):
                    async with httpx.AsyncClient(timeout=20.0) as client:
                        resp = await client.get(pub_url)
                        if resp.status_code == 200:
                            orig_size = len(resp.content)
                            with Image.open(io.BytesIO(resp.content)) as im:
                                im.load()
                                if im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info):
                                    converted_im = im.convert("RGBA")
                                else:
                                    converted_im = im.convert("RGB")

            if converted_im is None:
                errors.append(f"فایل فیزیکی یا نشانی «{row['filename']}» در سرور یافت نشد")
                continue

            stem = Path(row["filename"]).stem
            new_file_url = None
            new_size = 0

            if is_local and local_path:
                target_dir = local_path.parent
                out_path = target_dir / f"{stem}.webp"

                # Save as high quality WebP
                converted_im.save(out_path, format="WEBP", quality=82, method=4)
                new_size = out_path.stat().st_size

                # Remove old file if it wasn't already a .webp file (SAFE: file handle closed outside with block)
                if local_path.resolve() != out_path.resolve() and local_path.exists():
                    try:
                        local_path.unlink(missing_ok=True)
                    except Exception as rm_err:
                        logger.warning("[convert-webp] Could not remove old file %s: %s", local_path, rm_err)

                new_file_url = _url_for_local_path(out_path)
            else:
                out_io = io.BytesIO()
                converted_im.save(out_io, format="WEBP", quality=82, method=4)
                webp_bytes = out_io.getvalue()
                new_size = len(webp_bytes)

                stored = await storage.upload_file(
                    buffer=webp_bytes,
                    originalname=f"{stem}.webp",
                    mimetype="image/webp",
                    folder=row["folder"] or "general",
                    token=admin.token,
                )
                new_file_url = storage.stored_value(stored)

            if not new_file_url:
                errors.append(f"خطا در ایجاد نشانی فایل WebP برای «{row['filename']}»")
                continue

            saved = orig_size - new_size if orig_size > new_size else 0
            total_saved_bytes += saved

            orig_stem = Path(row["original_name"] or row["filename"]).stem
            new_orig_name = f"{orig_stem}.webp"
            out_filename = Path(new_file_url).name

            # Prevent UNIQUE constraint clash on file_url
            try:
                await db.execute(
                    "DELETE FROM media_files WHERE file_url = $1 AND id != $2",
                    new_file_url,
                    row["id"],
                )
            except Exception:
                pass

            # Update the media row in place
            await db.execute(
                """
                UPDATE media_files
                SET filename = $1, original_name = $2, file_url = $3, mimetype = 'image/webp', file_size = $4
                WHERE id = $5
                """,
                out_filename,
                new_orig_name,
                new_file_url,
                new_size,
                row["id"],
            )

            # Cascade update to all other tables (products, gallery, articles, settings, etc.)
            await _cascade_update_media_url(old_file_url, new_file_url)

            converted_items.append({
                "id": row["id"],
                "filename": out_filename,
                "url": storage.public_url(new_file_url),
                "file_size": new_size,
                "file_size_formatted": format_file_size(new_size),
                "saved_bytes": saved,
                "saved_formatted": format_file_size(saved),
            })
        except Exception as exc:
            logger.warning("[convert-webp] Error converting file for media_id=%s: %s", media_id, exc)
            errors.append(f"خطا در تبدیل «{row['filename']}»: {str(exc)}")

    if not converted_items:
        if already_webp_count > 0 and not errors:
            return success(
                message="تصویر (یا تصاویر) انتخاب‌شده در حال حاضر با فرمت بهینه WebP هستند.",
                data={
                    "converted_count": 0,
                    "already_webp": True,
                    "total_saved_bytes": 0,
                    "total_saved_formatted": "0 B",
                    "items": [],
                },
            )
        err_msg = "; ".join(errors) if errors else "هیچ تصویری برای تبدیل واجد شرایط نبود یا فایل روی سرور یافت نشد."
        raise ApiError(400, f"عملیات تبدیل به WebP ناموفق بود: {err_msg}")

    return success(
        message=f"{len(converted_items)} تصویر با موفقیت به فرمت سبک WebP تبدیل و در سامانه جایگزین شدند.",
        data={
            "converted_count": len(converted_items),
            "total_saved_bytes": total_saved_bytes,
            "total_saved_formatted": format_file_size(total_saved_bytes),
            "items": converted_items,
            "errors": errors,
        },
    )


@router.post("/compress")
async def compress_media_images(
    request: Request,
    admin: AdminContext = Depends(require_admin),
):
    """Compress image file size while preserving high visual fidelity."""
    from PIL import Image

    body, _ = await read_body(request)
    raw_ids = body.get("ids") or body.get("media_ids") or []
    if isinstance(raw_ids, (int, str)):
        raw_ids = [raw_ids]
    if not raw_ids and body.get("id"):
        raw_ids = [body.get("id")]

    clean_ids = []
    for x in raw_ids:
        try:
            clean_ids.append(int(x))
        except (ValueError, TypeError):
            continue

    if not clean_ids:
        raise ApiError(400, "هیچ تصویری برای فشرده‌سازی انتخاب نشده است.")

    compressed_items = []
    total_saved_bytes = 0

    for media_id in clean_ids:
        row = await db.fetchrow(
            "SELECT id, filename, original_name, file_url, file_type, mimetype, file_size, folder FROM media_files WHERE id = $1",
            media_id,
        )
        if not row or row["file_type"] != "image":
            continue

        local_path = _resolve_media_path(row["file_url"])
        if not local_path or not local_path.is_file():
            continue

        ext = local_path.suffix.lower()
        if ext == ".svg":
            continue

        try:
            orig_size = local_path.stat().st_size
            best_size = orig_size
            best_temp = None

            with Image.open(local_path) as im:
                if ext in (".jpg", ".jpeg"):
                    temp_jpg = local_path.with_name(f"{local_path.stem}_opt_tmp{ext}")
                    if im.mode not in ("RGB", "L"):
                        im = im.convert("RGB")
                    im.save(temp_jpg, format="JPEG", quality=80, optimize=True, progressive=True)
                    sz = temp_jpg.stat().st_size
                    if sz < best_size:
                        best_size = sz
                        best_temp = temp_jpg
                    else:
                        temp_jpg.unlink(missing_ok=True)

                elif ext == ".png":
                    # Option A: Standard compress with level 9
                    temp_a = local_path.with_name(f"{local_path.stem}_tmp_a.png")
                    im.save(temp_a, format="PNG", optimize=True, compress_level=9)
                    sz_a = temp_a.stat().st_size
                    if sz_a < best_size:
                        best_size = sz_a
                        best_temp = temp_a

                    # Option B: Fast octree 256 colors for large PNGs
                    if orig_size > 150_000:
                        temp_b = local_path.with_name(f"{local_path.stem}_tmp_b.png")
                        try:
                            if im.mode == "RGBA":
                                q = im.quantize(colors=256, method=Image.FASTOCTREE)
                            else:
                                q = im.convert("RGB").quantize(colors=256)
                            q.save(temp_b, format="PNG", optimize=True, compress_level=9)
                            sz_b = temp_b.stat().st_size
                            if sz_b < best_size:
                                best_size = sz_b
                                if best_temp and best_temp != temp_b:
                                    best_temp.unlink(missing_ok=True)
                                best_temp = temp_b
                            else:
                                temp_b.unlink(missing_ok=True)
                        except Exception as q_err:
                            temp_b.unlink(missing_ok=True)

                    if best_temp != temp_a and temp_a.exists():
                        temp_a.unlink(missing_ok=True)

                elif ext == ".webp":
                    temp_webp = local_path.with_name(f"{local_path.stem}_opt_tmp.webp")
                    if im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info):
                        conv = im.convert("RGBA")
                    else:
                        conv = im.convert("RGB")
                    conv.save(temp_webp, format="WEBP", quality=80, method=4)
                    sz_w = temp_webp.stat().st_size
                    if sz_w < best_size:
                        best_size = sz_w
                        best_temp = temp_webp
                    else:
                        temp_webp.unlink(missing_ok=True)

                else:
                    temp_gen = local_path.with_name(f"{local_path.stem}_opt_tmp{ext}")
                    im.save(temp_gen, optimize=True)
                    sz_g = temp_gen.stat().st_size
                    if sz_g < best_size:
                        best_size = sz_g
                        best_temp = temp_gen
                    else:
                        temp_gen.unlink(missing_ok=True)

            if best_temp and best_temp.exists() and best_size < orig_size:
                best_temp.replace(local_path)
                await db.execute("UPDATE media_files SET file_size = $1 WHERE id = $2", best_size, row["id"])
                saved = orig_size - best_size
                total_saved_bytes += saved
                compressed_items.append({
                    "id": row["id"],
                    "filename": row["filename"],
                    "orig_size": orig_size,
                    "new_size": best_size,
                    "saved_bytes": saved,
                    "saved_formatted": format_file_size(saved),
                })
            else:
                if best_temp and best_temp.exists():
                    best_temp.unlink(missing_ok=True)
                compressed_items.append({
                    "id": row["id"],
                    "filename": row["filename"],
                    "orig_size": orig_size,
                    "new_size": orig_size,
                    "saved_bytes": 0,
                    "saved_formatted": "0 B (قبلاً بهینه بوده)",
                })
        except Exception as exc:
            logger.warning("[compress] Error compressing file %s: %s", local_path, exc)

    return success(
        message=f"{len(compressed_items)} تصویر بررسی و بهینه‌سازی شدند.",
        data={
            "compressed_count": len(compressed_items),
            "total_saved_bytes": total_saved_bytes,
            "total_saved_formatted": format_file_size(total_saved_bytes),
            "items": compressed_items,
        },
    )

