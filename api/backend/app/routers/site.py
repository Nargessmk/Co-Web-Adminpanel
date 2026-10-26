"""Site-wide header + footer content (GET /api/site + admin updates).

One singleton row (``site_settings``) holds the standalone texts and links; the
ordered tables hold the lists both bars render. Lists are replaced as a whole.
"""

from __future__ import annotations

import logging
from typing import Any, Optional

from fastapi import APIRouter, Depends, Request

from .. import config, db, storage
from ..errors import ApiError
from ..helpers import bool_default_true, extract_file, read_body, text
from ..lists import replace_lists
from ..page_settings import settings_select
from ..responses import failure, success
from ..security import AdminContext, require_admin

logger = logging.getLogger("cloudland.site")

router = APIRouter(prefix="/api/site", tags=["Site (header/footer)"])

SETTINGS_TABLE = "site_settings"
SETTINGS_COLUMNS = [
    "logo_url", "site_name",
    "header_login_label", "header_login_link", "header_cta_label", "header_cta_link",
    "header_buttons_order",
    "footer_description", "footer_products_title", "footer_all_products_label",
    "footer_company_title", "footer_contact_title", "footer_contact_address",
    "footer_contact_phone", "footer_contact_email", "footer_cta_label", "footer_cta_link",
    "footer_copyright", "footer_privacy_label", "footer_privacy_url",
    "footer_terms_label", "footer_terms_url",
    "quick_phone", "quick_phone_label", "quick_telegram", "quick_telegram_label",
    "quick_cta_link", "quick_cta_label", "quick_whatsapp", "quick_is_enabled",
]

LISTS: dict[str, dict[str, Any]] = {
    "nav_items": {
        "table": "site_nav_items",
        "columns": ["label", "path"],
        "active_column": True,
    },
    "footer_links": {
        "table": "site_footer_links",
        "columns": ["label", "url"],
        "active_column": True,
    },
    "social_links": {
        "table": "site_social_links",
        "columns": ["label", "url", "icon"],
        "active_column": True,
    },
}


def _normalize_items(rows: Any, spec: dict[str, Any]) -> Optional[list[dict[str, Any]]]:
    """Rows missing a label or a target are dropped instead of breaking the bar."""
    if rows is None or not isinstance(rows, list):
        return None

    items: list[dict[str, Any]] = []
    for row in rows:
        row = row if isinstance(row, dict) else {}
        item: dict[str, Any] = {column: text(row.get(column)) for column in spec["columns"]}
        if item.get("icon") is None:
            item["icon"] = "link"
        if any(
            not item.get(column)
            for column in spec["columns"]
            if column != "icon"
        ):
            continue
        item["is_active"] = bool_default_true(row.get("is_active"))
        items.append(item)
    return items


async def _read_all(query) -> dict[str, Any]:
    settings_rows = await query(
        f"SELECT {settings_select(SETTINGS_COLUMNS)} FROM {SETTINGS_TABLE} WHERE id = 1"
    )
    nav_items = await query(
        "SELECT label, path, is_active FROM site_nav_items ORDER BY sort_order ASC, id ASC"
    )
    footer_links = await query(
        "SELECT label, url, is_active FROM site_footer_links ORDER BY sort_order ASC, id ASC"
    )
    social_links = await query(
        "SELECT label, url, icon, is_active FROM site_social_links ORDER BY sort_order ASC, id ASC"
    )

    return {
        "settings": dict(settings_rows[0]) if settings_rows else None,
        "nav_items": [dict(row) for row in nav_items],
        "footer_links": [dict(row) for row in footer_links],
        "social_links": [dict(row) for row in social_links],
    }


DEFAULT_SITE_DATA = {
    "settings": {
        "site_name": "سرزمین کهکشان هوشمند",
        "header_cta_label": "شروع همکاری",
        "header_cta_link": "#sec-contact",
        "header_buttons_order": "cta",
        "footer_description": "پلتفرم جامع مهندسی نرم‌افزار و معماری ابری",
        "footer_contact_phone": "۰۲۱ - ۸۸۹۰ ۱۲۳۴",
        "footer_contact_email": "contact@smartgalaxy.land",
        "footer_copyright": "© ۱۴۰۵ تمامی حقوق مادی و معنوی متعلق به سرزمین کهکشان هوشمند است.",
        "quick_phone": "02188901234",
        "quick_phone_label": "تماس تلفنی مستقیم",
        "quick_telegram": "https://t.me",
        "quick_telegram_label": "پشتیبانی تلگرام",
        "quick_cta_link": "/contact",
        "quick_cta_label": "درخواست مشاوره فوری",
        "quick_whatsapp": "",
        "quick_is_enabled": "true",
    },
    "nav_items": [
        {"label": "خانه", "path": "/", "is_active": True},
        {"label": "خدمات", "path": "/services", "is_active": True},
        {"label": "پروژه‌ها", "path": "/projects", "is_active": True},
        {"label": "مقالات", "path": "/articles", "is_active": True},
        {"label": "درباره ما", "path": "/about", "is_active": True},
        {"label": "تماس با ما", "path": "/contact", "is_active": True},
    ],
    "footer_links": [],
    "social_links": [],
}


