"""Storage helper.

The single place where the backend talks to the Storage microservice, which in
turn stores files in MinIO (S3). Ported one-to-one from the old
``services/storageService.js``.

Flow::

    browser -> backend (in memory) -> Storage microservice
            -> MinIO bucket        -> object key stored in Postgres

Only the object key (``products/abc.png``) is stored in Postgres — never the
host. The public URL is rebuilt on the way out, so moving the bucket to another
domain or endpoint does not invalidate a single row.

Configuration (see api/backend/.env):
  STORAGE_SERVICE_URL      base URL of the Storage microservice
  STORAGE_BACKEND          "minio" (default) or "local"
  STORAGE_FALLBACK_LOCAL   "true" (default) => write to disk when the
                           microservice is unreachable instead of failing
  S3_PUBLIC_BASE           public base URL of MinIO (changes are safe: it is
                           never written to the database)
  S3_BUCKET                bucket name (default: cloudland)
"""

from __future__ import annotations

import logging
import random
import time
from pathlib import Path
from typing import Any, Optional
from urllib.parse import quote

import httpx

from . import config
from .errors import StorageError

logger = logging.getLogger("cloudland.storage")

ALLOWED_TYPES: dict[str, str] = {
    "image/jpeg": "jpg",
    "image/jpg": "jpg",
    "image/png": "png",
    "image/gif": "gif",
    "image/webp": "webp",
    "image/svg+xml": "svg",
    "application/pdf": "pdf",
    "application/msword": "doc",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
    "application/vnd.ms-excel": "xls",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "xlsx",
    "application/vnd.ms-powerpoint": "ppt",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation": "pptx",
    "text/csv": "csv",
    "application/zip": "zip",
    "video/mp4": "mp4",
    "video/webm": "webm",
    "video/ogg": "ogg",
    "video/quicktime": "mov",
    "video/3gpp": "3gpp",
    "video/x-msvideo": "avi",
    "video/x-m4v": "m4v",
}

ALLOWED_TYPES_MESSAGE = (
    "File type not allowed. Allowed: jpg, jpeg, png, gif, webp, svg, pdf, doc, "
    "docx, xls, xlsx, ppt, pptx, csv, zip, mp4, webm, ogg, mov, 3gpp, avi, m4v"
)

# The response columns that hold a stored file. Only these are turned from an
# object key into a URL on the way out; every other URL-ish column (a product
# link, a GitHub profile, a resume written as text) is passed through as typed.
FILE_KEY_COLUMNS = frozenset(
    {
        "image",
        "image_url",
        "video_url",
        "file_url",
        "logo_url",
        "avatar",
        "thumbnail_url",
        "cover_url",
    }
)

# Joined queries alias a related row's file, e.g. `p.image_url AS
# product_image_url` or `t.image_url AS author_image_url`. Those carry object
# keys exactly like `image_url` does, so match the suffix too — otherwise the
# related product or author avatar renders as a broken relative path.
FILE_KEY_SUFFIXES = ("_image", "_image_url", "_video_url", "_file_url", "_logo_url", "_avatar")


def is_file_key_column(key: str) -> bool:
    """True for a response column whose value is a stored file."""
    return key in FILE_KEY_COLUMNS or key.endswith(FILE_KEY_SUFFIXES)


def extension_for(originalname: Optional[str], mimetype: Optional[str]) -> str:
    if mimetype and mimetype in ALLOWED_TYPES:
        return ALLOWED_TYPES[mimetype]
    parts = (originalname or "").rsplit(".", 1)
    name = parts[-1] if len(parts) == 2 else ""
    return name if name and len(name) <= 5 else "bin"


def save_to_disk(
    buffer: bytes,
    folder: Optional[str],
    originalname: Optional[str],
    mimetype: Optional[str],
) -> dict[str, Any]:
    """Save a buffer under ``uploads/<folder>`` (local mode + safety fallback)."""
    clean_folder = "".join(ch for ch in (folder or "uploads") if ch.isalnum() or ch in "_-")
    clean_folder = clean_folder or "uploads"

    directory = Path(config.UPLOADS_DIR) / clean_folder
    directory.mkdir(parents=True, exist_ok=True)

    filename = (
        f"{clean_folder}-{int(time.time() * 1000)}-"
        f"{random.randint(0, 999_999_999)}.{extension_for(originalname, mimetype)}"
    )
    (directory / filename).write_bytes(buffer)

    return {
        "url": f"/uploads/{clean_folder}/{filename}",
        # A local file has no bucket, so it has no object key: the path above is
        # already the address the browser uses.
        "key": None,
        "source": "local",
        "storage_path": None,
        "object_name": None,
    }


