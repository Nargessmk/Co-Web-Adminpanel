"""Home page content: GET /api/home + PUT /api/home/admin/settings.

One singleton row (``home_settings``) holds the standalone texts and links of
the sections; the ordered tables hold the lists (orbit items, feature cards,
customer logos, hero/why statistics, showcase works, testimonials). Lists are
replaced as a whole so the order the admin sees in the dialog is the order the
page renders.
"""

from __future__ import annotations

import logging
from typing import Any, Callable, Optional

from fastapi import APIRouter, Depends, Request

from .. import db, storage
from ..errors import ApiError
from ..helpers import extract_file, read_body, text
from ..lists import replace_lists
from ..page_settings import settings_select
from ..responses import failure, success
from ..security import AdminContext, require_admin

logger = logging.getLogger("cloudland.home")

router = APIRouter(prefix="/api/home", tags=["Home page"])

SETTINGS_TABLE = "home_settings"
# The title is a single value again (hero_title + hero_title_color); only the
# buttons and the statistics are lists, so their old single-value columns are
# not written. hero_title_accent is no longer edited: the gold line under the
# title is decoration, not a second line of text.
SETTINGS_COLUMNS = [
    "hero_badge", "hero_title", "hero_title_color",
    "hero_description", "hero_scroll_label", "hero_image_url",
    "orbit_caption",
    "products_badge", "products_title", "products_description",
    "products_all_label", "products_empty_title", "products_empty_text",
    "why_badge", "why_title", "why_title_accent", "why_description",
    "customers_badge", "customers_title", "customers_title_accent", "customers_description",
    "trust_title", "trust_description",
    "cta_icon", "cta_title", "cta_title_accent", "cta_description",
    "cta_primary_label", "cta_primary_link",
    "cta_secondary_label", "cta_secondary_link",
    "cta_image_url", "cta_tab_hi_label", "cta_tab_quote_label", "cta_submit_label",
    "works_eyebrow", "works_title", "works_description", "works_all_label", "works_details_label",
    "works_tech_label", "works_team_label", "works_cta_label",
    "works_category_label", "works_duration_label",
    "articles_badge", "articles_title", "articles_description",
    "reviews_eyebrow", "reviews_title",
]

# The four title colours the admin picks from; anything else falls back to the
# hero's own navy so a hand-written value cannot inject a style.
TITLE_COLORS = ["#0d1b5e", "#f5a300", "#000000", "#ffffff"]

# Which of the two hero button looks a row uses.
BUTTON_VARIANTS = ["primary", "secondary"]


def _button_fill(item: dict[str, Any]) -> dict[str, Any]:
    if item.get("variant") not in BUTTON_VARIANTS:
        item["variant"] = BUTTON_VARIANTS[0]
    return item


# A statistic is a key + a label: the key decides which number is shown, so
# reordering the rows reorders both halves together.
STAT_KEYS = ["products", "customers", "uptime", "support"]


def _stat_list(scope: str) -> dict[str, Any]:
    def fill(item: dict[str, Any]) -> dict[str, Any]:
        item["scope"] = scope
        if item.get("key") not in STAT_KEYS:
            item["key"] = "products"
        return item

    return {
        "table": "home_stats",
        "columns": ["scope", "key", "label"],
        "required": ["key", "label"],
        "where": f"scope = '{scope}'",
        "fill": fill,
    }


def _orbit_fill(item: dict[str, Any]) -> dict[str, Any]:
    if item.get("ring") not in ("inner", "outer"):
        item["ring"] = "inner"
    if not item.get("color"):
        item["color"] = "#1A2472"
    return item


import json

def _feature_fill(item: dict[str, Any]) -> dict[str, Any]:
    if item.get("color") not in ("navy", "orange", "light", "yellow", "dark", "soft"):
        item["color"] = "navy"
    if not item.get("link"):
        item["link"] = "/solutions"
    if not item.get("link_label"):
        item["link_label"] = "بیشتر بدانید"
    if not item.get("icon"):
        item["icon"] = "code"
    if "iconSrc" in item and not item.get("icon_src"):
        item["icon_src"] = item["iconSrc"]
    if "text" in item and not item.get("description"):
        item["description"] = item["text"]
    if isinstance(item.get("features"), list):
        item["features_json"] = json.dumps(item["features"], ensure_ascii=False)
    return item