@router.get("")
async def get_public():
    try:
        return success(data=await _read_all(db.fetch))
    except Exception as exc:  # noqa: BLE001
        logger.warning("Get site content warning (%s), falling back to defaults", exc)
        return success(data=DEFAULT_SITE_DATA)


@router.put("/admin/settings")
async def update_settings(
    request: Request,
    _admin: AdminContext = Depends(require_admin),
):
    try:
        body, _files = await read_body(request)

        columns = [column for column in SETTINGS_COLUMNS if column in body]
        values = [text(body.get(column)) for column in columns]

        lists = {key: _normalize_items(body.get(key), spec) for key, spec in LISTS.items()}
        has_lists = any(value is not None for value in lists.values())

        if not columns and not has_lists:
            raise ApiError(400, "No settings provided")

        async with db.pool().acquire() as connection:
            async with connection.transaction():
                if columns:
                    placeholders = [f"${index + 1}" for index in range(len(columns))]
                    updates = [f"{column} = EXCLUDED.{column}" for column in columns]
                    await connection.execute(
                        f"INSERT INTO {SETTINGS_TABLE} (id, {', '.join(columns)}, updated_at)\n"
                        f"VALUES (1, {', '.join(placeholders)}, CURRENT_TIMESTAMP)\n"
                        f"ON CONFLICT (id) DO UPDATE SET\n"
                        f"  {', '.join(updates)},\n"
                        f"  updated_at = CURRENT_TIMESTAMP",
                        *values,
                    )

                await replace_lists(connection, lists, LISTS)
                data = await _read_all(lambda sql: connection.fetch(sql))

        return success(data=data)
    except ApiError as error:
        return failure(error.message, error.status_code)
    except Exception:  # noqa: BLE001
        logger.exception("Update site settings error")
        return failure("Failed to update site content", 500)


@router.post("/admin/logo")
async def upload_logo(
    request: Request,
    admin: AdminContext = Depends(require_admin),
):
    try:
        _body, files = await read_body(request)
        upload = await extract_file(
            files,
            "image",
            max_mb=config.MAX_SITE_IMAGE_MB,
            size_message=config.SIZE_LIMIT_MESSAGE,
        )
        if upload is None:
            return failure("تصویری ارسال نشده است", 400)

        stored = await storage.upload_file(
            buffer=upload.buffer,
            originalname=upload.originalname,
            mimetype=upload.mimetype,
            folder="site",
            token=admin.token,
        )
        if not stored.get("url"):
            return failure("ذخیره لوگو انجام نشد", 500)

        return await _apply_logo(storage.stored_value(stored), admin)
    except ApiError as error:
        return failure(error.message, error.status_code)
    except Exception as error:  # noqa: BLE001
        logger.exception("Upload site logo error")
        return failure(str(error) or "خطا در آپلود لوگو", 500)


@router.delete("/admin/logo")
async def delete_logo(admin: AdminContext = Depends(require_admin)):
    try:
        current = await db.fetchrow("SELECT logo_url FROM site_settings WHERE id = 1")
        previous = current["logo_url"] if current else None
        if not previous:
            return failure("Site has no logo", 404)

        await db.execute(
            "UPDATE site_settings SET logo_url = NULL, updated_at = CURRENT_TIMESTAMP "
            "WHERE id = 1"
        )
        await storage.remove_stored_file(previous, admin.token, admin.app_id)

        return success(data=await _read_all(db.fetch))
    except Exception:  # noqa: BLE001
        logger.exception("Delete site logo error")
        return failure("Failed to delete site logo", 500)


async def _apply_logo(url: str, admin: AdminContext):
    current = await db.fetchrow("SELECT logo_url FROM site_settings WHERE id = 1")
    previous = current["logo_url"] if current else None

    await db.execute(
        "INSERT INTO site_settings (id, logo_url, updated_at)\n"
        "VALUES (1, $1, CURRENT_TIMESTAMP)\n"
        "ON CONFLICT (id) DO UPDATE SET\n"
        "  logo_url = EXCLUDED.logo_url,\n"
        "  updated_at = CURRENT_TIMESTAMP",
        url,
    )

    # The replaced file is only removed once the new one is stored.
    if previous and previous != url:
        await storage.remove_stored_file(previous, admin.token, admin.app_id)

    return success(data=await _read_all(db.fetch))
