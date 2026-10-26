"""
Two-factor authentication (TOTP) service using FusionAuth SDK.

Mirrors the C# UserManagementService 2FA methods.
"""

from __future__ import annotations

from typing import Any

from core.exceptions import FusionAuthAPIError
from Schema.Authentication.auth import TwoFactorDisableRequest, TwoFactorSetupRequest
from services.fusionauth_client import FusionAuthSDKClient, get_fusionauth_client


class TwoFactorService:

    def __init__(self, client: FusionAuthSDKClient | None = None) -> None:
        self._client = client or get_fusionauth_client()

    async def get_secret(self) -> dict[str, Any]:
        result = await self._client.generate_two_factor_secret()
        return {
            "secret": result.get("secret", ""),
            "secretBase32Encoded": result.get("secretBase32Encoded", ""),
        }

    async def enable(self, model: TwoFactorSetupRequest) -> dict[str, Any]:
        return await self._client.enable_two_factor(str(model.UserId), {
            "method": "authenticator",
            "secret": model.secret,
            "secretBase32Encoded": model.secretBase32Encoded,
            "code": model.code,
        })

    async def disable(self, model: TwoFactorDisableRequest) -> bool:
        await self._client.disable_two_factor(str(model.UserId), "authenticator", model.Code)
        return True

    async def get_status(self, user_id: str, application_id: str = "") -> dict[str, Any]:
        result = await self._client.retrieve_two_factor_status(user_id, application_id)
        return {
            "enabled": result.get("twoFactorEnabled", False),
            "methods": result.get("methods", []),
        }


_two_factor_service: TwoFactorService | None = None


def get_two_factor_service() -> TwoFactorService:
    global _two_factor_service
    if _two_factor_service is None:
        _two_factor_service = TwoFactorService()
    return _two_factor_service
