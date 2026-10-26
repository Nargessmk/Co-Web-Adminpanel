"""
Profile image upload service using FusionAuth SDK.

Validates file type/size, saves to disk, and updates FusionAuth user record.
Mirrors the C# UserManagementService.UploadUserProfile method.
"""

from __future__ import annotations

import logging
import uuid
from pathlib import Path
from typing import Any

from core.config import Settings, get_settings
from services.fusionauth_client import FusionAuthSDKClient, get_fusionauth_client

logger = logging.getLogger(__name__)

MAGIC_BYTES = {
    ".jpg": b"\xff\xd8\xff",
    ".jpeg": b"\xff\xd8\xff",
    ".png": b"\x89PNG",
    ".gif": b"GIF",
}


class FileUploadService:

    def __init__(
        self,
        client: FusionAuthSDKClient | None = None,
        settings: Settings | None = None,
    ) -> None:
        self._client = client or get_fusionauth_client()
        self._settings = settings or get_settings()
        self._allowed_extensions = set(self._settings.upload_allowed_extensions.split(","))
        self._max_bytes = self._settings.upload_max_file_size_mb * 1024 * 1024
        self._upload_dir = Path(self._settings.upload_path)
        self._upload_dir.mkdir(parents=True, exist_ok=True)

    async def upload_profile_image(self, user_id: str, filename: str, content: bytes) -> dict[str, Any]:
        ext = Path(filename).suffix.lower()
        if ext not in self._allowed_extensions:
            return {"success": False, "error": f"Invalid file type. Allowed: {', '.join(self._allowed_extensions)}"}

        if len(content) > self._max_bytes:
            return {"success": False, "error": f"File too large. Max: {self._settings.upload_max_file_size_mb}MB"}

        if not self._validate_magic_bytes(content, ext):
            return {"success": False, "error": "File content does not match its extension"}

        safe_name = f"{uuid.uuid4().hex}{ext}"
        file_path = self._upload_dir / safe_name
        file_path.write_bytes(content)

        image_url = f"{self._settings.upload_base_url}/{safe_name}"

        try:
            await self._client.update_user(user_id, {"user": {"imageUrl": image_url}})
        except Exception:
            file_path.unlink(missing_ok=True)
            return {"success": False, "error": "Failed to update user profile"}

        return {"success": True, "imageUrl": image_url}

    async def delete_profile_image(self, user_id: str) -> bool:
        try:
            user_data = await self._client.retrieve_user(user_id)
            user = user_data.get("user", {})
            image_url = user.get("imageUrl")
            if image_url:
                filename = Path(image_url).name
                (self._upload_dir / filename).unlink(missing_ok=True)

            await self._client.update_user(user_id, {"user": {"imageUrl": None}})
            return True
        except Exception:
            return False

    @staticmethod
    def _validate_magic_bytes(content: bytes, ext: str) -> bool:
        expected = MAGIC_BYTES.get(ext)
        if not expected:
            return False
        return content[:len(expected)] == expected


_file_upload_service: FileUploadService | None = None


def get_file_upload_service() -> FileUploadService:
    global _file_upload_service
    if _file_upload_service is None:
        _file_upload_service = FileUploadService()
    return _file_upload_service
