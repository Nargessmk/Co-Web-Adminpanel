"""GET /api/catalog-page + PUT /api/catalog-page/admin/settings.

The products page header (badge + title + description) and the headings and
button labels of a product's detail page, which has no header of its own.
Everything else on the two pages already lives in /api/products,
/api/categories, /api/catalogs and the product image/video endpoints.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, Request

from ..errors import ApiError
from ..helpers import read_body
from ..page_settings import read_settings, upsert_settings
from ..responses import failure, success
from ..security import AdminContext, require_admin

logger = logging.getLogger("cloudland.catalog_page")

router = APIRouter(prefix="/api/catalog-page", tags=["Catalog page"])

TABLE = "catalog_settings"
COLUMNS = [
    "page_badge", "page_title", "page_description",
    "all_category_label", "empty_title", "empty_text",
    "detail_catalogs_title", "detail_videos_title", "detail_gallery_title",
    "detail_description_title", "detail_related_title",
    "detail_site_label", "detail_consult_label", "detail_products_label",
]


@router.get("")
async def get_public():
    try:
        data = await read_settings(TABLE, COLUMNS)
        return success(data=data)
    except Exception:  # noqa: BLE001
        logger.exception("Get catalog page error")
        return failure("Failed to fetch catalog page", 500)


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
        logger.exception("Update catalog settings error")
        return failure("Failed to update catalog page settings", 500)