def _work_fill(item: dict[str, Any]) -> dict[str, Any]:
    # A card always has an icon and a visual: anything else falls back to the
    # star badge and the phone mockup the section drew before it was editable.
    if not item.get("badge_icon"):
        item["badge_icon"] = "star"
    if item.get("mockup") not in ("phones", "browser"):
        item["mockup"] = "phones"
    if isinstance(item.get("metrics"), list):
        item["metrics_json"] = json.dumps(item["metrics"], ensure_ascii=False)
    if isinstance(item.get("tags"), list):
        item["tags_json"] = json.dumps(item["tags"], ensure_ascii=False)
    return item


LISTS: dict[str, dict[str, Any]] = {
    "buttons": {
        "table": "home_buttons",
        "columns": ["label", "link", "variant"],
        "required": ["label"],
        "where": None,
        "fill": _button_fill,
    },
    "orbit_items": {
        "table": "home_orbit_items",
        "columns": ["ring", "label", "icon", "color"],
        "required": ["label", "icon"],
        "where": None,
        "fill": _orbit_fill,
    },
    "features": {
        "table": "home_features",
        "columns": ["title", "description", "icon", "color", "link", "link_label", "icon_src", "features_json"],
        "required": ["title"],
        "where": None,
        "fill": _feature_fill,
    },
    "customers": {
        "table": "home_customers",
        # Only the name is mandatory now. `logo_url` is the uploaded mark and is
        # what the strip shows; `logo` is the short text brand name kept purely
        # as a fallback for a customer who has no picture yet, so it must not
        # block a save that carries an image.
        "columns": ["name", "logo", "logo_url"],
        "required": ["name"],
        "where": None,
        "fill": lambda item: item,
    },
    "hero_stats": _stat_list("hero"),
    "why_stats": _stat_list("why"),
    "works": {
        "table": "home_works",
        # Only the badge is mandatory: a card can carry no link, no team and no
        # picture (the built-in mockup then stands in for the visual).
        "columns": [
            "badge", "badge_icon", "details_link", "meta_category", "meta_duration",
            "description", "tech", "team", "team_more", "cta_label", "cta_link",
            "image_url", "mockup", "metrics_json", "tags_json",
        ],
        "required": ["badge"],
        "where": None,
        "fill": _work_fill,
    },
    "reviews": {
        "table": "home_reviews",
        # The quote and the name are what a testimonial is made of; the role and
        # the initials are supporting lines and may be missing.
        "columns": ["name", "role", "initials", "text"],
        "required": ["name", "text"],
        "where": None,
        "fill": lambda item: item,
    },
}


def _normalize_items(rows: Any, spec: dict[str, Any]) -> Optional[list[dict[str, Any]]]:
    if rows is None or not isinstance(rows, list):
        return None

    fill: Callable[[dict[str, Any]], dict[str, Any]] = spec["fill"]
    items: list[dict[str, Any]] = []
    for row in rows:
        row = row if isinstance(row, dict) else {}
        item = {column: text(row.get(column)) for column in spec["columns"]}
        filled = fill(dict(item))
        if not all(filled.get(column) for column in spec["required"]):
            continue
        items.append(filled)
    return items


