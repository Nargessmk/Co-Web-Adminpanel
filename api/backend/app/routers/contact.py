"""Contact page content: GET /api/contact + admin CRUD.

Every Contact-page text the admin panel is allowed to edit. The request form
itself stays separate and posts to /api/consultations.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, Request

from .. import db
from ..errors import ApiError
from ..helpers import (
    optional_order,
    read_body,
    text,
)
from ..page_settings import read_settings, upsert_settings
from ..responses import failure, success
from ..security import AdminContext, require_admin

logger = logging.getLogger("cloudland.contact")

router = APIRouter(prefix="/api/contact", tags=["Contact page"])

import json

SETTINGS_TABLE = "contact_settings"
SETTINGS_COLUMNS = [
    "hero_badge",
    "hero_title",
    "hero_title_accent",
    "hero_description",
    "aside_title",
    "aside_description",
    "aside_icon",
    "form_title",
    "form_subtitle",
    "form_submit_label",
    "phone",
    "email",
    "address",
    "working_hours",
    "emergency_support",
    "sla_response",
    "faqs_json",
]
ICON_DEFAULTS = {"aside_icon": "support_agent"}
CARD_SELECT = "id, label, value, icon, sort_order"


async def _next_order() -> int:
    value = await db.fetchval(
        "SELECT COALESCE(MAX(sort_order), -1) + 1 FROM contact_info_cards"
    )
    return int(value or 0)


async def _read_all() -> dict:
    settings = await read_settings(SETTINGS_TABLE, SETTINGS_COLUMNS)
    s_dict = settings.get("settings") or {}
    cards = await db.fetch(f"SELECT {CARD_SELECT} FROM contact_info_cards ORDER BY sort_order ASC, id ASC")

    parsed_faqs = None
    if s_dict.get("faqs_json"):
        try:
            parsed_faqs = json.loads(s_dict["faqs_json"])
        except Exception:
            pass

    return {
        "settings": s_dict,
        "phone": s_dict.get("phone") or DEFAULT_CONTACT_DATA["phone"],
        "email": s_dict.get("email") or DEFAULT_CONTACT_DATA["email"],
        "address": s_dict.get("address") or DEFAULT_CONTACT_DATA["address"],
        "workingHours": s_dict.get("working_hours") or DEFAULT_CONTACT_DATA["workingHours"],
        "emergencySupport": s_dict.get("emergency_support") or DEFAULT_CONTACT_DATA["emergencySupport"],
        "slaResponse": s_dict.get("sla_response") or DEFAULT_CONTACT_DATA["slaResponse"],
        "faqs": parsed_faqs or DEFAULT_CONTACT_DATA["faqs"],
        "info_cards": [dict(row) for row in cards],
    }


DEFAULT_CONTACT_DATA = {
    "settings": {
        "hero_badge": "ارتباط مستقیم و مشاوره تخصصی",
        "hero_title": "بیایید پروژه نرم‌افزاری و زیرساخت ابری شما را آغاز کنیم",
        "hero_description": "کارشناسان و معماران ارشد کهکشان هوشمند آماده ارائه مشاوره در زمینه معماری نرم‌افزار، زیرساخت ابری و تخمین زمان و هزینه پروژه‌های شما هستند.",
        "form_title": "درخواست جلسه مشاوره و بررسی پروژه",
        "form_subtitle": "مشخصات اولیه سازمان و نیازمندی‌های فنی خود را ثبت کنید تا در سریع‌ترین زمان با شما تماس بگیریم.",
    },
    "phone": "۰۲۱ - ۸۸۹۰ ۱۲۳۴",
    "email": "contact@smartgalaxy.land",
    "address": "تهران، نلسون ماندلا (جردن)، بالاتر از میرداماد، برج کهکشان، طبقه ۱۲",
    "workingHours": "شنبه تا چهارشنبه: ۸:۰۰ الی ۱۸:۰۰ | پنجشنبه: ۸:۰۰ الی ۱۳:۰۰",
    "emergencySupport": "پایش و پشتیبانی زیرساخت‌های ابری: ۲۴ ساعته / ۷ روز هفته",
    "slaResponse": "میانگین زمان پاسخ‌دهی به درخواست‌های جدید کمتر از ۲ ساعت است.",
    "faqs": [
        {
            "q": "فرآیند شروع همکاری و بررسی نیازمندی‌ها چگونه است؟",
            "a": "پس از تکمیل فرم، ظرف کمتر از ۲ ساعت کاری معمار ارشد سیستم با شما تماس گرفته و جلسه آنلاین یا حضوری جهت دریافت نیازمندی‌ها و تنظیم توافق‌نامه محرمانگی (NDA) هماهنگ می‌شود.",
        },
        {
            "q": "آیا امکان ارائه قرارداد سطح خدمات (SLA) رسمی وجود دارد؟",
            "a": "بله، تمامی پروژه‌های سازمانی و استقرار زیرساخت‌های ابری ما دارای تضمین رسمی آپ‌تایم ۹۹.۹۹٪ با جبران خسارت مکتوب در قرارداد حقوقی هستند.",
        },
        {
            "q": "تخمین هزینه و زمان‌بندی پروژه چقدر زمان می‌برد؟",
            "a": "معمولاً پس از جلسه اولیه شناخت و دریافت RFC یا مستندات، سند تفصیلی معماری (Architecture Blueprint) به همراه هزینه شفاف ظرف حداکثر ۳ تا ۵ روز کاری تقدیم می‌شود.",
        },
        {
            "q": "آیا سورس‌کد و مالکیت فکری پروژه به کارفرما واگذار می‌شود؟",
            "a": "صد در صد. تمامی کدهای توسعه‌یافته، خطوط استقرار CI/CD و اسناد معماری به صورت کامل و اختصاصی به سازمان شما واگذار خواهد شد.",
        },
    ],
    "info_cards": [],
}


@router.get("")
async def get_public():
    try:
        return success(data=await _read_all())
    except Exception as exc:  # noqa: BLE001
        logger.warning("Get contact page warning (%s), falling back to defaults", exc)
        return success(data=DEFAULT_CONTACT_DATA)


@router.put("/admin/settings")
async def update_settings(
    request: Request,
    _admin: AdminContext = Depends(require_admin),
):
    try:
        body, _files = await read_body(request)
        if "workingHours" in body and "working_hours" not in body:
            body["working_hours"] = body["workingHours"]
        if "emergencySupport" in body and "emergency_support" not in body:
            body["emergency_support"] = body["emergencySupport"]
        if "slaResponse" in body and "sla_response" not in body:
            body["sla_response"] = body["slaResponse"]
        if "faqs" in body and not body.get("faqs_json"):
            body["faqs_json"] = json.dumps(body["faqs"], ensure_ascii=False)

        row = await upsert_settings(SETTINGS_TABLE, SETTINGS_COLUMNS, body, ICON_DEFAULTS)
        return success(data=row)
    except ApiError as error:
        return failure(error.message, error.status_code)
    except Exception:  # noqa: BLE001
        logger.exception("Update contact settings error")
        return failure("Failed to update contact page settings", 500)


@router.post("/admin/info-cards")
async def create_info_card(
    request: Request,
    _admin: AdminContext = Depends(require_admin),
):
    try:
        body, _files = await read_body(request)
        label = text(body.get("label"))
        value = text(body.get("value"))
        if not label or not value:
            return failure("label and value are required", 400)

        requested = optional_order(body.get("sort_order"))
        order = await _next_order() if requested is None else requested

        row = await db.fetchrow(
            f"INSERT INTO contact_info_cards (label, value, icon, sort_order) "
            f"VALUES ($1, $2, $3, $4) RETURNING {CARD_SELECT}",
            label,
            value,
            text(body.get("icon")) or "info",
            order,
        )
        return success(data=row, status_code=201)
    except Exception:  # noqa: BLE001
        logger.exception("Create contact info card error")
        return failure("Failed to create info card", 500)


@router.put("/admin/info-cards/{card_id}")
async def update_info_card(
    card_id: int,
    request: Request,
    _admin: AdminContext = Depends(require_admin),
):
    try:
        body, _files = await read_body(request)
        label = text(body.get("label"))
        value = text(body.get("value"))
        if not label or not value:
            return failure("label and value are required", 400)

        row = await db.fetchrow(
            f"UPDATE contact_info_cards SET \n"
            f"  label = $1,\n"
            f"  value = $2,\n"
            f"  icon = $3,\n"
            f"  sort_order = COALESCE($4, sort_order),\n"
            f"  updated_at = CURRENT_TIMESTAMP\n"
            f"WHERE id = $5\n"
            f"RETURNING {CARD_SELECT}",
            label,
            value,
            text(body.get("icon")) or "info",
            optional_order(body.get("sort_order")),
            card_id,
        )
        if row is None:
            return failure("Info card not found", 404)
        return success(data=row)
    except Exception:  # noqa: BLE001
        logger.exception("Update contact info card error")
        return failure("Failed to update info card", 500)


@router.delete("/admin/info-cards/{card_id}")
async def delete_info_card(
    card_id: int,
    _admin: AdminContext = Depends(require_admin),
):
    try:
        row = await db.fetchrow(
            "DELETE FROM contact_info_cards WHERE id = $1 RETURNING id", card_id
        )
        if row is None:
            return failure("Info card not found", 404)
        return success(message="Info card deleted")
    except Exception:  # noqa: BLE001
        logger.exception("Delete contact info card error")
        return failure("Failed to delete info card", 500)
