"""About page content: GET /api/about (public) + admin CRUD.

Every About-page text the admin panel is allowed to edit. Section background
colours are part of the site theme and deliberately not stored here.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, Request

from .. import db
from ..errors import ApiError
from ..helpers import (
    js_bool,
    optional_order,
    read_body,
    text,
)
from ..page_settings import read_settings, upsert_settings
from ..responses import failure, success
from ..security import AdminContext, require_admin

logger = logging.getLogger("cloudland.about")

router = APIRouter(prefix="/api/about", tags=["About page"])

import json

SETTINGS_TABLE = "about_settings"
SETTINGS_COLUMNS = [
    "hero_badge",
    "hero_title",
    "hero_title_accent",
    "hero_description",
    "timeline_title",
    "team_title",
    "team_subtitle",
    "statement_title",
    "statement_p1",
    "statement_p2",
    "metrics_json",
    "values_json",
    "milestones_json",
    "cta_icon",
    "cta_eyebrow",
    "cta_title",
    "cta_description",
    "cta_primary_icon",
    "cta_primary_label",
    "cta_primary_link",
    "cta_secondary_icon",
    "cta_secondary_label",
    "cta_secondary_link",
]
# Icons always need a value, so an empty string falls back to these.
ICON_DEFAULTS = {
    "cta_icon": "support_agent",
    "cta_primary_icon": "mail",
    "cta_secondary_icon": "inventory_2",
}

STAT_SELECT = "id, value, label, icon, sort_order"
CARD_SELECT = "id, title, description, icon, is_highlight, sort_order"
TIMELINE_SELECT = "id, year, title, description, icon, sort_order"
PERK_SELECT = "id, label, icon, sort_order"

# Internal table names only — never user input.
_TABLES = {"stats": "about_stats", "cards": "about_mission_cards", "timeline": "about_timeline", "perks": "about_cta_perks"}


async def _next_order(table: str) -> int:
    value = await db.fetchval(f"SELECT COALESCE(MAX(sort_order), -1) + 1 FROM {table}")
    return int(value or 0)


async def _read_all() -> dict:
    settings = await read_settings(SETTINGS_TABLE, SETTINGS_COLUMNS)
    s_dict = settings.get("settings") or {}

    stats = await db.fetch(f"SELECT {STAT_SELECT} FROM about_stats ORDER BY sort_order ASC, id ASC")
    cards = await db.fetch(f"SELECT {CARD_SELECT} FROM about_mission_cards ORDER BY sort_order ASC, id ASC")
    timeline = await db.fetch(f"SELECT {TIMELINE_SELECT} FROM about_timeline ORDER BY sort_order ASC, id ASC")
    perks = await db.fetch(f"SELECT {PERK_SELECT} FROM about_cta_perks ORDER BY sort_order ASC, id ASC")
    team = await db.fetch("SELECT id, full_name as name, role, resume_fa as bio, image_url as image FROM team_members WHERE is_active = true ORDER BY sort_order ASC, id ASC")

    # Parse JSON columns if present
    parsed_metrics = None
    if s_dict.get("metrics_json"):
        try:
            parsed_metrics = json.loads(s_dict["metrics_json"])
        except Exception:
            pass

    parsed_values = None
    if s_dict.get("values_json"):
        try:
            parsed_values = json.loads(s_dict["values_json"])
        except Exception:
            pass

    parsed_milestones = None
    if s_dict.get("milestones_json"):
        try:
            parsed_milestones = json.loads(s_dict["milestones_json"])
        except Exception:
            pass

    team_list = [dict(row) for row in team]
    if not team_list:
        team_list = DEFAULT_ABOUT_DATA["team"]

    return {
        "settings": s_dict,
        "statementTitle": s_dict.get("statement_title") or DEFAULT_ABOUT_DATA["statementTitle"],
        "statementP1": s_dict.get("statement_p1") or DEFAULT_ABOUT_DATA["statementP1"],
        "statementP2": s_dict.get("statement_p2") or DEFAULT_ABOUT_DATA["statementP2"],
        "metrics": parsed_metrics or DEFAULT_ABOUT_DATA["metrics"],
        "values": parsed_values or DEFAULT_ABOUT_DATA["values"],
        "milestones": parsed_milestones or DEFAULT_ABOUT_DATA["milestones"],
        "team": team_list,
        "stats": [dict(row) for row in stats],
        "mission_cards": [dict(row) for row in cards],
        "timeline": [dict(row) for row in timeline],
        "cta_perks": [dict(row) for row in perks],
    }


DEFAULT_ABOUT_DATA = {
    "settings": {
        "hero_badge": "درباره کهکشان هوشمند",
        "hero_title": "اصالت مهندسی، انضباط سازمانی",
        "hero_description": "ما یک استودیوی پیشرو در معماری نرم‌افزارهای تجاری و زیرساخت‌های ابری هستیم که دقت فنی را با استانداردهای بین‌المللی سازمانی تلفیق می‌کنیم.",
        "statement_title": "پیشگام در مهندسی سیستم‌های توزیع‌شده با قابلیت اتکای سازمانی",
    },
    "statementTitle": "پیشگام در مهندسی سیستم‌های توزیع‌شده با قابلیت اتکای سازمانی",
    "statementP1": "کهکشان هوشمند متشکل از معماران ارشد سیستم، مهندسان زیرساخت ابری و متخصصان داده با سابقه طراحی و اجرای سیستم‌های پرترافیک سازمانی است. رویکرد ما در مهندسی نرم‌افزار متکی بر شفافیت کد منبع، کاهش ریسک‌های عملیاتی و ایزولاسیون امنیتی Zero-Trust بنا شده است.",
    "statementP2": "ما پیچیدگی‌های فنی را به معماری‌های ساده، آزمون‌پذیر و پایدار تبدیل می‌کنیم تا تصمیم‌گیرندگان تجاری بتوانند با آرامش کامل و بدون دغدغه قطعی سرور یا گلوگاه‌های ترافیکی، مسیر رشد کسب‌وکار خود را دنبال کنند.",
    "metrics": [
        {"val": "+۸۵", "title": "سامانه سازمانی استقراریافته", "desc": "پروژه‌های موفق ملی و تجاری با پایداری کامل"},
        {"val": "۹۹.۹۹٪", "title": "تضمین قرارداد سطح خدمات (SLA)", "desc": "پایداری زیرساخت بدون قطعی و وقفه ناخواسته"},
        {"val": "< ۱۵ms", "title": "لتنسی شبکه در نقاط لبه Anycast", "desc": "پاسخ‌دهی آنی درخواست‌ها در لبه شبکه ابری"},
        {"val": "۲۰+", "title": "متخصصان و معماران ارشد", "desc": "تیم تخصصی با مدارک معتبر بین‌المللی ابری"},
    ],
    "values": [
        {
            "title": "معماری تاب‌آور و Zero-Downtime",
            "desc": "تمامی سرویس‌ها با منطق توزیع جغرافیایی، Failover خودکار و ایزولاسیون پردازش طراحی می‌شوند تا حتی در بحرانی‌ترین شرایط ترافیکی بدون وقفه به کار خود ادامه دهند.",
            "icon": "dns",
        },
        {
            "title": "امنیت چندسطحی Zero-Trust",
            "desc": "هیچ درخواستی بدون احراز هویت و رمزنگاری سراسری پذیرفته نمی‌شود. انطباق با استاندارد ISO 27001 و تفکیک لایه‌های دسترسی، امضای امنیتی پروژه‌های ماست.",
            "icon": "security",
        },
        {
            "title": "شفافیت فنی و مالکیت کامل کارفرما",
            "desc": "کد تمیز، مستندسازی RFC استاندارد و تحویل کامل تمام کدهای منبع، کانتینرها و خطوط پایپ‌لاین CI/CD به کارفرما بدون هیچ‌گونه قفل‌شدگی به ارائه‌دهنده خاص.",
            "icon": "code",
        },
        {
            "title": "وسواس در کارایی و لتنسی میلی‌ثانیه‌ای",
            "desc": "پایش مستمر پروفایلینگ مصرف رم و پردازنده و بهینه‌سازی لایه‌های داده با کش‌های توزیع‌شده Redis Cluster برای دستیابی به کمترین زمان پاسخ‌دهی ممکن.",
            "icon": "speed",
        },
    ],
    "milestones": [
        {"year": "۱۳۹۸", "title": "آغاز فعالیت هسته مهندسی", "desc": "تأسیس کهکشان هوشمند با تمرکز بر مشاوره معماری سیستم‌های توزیع‌شده و پردازش ابری."},
        {"year": "۱۴۰۰", "title": "توسعه پلتفرم ابری Anycast", "desc": "راه‌اندازی زیرساخت لبه با بیش از ۳۰ نقطه حضور (PoP) در سراسر کشور و اتصال مستقیم به IXP."},
        {"year": "۱۴۰۲", "title": "ورود به حوزه مدل‌های پردازش هوش مصنوعی در لبه", "desc": "ارائه راهکارهای فشرده‌سازی و استقرار مدل‌های LLM و پردازش صوت به صورت آفلاین بر روی چیپ‌های Edge."},
        {"year": "۱۴۰۴", "title": "تضمین SLA ۹۹.۹۹٪ برای بیش از ۸۵ سامانه ملی", "desc": "پوشش تراکنش‌های روزانه چندمیلیونی در حوزه‌های بانکی، لجستیک و تلکام بدون حتی یک دقیقه قطعی."},
    ],
    "team": [
        {
            "name": "مهندس آرش رادمنش",
            "role": "معمار ارشد سیستم و هم‌بنیان‌گذار",
            "bio": "بیش از ۱۵ سال سابقه طراحی معماری نرم‌افزارهای تجاری با ترافیک میلیون تراکنش روزانه و متخصص سیستم‌های توزیع‌شده.",
            "image": "/images/home/contact-programming.jpg",
            "tags": ["Distributed Systems", "Golang Core", "Kubernetes"],
        },
        {
            "name": "مهندس نیما سهرابی",
            "role": "سرپرست ارشد زیرساخت ابری و DevOps",
            "bio": "متخصص کلاسترهای چندناحیه‌ای کوبرنتیز، امنیت Zero-Trust و اتوماسیون CI/CD با تجارب استقرار بانکی.",
            "image": "/images/home/contact-datacenter.jpg",
            "tags": ["Cloud Architecture", "Zero-Trust", "Terraform"],
        },
        {
            "name": "دکتر سارا یزدانی",
            "role": "سرپرست تیم هوش مصنوعی و داده",
            "bio": "پژوهشگر یادگیری عمیق، مدل‌های زبانی بزرگ (LLM) و پردازش بلادرنگ داده‌های صوتی و متنی در لبه شبکه.",
            "image": "/images/home/hero-corporate.jpg",
            "tags": ["Edge AI", "PyTorch C++", "RAG Systems"],
        },
        {
            "name": "مهندس مهرداد کیا",
            "role": "مدیر ارشد طراحی محصول و تجربه کاربری",
            "bio": "طراح استراتژیک سیستم‌های دیزاین سازمانی، رابط‌های کاربری تعاملی مدرن و متخصص ارگونومی بصری.",
            "image": "/Modern 3D Tech Dashboard Illustration(1).png",
            "tags": ["Design Systems", "Micro-interactions", "Design Ops"],
        },
    ],
    "stats": [],
    "mission_cards": [],
    "timeline": [],
    "cta_perks": [],
}


@router.get("")
async def get_public():
    try:
        return success(data=await _read_all())
    except Exception as exc:  # noqa: BLE001
        logger.warning("Get about page warning (%s), falling back to defaults", exc)
        return success(data=DEFAULT_ABOUT_DATA)


@router.put("/admin/settings")
async def update_settings(
    request: Request,
    _admin: AdminContext = Depends(require_admin),
):
    try:
        body, _files = await read_body(request)
        if "metrics" in body and not body.get("metrics_json"):
            body["metrics_json"] = json.dumps(body["metrics"], ensure_ascii=False)
        if "values" in body and not body.get("values_json"):
            body["values_json"] = json.dumps(body["values"], ensure_ascii=False)
        if "milestones" in body and not body.get("milestones_json"):
            body["milestones_json"] = json.dumps(body["milestones"], ensure_ascii=False)
        row = await upsert_settings(SETTINGS_TABLE, SETTINGS_COLUMNS, body, ICON_DEFAULTS)
        return success(data=row)
    except ApiError as error:
        return failure(error.message, error.status_code)
    except Exception:  # noqa: BLE001
        logger.exception("Update about settings error")
        return failure("Failed to update about page settings", 500)


# ------------------------------------------------------------- stats CRUD ----
@router.post("/admin/stats")
async def create_stat(
    request: Request,
    _admin: AdminContext = Depends(require_admin),
):
    try:
        body, _files = await read_body(request)
        value, label = text(body.get("value")), text(body.get("label"))
        if not value or not label:
            return failure("value and label are required", 400)

        requested = optional_order(body.get("sort_order"))
        order = await _next_order(_TABLES["stats"]) if requested is None else requested

        row = await db.fetchrow(
            f"INSERT INTO about_stats (value, label, icon, sort_order) "
            f"VALUES ($1, $2, $3, $4) RETURNING {STAT_SELECT}",
            value,
            label,
            text(body.get("icon")) or "star",
            order,
        )
        return success(data=row, status_code=201)
    except Exception:  # noqa: BLE001
        logger.exception("Create about stat error")
        return failure("Failed to create stat", 500)


@router.put("/admin/stats/{stat_id}")
async def update_stat(
    stat_id: int,
    request: Request,
    _admin: AdminContext = Depends(require_admin),
):
    try:
        body, _files = await read_body(request)
        value, label = text(body.get("value")), text(body.get("label"))
        if not value or not label:
            return failure("value and label are required", 400)

        row = await db.fetchrow(
            f"UPDATE about_stats SET\n"
            f"  value = $1,\n"
            f"  label = $2,\n"
            f"  icon = $3,\n"
            f"  sort_order = COALESCE($4, sort_order),\n"
            f"  updated_at = CURRENT_TIMESTAMP\n"
            f"WHERE id = $5\n"
            f"RETURNING {STAT_SELECT}",
            value,
            label,
            text(body.get("icon")) or "star",
            optional_order(body.get("sort_order")),
            stat_id,
        )
        if row is None:
            return failure("Stat not found", 404)
        return success(data=row)
    except Exception:  # noqa: BLE001
        logger.exception("Update about stat error")
        return failure("Failed to update stat", 500)


@router.delete("/admin/stats/{stat_id}")
async def delete_stat(
    stat_id: int,
    _admin: AdminContext = Depends(require_admin),
):
    try:
        row = await db.fetchrow("DELETE FROM about_stats WHERE id = $1 RETURNING id", stat_id)
        if row is None:
            return failure("Stat not found", 404)
        return success(message="Stat deleted")
    except Exception:  # noqa: BLE001
        logger.exception("Delete about stat error")
        return failure("Failed to delete stat", 500)


# ----------------------------------------------- mission / vision cards CRUD ---
@router.post("/admin/mission-cards")
async def create_mission_card(
    request: Request,
    _admin: AdminContext = Depends(require_admin),
):
    try:
        body, _files = await read_body(request)
        title = text(body.get("title"))
        if not title:
            return failure("title is required", 400)

        requested = optional_order(body.get("sort_order"))
        order = await _next_order(_TABLES["cards"]) if requested is None else requested

        row = await db.fetchrow(
            f"INSERT INTO about_mission_cards (title, description, icon, is_highlight, sort_order) "
            f"VALUES ($1, $2, $3, $4, $5) RETURNING {CARD_SELECT}",
            title,
            text(body.get("description")),
            text(body.get("icon")) or "star",
            js_bool(body.get("is_highlight")),
            order,
        )
        return success(data=row, status_code=201)
    except Exception:  # noqa: BLE001
        logger.exception("Create about mission card error")
        return failure("Failed to create card", 500)


@router.put("/admin/mission-cards/{card_id}")
async def update_mission_card(
    card_id: int,
    request: Request,
    _admin: AdminContext = Depends(require_admin),
):
    try:
        body, _files = await read_body(request)
        title = text(body.get("title"))
        if not title:
            return failure("title is required", 400)

        row = await db.fetchrow(
            f"UPDATE about_mission_cards SET\n"
            f"  title = $1,\n"
            f"  description = $2,\n"
            f"  icon = $3,\n"
            f"  is_highlight = $4,\n"
            f"  sort_order = COALESCE($5, sort_order),\n"
            f"  updated_at = CURRENT_TIMESTAMP\n"
            f"WHERE id = $6\n"
            f"RETURNING {CARD_SELECT}",
            title,
            text(body.get("description")),
            text(body.get("icon")) or "star",
            js_bool(body.get("is_highlight")),
            optional_order(body.get("sort_order")),
            card_id,
        )
        if row is None:
            return failure("Card not found", 404)
        return success(data=row)
    except Exception:  # noqa: BLE001
        logger.exception("Update about mission card error")
        return failure("Failed to update card", 500)


@router.delete("/admin/mission-cards/{card_id}")
async def delete_mission_card(
    card_id: int,
    _admin: AdminContext = Depends(require_admin),
):
    try:
        row = await db.fetchrow(
            "DELETE FROM about_mission_cards WHERE id = $1 RETURNING id", card_id
        )
        if row is None:
            return failure("Card not found", 404)
        return success(message="Card deleted")
    except Exception:  # noqa: BLE001
        logger.exception("Delete about mission card error")
        return failure("Failed to delete card", 500)


# ---------------------------------------------------------- timeline CRUD -----
@router.post("/admin/timeline")
async def create_timeline(
    request: Request,
    _admin: AdminContext = Depends(require_admin),
):
    try:
        body, _files = await read_body(request)
        year, title = text(body.get("year")), text(body.get("title"))
        if not year or not title:
            return failure("year and title are required", 400)

        requested = optional_order(body.get("sort_order"))
        order = await _next_order(_TABLES["timeline"]) if requested is None else requested

        row = await db.fetchrow(
            f"INSERT INTO about_timeline (year, title, description, icon, sort_order) "
            f"VALUES ($1, $2, $3, $4, $5) RETURNING {TIMELINE_SELECT}",
            year,
            title,
            text(body.get("description")),
            text(body.get("icon")) or "star",
            order,
        )
        return success(data=row, status_code=201)
    except Exception:  # noqa: BLE001
        logger.exception("Create about timeline item error")
        return failure("Failed to create timeline item", 500)


@router.put("/admin/timeline/{item_id}")
async def update_timeline(
    item_id: int,
    request: Request,
    _admin: AdminContext = Depends(require_admin),
):
    try:
        body, _files = await read_body(request)
        year, title = text(body.get("year")), text(body.get("title"))
        if not year or not title:
            return failure("year and title are required", 400)

        row = await db.fetchrow(
            f"UPDATE about_timeline SET\n"
            f"  year = $1,\n"
            f"  title = $2,\n"
            f"  description = $3,\n"
            f"  icon = $4,\n"
            f"  sort_order = COALESCE($5, sort_order),\n"
            f"  updated_at = CURRENT_TIMESTAMP\n"
            f"WHERE id = $6\n"
            f"RETURNING {TIMELINE_SELECT}",
            year,
            title,
            text(body.get("description")),
            text(body.get("icon")) or "star",
            optional_order(body.get("sort_order")),
            item_id,
        )
        if row is None:
            return failure("Timeline item not found", 404)
        return success(data=row)
    except Exception:  # noqa: BLE001
        logger.exception("Update about timeline item error")
        return failure("Failed to update timeline item", 500)


@router.delete("/admin/timeline/{item_id}")
async def delete_timeline(
    item_id: int,
    _admin: AdminContext = Depends(require_admin),
):
    try:
        row = await db.fetchrow(
            "DELETE FROM about_timeline WHERE id = $1 RETURNING id", item_id
        )
        if row is None:
            return failure("Timeline item not found", 404)
        return success(message="Timeline item deleted")
    except Exception:  # noqa: BLE001
        logger.exception("Delete about timeline item error")
        return failure("Failed to delete timeline item", 500)


# ------------------------------------------------------------- perks CRUD ----
@router.post("/admin/perks")
async def create_perk(
    request: Request,
    _admin: AdminContext = Depends(require_admin),
):
    try:
        body, _files = await read_body(request)
        label = text(body.get("label"))
        if not label:
            return failure("label is required", 400)

        requested = optional_order(body.get("sort_order"))
        order = await _next_order(_TABLES["perks"]) if requested is None else requested

        row = await db.fetchrow(
            f"INSERT INTO about_cta_perks (label, icon, sort_order) "
            f"VALUES ($1, $2, $3) RETURNING {PERK_SELECT}",
            label,
            text(body.get("icon")) or "verified",
            order,
        )
        return success(data=row, status_code=201)
    except Exception:  # noqa: BLE001
        logger.exception("Create about perk error")
        return failure("Failed to create perk", 500)


@router.put("/admin/perks/{perk_id}")
async def update_perk(
    perk_id: int,
    request: Request,
    _admin: AdminContext = Depends(require_admin),
):
    try:
        body, _files = await read_body(request)
        label = text(body.get("label"))
        if not label:
            return failure("label is required", 400)

        row = await db.fetchrow(
            f"UPDATE about_cta_perks SET\n"
            f"  label = $1,\n"
            f"  icon = $2,\n"
            f"  sort_order = COALESCE($3, sort_order)\n"
            f"WHERE id = $4\n"
            f"RETURNING {PERK_SELECT}",
            label,
            text(body.get("icon")) or "verified",
            optional_order(body.get("sort_order")),
            perk_id,
        )
        if row is None:
            return failure("Perk not found", 404)
        return success(data=row)
    except Exception:  # noqa: BLE001
        logger.exception("Update about perk error")
        return failure("Failed to update perk", 500)


@router.delete("/admin/perks/{perk_id}")
async def delete_perk(
    perk_id: int,
    _admin: AdminContext = Depends(require_admin),
):
    try:
        row = await db.fetchrow(
            "DELETE FROM about_cta_perks WHERE id = $1 RETURNING id", perk_id
        )
        if row is None:
            return failure("Perk not found", 404)
        return success(message="Perk deleted")
    except Exception:  # noqa: BLE001
        logger.exception("Delete about perk error")
        return failure("Failed to delete perk", 500)