async def _read_all(query) -> dict[str, Any]:
    """``query(sql)`` reads through the pool or through a transaction connection."""
    settings_rows = await query(
        f"SELECT {settings_select(SETTINGS_COLUMNS)} FROM {SETTINGS_TABLE} WHERE id = 1"
    )
    buttons = await query(
        "SELECT label, link, variant FROM home_buttons ORDER BY sort_order ASC, id ASC"
    )
    orbit_items = await query(
        "SELECT ring, label, icon, color FROM home_orbit_items ORDER BY sort_order ASC, id ASC"
    )
    features_raw = await query(
        "SELECT title, description, icon, color, link, link_label, icon_src, features_json FROM home_features ORDER BY sort_order ASC, id ASC"
    )
    customers = await query(
        "SELECT name, logo, logo_url FROM home_customers ORDER BY sort_order ASC, id ASC"
    )
    hero_stats = await query(
        "SELECT key, label FROM home_stats WHERE scope = 'hero' ORDER BY sort_order ASC, id ASC"
    )
    why_stats = await query(
        "SELECT key, label FROM home_stats WHERE scope = 'why' ORDER BY sort_order ASC, id ASC"
    )
    works_raw = await query(
        "SELECT badge, badge_icon, details_link, meta_category, meta_duration,\n"
        "       description, tech, team, team_more, cta_label, cta_link,\n"
        "       image_url, mockup, metrics_json, tags_json\n"
        "FROM home_works ORDER BY sort_order ASC, id ASC"
    )
    reviews = await query(
        "SELECT name, role, initials, text FROM home_reviews ORDER BY sort_order ASC, id ASC"
    )

    parsed_features = []
    for row in features_raw:
        d = dict(row)
        feat_list = []
        if d.get("features_json"):
            try:
                feat_list = json.loads(d["features_json"])
            except Exception:
                pass
        d["features"] = feat_list
        d["text"] = d.get("description")
        icon_key = str(d.get("icon") or "cloud").lower().strip()
        known_3d_icons = {
            "cloud": "cloud",
            "microservices": "microservices",
            "ai": "ai",
            "ux": "ux",
            "security": "security",
            "bigdata": "bigdata",
            "code": "code",
            "language": "ux",
            "smartphone": "ux",
            "cloud_sync": "cloud",
            "shield": "security",
            "verified": "security",
            "support_agent": "ux",
            "trending_up": "bigdata",
            "terminal": "code",
            "developer_mode": "code",
        }
        mapped_icon = known_3d_icons.get(icon_key, "code" if "code" in icon_key else "cloud")
        d["iconSrc"] = d.get("icon_src") or f"/assets/icons3d/{mapped_icon}.svg"
        parsed_features.append(d)

    parsed_works = []
    for row in works_raw:
        w = dict(row)
        m_list = []
        t_list = []
        if w.get("metrics_json"):
            try:
                m_list = json.loads(w["metrics_json"])
            except Exception:
                pass
        if w.get("tags_json"):
            try:
                t_list = json.loads(w["tags_json"])
            except Exception:
                pass
        w["metrics"] = m_list
        w["tags"] = t_list
        w["title"] = w.get("badge")
        parsed_works.append(w)

    return {
        "settings": dict(settings_rows[0]) if settings_rows else None,
        "buttons": [dict(row) for row in buttons],
        "orbit_items": [dict(row) for row in orbit_items],
        "features": parsed_features,
        "services": parsed_features,
        "customers": [dict(row) for row in customers],
        "hero_stats": [dict(row) for row in hero_stats],
        "why_stats": [dict(row) for row in why_stats],
        "works": parsed_works,
        "projects": parsed_works,
        "reviews": [dict(row) for row in reviews],
    }


DEFAULT_HOME_DATA = {
    "settings": {
        "hero_badge": "استودیو هوشمند معماری ابری و مهندسی نرم‌افزار",
        "hero_title": "خلق پلتفرم‌های مقیاس‌پذیر،\nمهندسی سیستم‌های ابری پایدار",
        "hero_title_color": "#0a0a0a",
        "hero_description": "ما به سازمان‌ها و استارتاپ‌های پیشرو کمک می‌کنیم تا نرم‌افزارهای تجاری با پایداری ۹۹.۹۹٪، لتنسی زیر ۱۵ میلی‌ثانیه و معماری امن ابری خلق کنند.",
        "hero_scroll_label": "بررسی توانمندی‌های مهندسی",
        "hero_image_url": "/Modern 3D Tech Dashboard Illustration(1).png",
        "why_badge": "خدمات ما",
        "why_title": "راهکارهای تخصصی مهندسی",
        "why_description": "طراحی سیستم‌های ماژولار سازمانی با مقیاس‌پذیری خودکار و ایزولاسیون امنیتی Zero-Trust.",
        "works_eyebrow": "پروژه‌های شاخص",
        "works_title": "معماری سیستم‌های پرترافیک و مقیاس‌پذیر",
        "cta_title": "آماده‌اید پروژه نرم‌افزاری مقیاس‌پذیر بعدی خود را بسازید؟",
        "cta_description": "تیم مشاوره و معماران ارشد سیستم در کهکشان هوشمند آماده ارزیابی نیازمندی‌ها و ارائه برآورد زمان و هزینه هستند.",
    },
    "buttons": [
        {"label": "درخواست جلسه و مشاوره رایگان", "link": "/contact", "variant": "primary"},
        {"label": "بررسی نمونه‌کارها", "link": "/projects", "variant": "secondary"},
    ],
    "orbit_items": [],
    "features": [],
    "customers": [],
    "hero_stats": [],
    "why_stats": [],
    "works": [],
    "reviews": [],
}


@router.get("")
async def get_public():
    try:
        return success(data=await _read_all(db.fetch))
    except Exception as exc:  # noqa: BLE001
        logger.warning("Get home content warning (%s), falling back to defaults", exc)
        return success(data=DEFAULT_HOME_DATA)