def _is_object_key(value: Any) -> bool:
    """True for a stored object key such as ``products/abc.png``.

    A key never has a scheme, never starts with a slash and always has a
    folder in front of the file name. Those three rules tell it apart from
    everything else a URL-ish column can hold (absolute URLs, ``/uploads/...``
    disk paths, page links).
    """
    if not isinstance(value, str) or not value or len(value) > 512:
        return False
    if value.startswith(("http://", "https://", "/")):
        return False
    folder, _, name = value.partition("/")
    return bool(folder) and bool(name) and " " not in value


def public_url(value: Optional[str]) -> Optional[str]:
    """The URL a browser should fetch, for a value read out of the database.

    Object keys are expanded against ``S3_PUBLIC_BASE``; anything else (an
    absolute URL, a legacy ``/uploads/...`` path, a page link, NULL) is handed
    back untouched. Because the host only ever appears here, moving the bucket
    to another domain is a one-line change in the environment.
    """
    if _is_object_key(value):
        return f"{config.S3_PUBLIC_BASE}/{config.S3_BUCKET}/{value}"
    return value


def expand_file_keys(payload: Any) -> Any:
    """Recursively turn every stored object key in a response into its URL.

    Applied once, to the whole answer, on the way out — so no router has to
    remember which of its columns hold files.
    """
    if isinstance(payload, list):
        return [expand_file_keys(item) for item in payload]
    if not isinstance(payload, dict):
        return payload
    return {
        key: public_url(value) if is_file_key_column(key) else expand_file_keys(value)
        for key, value in payload.items()
    }


def to_object_key(value: Optional[str]) -> Optional[str]:
    """Normalise a value a client sent back into what the database stores.

    The admin forms always hand back the URL the API gave them, so an old row
    (absolute URL) that is saved again must not smuggle the host back into
    Postgres.
    """
    if not isinstance(value, str) or not value:
        return value
    if _is_object_key(value):
        return value
    if not value.lower().startswith(("http://", "https://")):
        return value
    return object_key_of(value) or value


def stored_value(stored: Optional[dict[str, Any]]) -> Optional[str]:
    """What a write must persist for a file that was just uploaded.

    MinIO files become their object key; a local fallback has no key, so its
    ``/uploads/...`` path — already a servable address — is stored as is.
    """
    if not stored:
        return None
    return stored.get("key") or stored.get("url")


def object_key_of(value: Optional[str]) -> Optional[str]:
    """The key behind one of our public URLs, or None when it is not ours.

    Only a URL served by ``S3_PUBLIC_BASE`` for ``S3_BUCKET`` is unwrapped. A
    link an admin typed by hand (a GitHub profile, a document on another host)
    is not ours and is never touched, so it cannot lose its first path segment.
    """
    if not isinstance(value, str) or not value.lower().startswith(("http://", "https://")):
        return None
    without_scheme = value.split("://", 1)[1]
    host, _, without_host = without_scheme.partition("/")
    if not _is_our_host(host):
        return None
    if "/" not in without_host:
        return None
    bucket, _, object_name = without_host.partition("/")
    if bucket != config.S3_BUCKET:
        return None
    return object_name or None


def _is_our_host(host: str) -> bool:
    """True when ``host`` is the public host of the bucket we write to."""
    if not host:
        return False
    base = config.S3_PUBLIC_BASE.split("://", 1)[-1].split("/", 1)[0].lower()
    return host.lower() == base


def _split_location(value: Optional[str]) -> tuple[str, str]:
    """``(bucket, object)`` for a stored key or for a full URL. Never raises."""
    if _is_object_key(value):
        return config.S3_BUCKET, value
    if not isinstance(value, str) or not value.lower().startswith(("http://", "https://")):
        return "", ""
    without_scheme = value.split("://", 1)[1]
    if "/" not in without_scheme:
        return "", ""
    without_host = without_scheme.split("/", 1)[1]
    if "/" not in without_host:
        return "", ""
    bucket, _, object_name = without_host.partition("/")
    return bucket, object_name


def _storage_timeout() -> httpx.Timeout:
    return httpx.Timeout(config.STORAGE_UPLOAD_TIMEOUT_MS / 1000)


def _fallback_or_raise(
    error: StorageError,
    buffer: bytes,
    folder: Optional[str],
    originalname: Optional[str],
    mimetype: Optional[str],
) -> dict[str, Any]:
    logger.error("[storage] MinIO upload failed (%s)", error.message)
    if not config.STORAGE_FALLBACK_LOCAL:
        raise error
    logger.warning(
        "[storage] STORAGE_FALLBACK_LOCAL=true -> saving file to disk instead of MinIO"
    )
    return save_to_disk(buffer, folder, originalname, mimetype)


