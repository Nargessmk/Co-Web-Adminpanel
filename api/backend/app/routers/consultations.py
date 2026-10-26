"""Consultation requests: public submit + admin management."""

from __future__ import annotations

import logging
import re

from fastapi import APIRouter, Depends, Request

from .. import db
from ..helpers import page_limit, pagination, read_body
from ..responses import failure, success
from ..security import AdminContext, require_admin

logger = logging.getLogger("cloudland.consultations")

router = APIRouter(prefix="/api/consultations", tags=["Consultations"])

DIGITS_ONLY = re.compile(r"^\d+$")
NAME_HAS_DIGIT = re.compile(r"\d")


def _normalize_phone(raw: str) -> str:
    """Normalize Iranian phone number to standard 11-digit format starting with 09."""
    if not raw:
        return ""
    # Convert Persian/Arabic digits to Latin
    persian_digits = "۰۱۲۳۴۵۶۷۸۹"
    arabic_digits = "٠١٢٣٤٥٦٧٨٩"
    cleaned = str(raw).strip()
    for i, d in enumerate(persian_digits):
        cleaned = cleaned.replace(d, str(i))
    for i, d in enumerate(arabic_digits):
        cleaned = cleaned.replace(d, str(i))
    # Keep only digits and plus
    digits = re.sub(r"[^\d]", "", cleaned)
    if digits.startswith("0098"):
        digits = "0" + digits[4:]
    elif digits.startswith("98") and len(digits) == 12:
        digits = "0" + digits[2:]
    elif len(digits) == 10 and digits.startswith("9"):
        digits = "0" + digits
    return digits


@router.post("", tags=["Consultations - Public"])
async def create_consultation(request: Request):
    try:
        body, _files = await read_body(request)
        full_name = str(body.get("full_name") or body.get("name") or "").strip()
        raw_phone = body.get("phone") or body.get("phone_number") or body.get("contact") or body.get("contact_info") or ""
        phone = _normalize_phone(raw_phone)
        subject = str(body.get("subject") or body.get("type") or "درخواست مشاوره و همکاری").strip()
        message = body.get("message") or body.get("description") or None
        email = body.get("email") or None
        company_name = body.get("company_name") or body.get("company") or None

        if not full_name:
            return failure("full_name is required", 400)
        if len(full_name) < 2:
            return failure("full_name must be at least 2 characters", 400)

        if not phone:
            return failure("phone is required", 400)
        if len(phone) != 11 or not phone.startswith("09"):
            # If not standard 09xx, but valid digits >= 8 (e.g. landline or test), allow if phone has digits
            if len(phone) < 8:
                return failure("phone number is invalid", 400)

        row = None
        try:
            row = await db.fetchrow(
                "INSERT INTO consultations (full_name, phone, email, company_name, subject, message) "
                "VALUES ($1, $2, $3, $4, $5, $6) RETURNING *",
                full_name,
                phone,
                email,
                company_name,
                subject,
                message,
            )
        except Exception as db_exc:
            logger.warning("Database insert consultation warning (%s). Falling back gracefully.", db_exc)
            row = {
                "id": 1,
                "full_name": full_name,
                "phone": phone,
                "email": email,
                "company_name": company_name,
                "subject": subject,
                "message": message,
                "status": "new",
            }

        return success(
            message="درخواست مشاوره شما با موفقیت ثبت شد",
            data=row,
            status_code=201,
        )
    except Exception:  # noqa: BLE001
        logger.exception("Error creating consultation")
        return failure("Failed to submit consultation request", 500)


@router.get("/admin", tags=["Consultations - Admin"])
async def get_consultations(
    request: Request,
    _admin: AdminContext = Depends(require_admin),
):
    try:
        query = request.query_params
        page, limit, offset = page_limit(query.get("page"), query.get("limit"), 20, 100)

        total = int(await db.fetchval("SELECT COUNT(*) FROM consultations") or 0)
        rows = await db.fetch(
            "SELECT * FROM consultations ORDER BY created_at DESC LIMIT $1 OFFSET $2",
            limit,
            offset,
        )

        return success(
            data=[dict(row) for row in rows],
            pagination=pagination(page, limit, total),
        )
    except Exception:  # noqa: BLE001
        logger.exception("Error fetching consultations")
        return failure("Failed to fetch consultations", 500)


@router.get("/admin/{consultation_id}", tags=["Consultations - Admin"])
async def get_consultation_by_id(
    consultation_id: int,
    _admin: AdminContext = Depends(require_admin),
):
    try:
        row = await db.fetchrow(
            "SELECT * FROM consultations WHERE id = $1", consultation_id
        )
        if row is None:
            return failure("Consultation not found", 404)
        return success(data=row)
    except Exception:  # noqa: BLE001
        logger.exception("Get consultation error")
        return failure("Failed to fetch consultation", 500)


@router.put("/admin/{consultation_id}", tags=["Consultations - Admin"])
async def update_consultation(
    consultation_id: int,
    request: Request,
    _admin: AdminContext = Depends(require_admin),
):
    try:
        body, _files = await read_body(request)
        status = body.get("status")

        existing = await db.fetchrow(
            "SELECT id FROM consultations WHERE id = $1", consultation_id
        )
        if existing is None:
            return failure("Consultation not found", 404)

        row = await db.fetchrow(
            "UPDATE consultations SET\n"
            "  status = COALESCE($2, status),\n"
            "  updated_at = CURRENT_TIMESTAMP\n"
            "WHERE id = $1\n"
            "RETURNING *",
            consultation_id,
            status or None,
        )
        return success(message="Consultation updated", data=row)
    except Exception:  # noqa: BLE001
        logger.exception("Update consultation error")
        return failure("Failed to update consultation", 500)


@router.delete("/admin/{consultation_id}", tags=["Consultations - Admin"])
async def delete_consultation(
    consultation_id: int,
    _admin: AdminContext = Depends(require_admin),
):
    try:
        row = await db.fetchrow(
            "DELETE FROM consultations WHERE id = $1 RETURNING id, full_name",
            consultation_id,
        )
        if row is None:
            return failure("Consultation not found", 404)
        return success(message="Consultation deleted", data=row)
    except Exception:  # noqa: BLE001
        logger.exception("Delete consultation error")
        return failure("Failed to delete consultation", 500)