@router.put("/admin/settings")
async def update_settings(
    request: Request,
    _admin: AdminContext = Depends(require_admin),
):
    try:
        body, _files = await read_body(request)
        if "services" in body and "features" not in body:
            body["features"] = body["services"]
        if "projects" in body and "works" not in body:
            body["works"] = body["projects"]

        columns = [column for column in SETTINGS_COLUMNS if column in body]
        values = [text(body.get(column)) for column in columns]
        # The title colour reaches the page as a CSS value, so a hand-written one
        # is replaced by the first of the four the dialog offers.
        if "hero_title_color" in columns and body.get("hero_title_color") not in TITLE_COLORS:
            values[columns.index("hero_title_color")] = TITLE_COLORS[0]

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
        logger.exception("Update home page error")
        return failure("Failed to update home page content", 500)


@router.post("/admin/customers/logo")
async def upload_customer_logo(
    request: Request,
    admin: AdminContext = Depends(require_admin),
):
    """Store a customer's mark and return the URL to put in the row.

    Uploaded separately from the settings save, for the same reason the site
    logo is: the settings endpoint takes JSON, and a file cannot ride along in
    it. The admin then saves the customer list with the returned URL in
    `logo_url`, and the strip prefers that over the text brand name.
    """
    try:
        _fields, files = await read_body(request)
        upload = await extract_file(files, "file")
        if upload is None:
            return failure("No file uploaded or invalid file type", 400)

        stored = await storage.upload_file(
            buffer=upload.buffer,
            originalname=upload.originalname,
            mimetype=upload.mimetype,
            folder="customers",
            token=admin.token,
        )
        logger.info("[home] customer logo stored via %s", stored["source"])
        return success(message="File uploaded", data={"url": storage.stored_value(stored)})
    except ApiError as error:
        return failure(error.message, error.status_code)
    except Exception as error:  # noqa: BLE001
        logger.exception("Upload customer logo error")
        return failure(str(error) or "Upload failed", 500)


@router.post("/admin/works/image")
async def upload_work_image(
    request: Request,
    admin: AdminContext = Depends(require_admin),
):
    """Store a showcase card's screenshot and return the URL for the row.

    The settings save carries JSON, so a picture is uploaded on its own (same
    split as the customer logo): the row only gets its URL when the dialog is
    saved, and the card then prefers that picture over its built-in mockup.
    """
    try:
        _fields, files = await read_body(request)
        upload = await extract_file(files, "file")
        if upload is None:
            return failure("No file uploaded or invalid file type", 400)

        stored = await storage.upload_file(
            buffer=upload.buffer,
            originalname=upload.originalname,
            mimetype=upload.mimetype,
            folder="works",
            token=admin.token,
        )
        logger.info("[home] work image stored via %s", stored["source"])
        return success(message="File uploaded", data={"url": storage.stored_value(stored)})
    except ApiError as error:
        return failure(error.message, error.status_code)
    except Exception as error:  # noqa: BLE001
        logger.exception("Upload work image error")
        return failure(str(error) or "Upload failed", 500)


@router.post("/admin/hero/image")
async def upload_hero_image(
    request: Request,
    admin: AdminContext = Depends(require_admin),
):
    """Upload and store the homepage hero visual picture."""
    try:
        _fields, files = await read_body(request)
        upload = await extract_file(files, "file")
        if upload is None:
            return failure("No file uploaded or invalid file type", 400)

        stored = await storage.upload_file(
            buffer=upload.buffer,
            originalname=upload.originalname,
            mimetype=upload.mimetype,
            folder="hero",
            token=admin.token,
        )
        logger.info("[home] hero image stored via %s", stored["source"])
        return success(message="File uploaded", data={"url": storage.stored_value(stored)})
    except ApiError as error:
        return failure(error.message, error.status_code)
    except Exception as error:  # noqa: BLE001
        logger.exception("Upload hero image error")
        return failure(str(error) or "Upload failed", 500)


@router.post("/admin/cta/image")
async def upload_cta_image(
    request: Request,
    admin: AdminContext = Depends(require_admin),
):
    """Upload and store the homepage CTA / contact visual picture."""
    try:
        _fields, files = await read_body(request)
        upload = await extract_file(files, "file")
        if upload is None:
            return failure("No file uploaded or invalid file type", 400)

        stored = await storage.upload_file(
            buffer=upload.buffer,
            originalname=upload.originalname,
            mimetype=upload.mimetype,
            folder="cta",
            token=admin.token,
        )
        logger.info("[home] CTA image stored via %s", stored["source"])
        return success(message="File uploaded", data={"url": storage.stored_value(stored)})
    except ApiError as error:
        return failure(error.message, error.status_code)
    except Exception as error:  # noqa: BLE001
        logger.exception("Upload CTA image error")
        return failure(str(error) or "Upload failed", 500)

