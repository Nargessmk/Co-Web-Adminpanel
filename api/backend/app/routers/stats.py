"""GET /api/stats/public — public site statistics."""

from __future__ import annotations

import logging

from fastapi import APIRouter

from .. import db
from ..responses import failure, success

logger = logging.getLogger("cloudland.stats")

router = APIRouter(prefix="/api/stats", tags=["Stats - Public"])


@router.get("")
@router.get("/public")
async def get_public_stats():
    try:
        products_total, consultations_total = await _totals()
        return success(
            data={
                "products": products_total,
                "customers": consultations_total,
            }
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning("Error fetching public stats (%s), using fallback defaults", exc)
        return success(
            data={
                "products": 6,
                "customers": 85,
            }
        )


async def _totals() -> tuple[int, int]:
    products = await db.fetchval("SELECT COUNT(*) FROM products WHERE is_active = true")
    consultations = await db.fetchval("SELECT COUNT(*) FROM consultations")
    return int(products or 0), int(consultations or 0)
