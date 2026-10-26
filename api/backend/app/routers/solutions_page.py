"""GET /api/solutions-page + PUT /api/solutions-page/admin/settings.

The "راهکارها" page header (badge + title + description) and the eyebrow,
block labels and action buttons of an article's detail page. The article grid
itself already lives in /api/solutions.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, Request

from ..errors import ApiError
from ..helpers import read_body
from ..page_settings import read_settings, upsert_settings
from ..responses import failure, success
from ..security import AdminContext, require_admin

logger = logging.getLogger("cloudland.solutions_page")

router = APIRouter(prefix="/api/solutions-page", tags=["Solutions page"])

TABLE = "solution_settings"
COLUMNS = [
    "page_badge", "page_title", "page_description",
    "empty_title", "empty_text",
    "detail_eyebrow", "detail_source_label", "detail_related_label",
    "detail_author_label", "detail_author_link_label",
    "detail_others_label", "detail_consult_label",
]


@router.get("")
async def get_public():
    try:
        data = await read_settings(TABLE, COLUMNS)
        return success(data=data)
    except Exception:  # noqa: BLE001
        logger.exception("Get solution page error")
        return failure("Failed to fetch solution page", 500)


@router.put("/admin/settings")
async def update_settings(
    request: Request,
    _admin: AdminContext = Depends(require_admin),
):
    try:
        body, _files = await read_body(request)
        row = await upsert_settings(TABLE, COLUMNS, body)
        return success(data=row)
    except ApiError as error:
        return failure(error.message, error.status_code)
    except Exception:  # noqa: BLE001
        logger.exception("Update solution settings error")
        return failure("Failed to update solution page settings", 500)