async def upload_file(
    buffer: bytes,
    originalname: Optional[str],
    mimetype: Optional[str],
    folder: str,
    token: Optional[str] = None,
    title: Optional[str] = None,
    record_id: Optional[Any] = None,
) -> dict[str, Any]:
    """Upload one file to the Storage microservice -> MinIO."""
    if config.STORAGE_BACKEND == "local":
        return save_to_disk(buffer, folder, originalname, mimetype)

    url = f"{config.STORAGE_SERVICE_URL}/api/v1/buckets-objects/file-uploader"
    files = {
        "file": (originalname or "file", buffer, mimetype or "application/octet-stream")
    }
    data: dict[str, str] = {"FolderName": folder}
    if title:
        data["Title"] = str(title)
    if record_id is not None:
        data["RecordId"] = str(record_id)
    # NOTE: ApplicationId is intentionally NOT sent — the Storage microservice
    # derives the tenant from the JWT; a mismatching value would return 403.
    headers = {"Authorization": f"Bearer {token}"} if token else {}

    try:
        async with httpx.AsyncClient(timeout=_storage_timeout()) as client:
            response = await client.post(url, data=data, files=files, headers=headers)

        try:
            payload = response.json()
        except ValueError as exc:
            raise StorageError(
                f"Storage returned non-JSON response (HTTP {response.status_code}): "
                f"{response.text[:200]}"
            ) from exc

        if response.status_code >= 400 or payload.get("success") is False:
            raise StorageError(
                payload.get("error_message")
                or payload.get("detail")
                or f"Storage upload failed (HTTP {response.status_code})"
            )

        # The Storage microservice serializes with PascalCase aliases
        # (ObjectName, DirectUrl, ...) — accept both styles.
        object_name = (
            payload.get("object_name")
            or payload.get("ObjectName")
            or payload.get("file_identifier")
            or payload.get("FileIdentifier")
        )
        bucket = payload.get("bucket_name") or payload.get("BucketName") or config.S3_BUCKET
        direct_url = (
            payload.get("direct_url")
            or payload.get("DirectUrl")
            or (f"{config.S3_PUBLIC_BASE}/{bucket}/{object_name}" if object_name else None)
        )

        if not direct_url:
            raise StorageError("Storage response did not contain a usable file URL")

        return {
            "url": direct_url,
            # What the database stores. Callers persist this, never "url".
            "key": object_name,
            "source": "minio",
            "storage_path": payload.get("storage_path")
            or payload.get("StoragePath")
            or (f"{bucket}/{object_name}" if object_name else None),
            "object_name": object_name,
            "bucket": bucket,
            "presigned_url": payload.get("presigned_url") or payload.get("PresignedUrl"),
        }
    except StorageError as error:
        return _fallback_or_raise(error, buffer, folder, originalname, mimetype)
    except httpx.HTTPError as error:
        return _fallback_or_raise(
            StorageError(str(error)), buffer, folder, originalname, mimetype
        )


async def delete_file(
    stored_url: Optional[str],
    token: Optional[str],
    application_id: Optional[str],
) -> bool:
    """Best-effort delete of an object from MinIO. Never raises.

    Accepts either an object key (``products/abc.png``) or a full public URL,
    so a row that still holds a legacy absolute URL is still cleaned up.
    """
    bucket_name, object_name = _split_location(stored_url)
    if not object_name:
        return False  # legacy/local file
    if not token or not application_id:
        logger.warning("[storage] skipping MinIO delete: missing token or application_id")
        return False

    try:
        url = (
            f"{config.STORAGE_SERVICE_URL}/api/v1/buckets-objects/delete-object"
            f"?application_id={quote(str(application_id), safe='')}"
            f"&bucketName={quote(bucket_name, safe='')}"
            f"&objectName={quote(object_name, safe='')}"
        )

        async with httpx.AsyncClient(timeout=_storage_timeout()) as client:
            response = await client.delete(url, headers={"Authorization": f"Bearer {token}"})

        if response.status_code >= 400:
            logger.warning(
                "[storage] MinIO delete returned HTTP %s for %s/%s",
                response.status_code,
                bucket_name,
                object_name,
            )
            return False
        return True
    except Exception as error:  # noqa: BLE001 — cleanup must never break the request
        logger.warning("[storage] MinIO delete failed: %s", error)
        return False


async def remove_stored_file(
    stored_url: Optional[str],
    token: Optional[str],
    application_id: Optional[str],
) -> None:
    """Remove a stored file wherever it lives (MinIO object or legacy disk file)."""
    if not stored_url:
        return
    if stored_url.lower().startswith(("http://", "https://")):
        await delete_file(stored_url, token, application_id)
        return
    if stored_url.startswith("/uploads/"):
        target = Path(config.UPLOADS_DIR) / stored_url[len("/uploads/"):]
        try:
            target.unlink(missing_ok=True)
        except OSError:
            pass


__all__ = [
    "ALLOWED_TYPES",
    "ALLOWED_TYPES_MESSAGE",
    "extension_for",
    "save_to_disk",
    "upload_file",
    "delete_file",
    "remove_stored_file",
]
