"""POST /api/upload/product + /api/upload/category.

Stores one uploaded file in MinIO through the Storage microservice and returns
its public URL, falling back to the local disk when configured to do so.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, Request

from pathlib import Path
from .. import config, db, storage
from ..errors import ApiError, StorageError
from ..helpers import extract_file, read_body
from ..responses import failure, success
from ..security import AdminContext, require_admin

logger = logging.getLogger("cloudland.uploads")

router = APIRouter(prefix="/api/upload", tags=["Upload"])


async def _store(request: Request, folder: str, admin: AdminContext) -> str:
    _fields, files = await read_body(request)
    upload = await extract_file(files, "file")
    if upload is None:
        raise ApiError(400, "No file uploaded or invalid file type")

    stored = await storage.upload_file(
        buffer=upload.buffer,
        originalname=upload.originalname,
        mimetype=upload.mimetype,
        folder=folder,
        token=admin.token,
    )
    logger.info("[upload] %s file stored via %s: %s", folder, stored["source"], stored["url"])
    file_url = storage.stored_value(stored)

    try:
        from .media import detect_file_type
        await db.execute(
            """
            INSERT INTO media_files (
                filename, original_name, file_url, file_type, mimetype, file_size, folder
            ) VALUES ($1, $2, $3, $4, $5, $6, $7)
            ON CONFLICT (file_url) DO NOTHING
            """,
            Path(file_url).name if file_url else upload.originalname,
            upload.originalname,
            file_url,
            detect_file_type(upload.mimetype, upload.originalname),
            upload.mimetype,
            len(upload.buffer),
            folder,
        )
    except Exception as exc:
        logger.debug("[upload] Could not log to media_files: %s", exc)

    return file_url


@router.post("/product")
async def upload_product_file(
    request: Request,
    admin: AdminContext = Depends(require_admin),
):
    try:
        url = await _store(request, "products", admin)
        return success(message="File uploaded", data={"url": url})
    except ApiError as error:
        return failure(error.message, error.status_code)
    except StorageError as error:
        return failure(error.message, 500)
    except Exception as error:  # noqa: BLE001
        logger.exception("Upload product file error")
        return failure(str(error) or "Upload failed", 500)


@router.post("/category")
async def upload_category_file(
    request: Request,
    admin: AdminContext = Depends(require_admin),
):
    try:
        url = await _store(request, "categories", admin)
        return success(message="File uploaded", data={"url": url})
    except ApiError as error:
        return failure(error.message, error.status_code)
    except StorageError as error:
        return failure(error.message, 500)
    except Exception as error:  # noqa: BLE001
        logger.exception("Upload category file error")
        return failure(str(error) or "Upload failed", 500)


@router.post("/image")
@router.post("/general")
async def upload_general_image(
    request: Request,
    admin: AdminContext = Depends(require_admin),
):
    try:
        url = await _store(request, "general", admin)
        return success(message="Image uploaded successfully", data={"url": url})
    except ApiError as error:
        return failure(error.message, error.status_code)
    except StorageError as error:
        return failure(error.message, 500)
    except Exception as error:  # noqa: BLE001
        logger.exception("Upload general image error")
        return failure(str(error) or "Upload failed", 500)
