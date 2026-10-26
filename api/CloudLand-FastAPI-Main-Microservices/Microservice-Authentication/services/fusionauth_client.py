"""
FusionAuth client wrapper using the official Python SDK.

This module wraps the official fusionauth-client SDK and provides async
methods for FastAPI. All FusionAuth calls go through this module.

Mirrors the C# IFusionAuthAsyncClient usage pattern.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from core.config import Settings, get_settings
from core.exceptions import (
    FusionAuthAPIError,
    FusionAuthConnectionError,
    FusionAuthNotFoundError,
)

logger = logging.getLogger(__name__)


def _check_response(response: Any, method_name: str) -> dict[str, Any]:
    """
    Check a FusionAuth SDK ClientResponse.

    Handles three cases like C#:
    - 200-299: success
    - 203, 242: valid FusionAuth responses (forced password change, 2FA required)
    - Others: error
    """
    status = response.status

    # Valid FusionAuth responses that are NOT in 200-299 range
    if status in (203, 242):
        return response.success_response or {}

    if not response.was_successful():
        error = response.error_response
        if status == 404:
            raise FusionAuthNotFoundError(
                "Resource not found in FusionAuth",
                status_code=404,
                details=error,
            )
        raise FusionAuthAPIError(
            f"FusionAuth {method_name} failed with status {status}",
            status_code=status,
            details=error,
        )

    return response.success_response or {}


class FusionAuthSDKClient:
    """
    Async wrapper around the official FusionAuth Python SDK.
    Tenant ID is set dynamically per-request when needed.
    """

    def __init__(self, settings: Settings) -> None:
        from fusionauth.fusionauth_client import FusionAuthClient
        self._settings = settings
        self._client = FusionAuthClient(
            settings.fusionauth_api_key,
            settings.fusionauth_base_url,
        )

    def _set_tenant(self, tenant_id: str) -> None:
        """Set tenant header for operations that require it."""
        if tenant_id:
            self._client.set_tenant_id(tenant_id)

    def _clear_tenant(self) -> None:
        """Remove tenant header."""
        self._client.set_tenant_id(None)

    # ------------------------------------------------------------------
    # Authentication
    # ------------------------------------------------------------------

    async def login(self, request: dict[str, Any]) -> dict[str, Any]:
        """POST /api/login — Authenticate user."""
        resp = await asyncio.to_thread(self._client.login, request)
        return _check_response(resp, "login")

    async def logout(self, global_logout: bool, refresh_token: str | None = None) -> dict[str, Any]:
        """POST /api/logout — Invalidate refresh token(s)."""
        resp = await asyncio.to_thread(self._client.logout, global_logout, refresh_token)
        return _check_response(resp, "logout")

    async def forgot_password(self, request: dict[str, Any]) -> dict[str, Any]:
        """POST /api/user/forgot-password — Send reset email or get changePasswordId."""
        resp = await asyncio.to_thread(self._client.forgot_password, request)
        return _check_response(resp, "forgot_password")

    async def change_password(self, change_password_id: str, request: dict[str, Any]) -> dict[str, Any]:
        """POST /api/user/change-password/{id} — Change password with token."""
        resp = await asyncio.to_thread(self._client.change_password, change_password_id, request)
        return _check_response(resp, "change_password")

    # ------------------------------------------------------------------
    # User CRUD
    # ------------------------------------------------------------------

    async def create_user(self, request: dict[str, Any], user_id: str | None = None) -> dict[str, Any]:
        """POST /api/user — Create a new user."""
        resp = await asyncio.to_thread(self._client.create_user, request, user_id)
        return _check_response(resp, "create_user")

    async def retrieve_user(self, user_id: str) -> dict[str, Any]:
        """GET /api/user/{user_id} — Retrieve user by ID."""
        resp = await asyncio.to_thread(self._client.retrieve_user, user_id)
        return _check_response(resp, "retrieve_user")

    async def retrieve_user_by_email(self, email: str) -> dict[str, Any]:
        """GET /api/user?email={email} — Retrieve user by email."""
        resp = await asyncio.to_thread(self._client.retrieve_user_by_email, email)
        return _check_response(resp, "retrieve_user_by_email")

    async def update_user(self, user_id: str, request: dict[str, Any]) -> dict[str, Any]:
        """PUT /api/user/{user_id} — Update user fields."""
        resp = await asyncio.to_thread(self._client.update_user, user_id, request)
        return _check_response(resp, "update_user")

    async def delete_user(self, user_id: str) -> dict[str, Any]:
        """DELETE /api/user/{user_id} — Hard delete user."""
        resp = await asyncio.to_thread(self._client.delete_user, user_id)
        return _check_response(resp, "delete_user")

    async def deactivate_user(self, user_id: str) -> dict[str, Any]:
        """DELETE /api/user/{user_id} — Soft deactivate user."""
        resp = await asyncio.to_thread(self._client.deactivate_user, user_id)
        return _check_response(resp, "deactivate_user")

    async def reactivate_user(self, user_id: str) -> dict[str, Any]:
        """PUT /api/user/{user_id}?reactivate=true — Reactivate user."""
        resp = await asyncio.to_thread(self._client.reactivate_user, user_id)
        return _check_response(resp, "reactivate_user")

    async def search_users_by_query(self, request: dict[str, Any]) -> dict[str, Any]:
        """POST /api/user/search — Search users with query. Wraps in 'search' key for SDK."""
        wrapped = {"search": request}
        resp = await asyncio.to_thread(self._client.search_users_by_query, wrapped)
        return _check_response(resp, "search_users_by_query")

    async def search_users_by_ids(self, ids: list[str]) -> dict[str, Any]:
        """GET /api/user/search?ids=... — Search users by IDs."""
        resp = await asyncio.to_thread(self._client.search_users_by_ids, ids)
        return _check_response(resp, "search_users_by_ids")

    # ------------------------------------------------------------------
    # User registration to application
    # ------------------------------------------------------------------

    async def register(self, request: dict[str, Any], user_id: str | None = None) -> dict[str, Any]:
        """POST /api/user/registration/{user_id} — Register user to application."""
        resp = await asyncio.to_thread(self._client.register, request, user_id)
        return _check_response(resp, "register")

    async def update_registration(self, user_id: str, request: dict[str, Any]) -> dict[str, Any]:
        """PUT /api/user/registration/{user_id} — Update registration."""
        resp = await asyncio.to_thread(self._client.update_registration, user_id, request)
        return _check_response(resp, "update_registration")

    async def delete_registration(self, user_id: str, application_id: str) -> dict[str, Any]:
        """DELETE /api/user/registration/{user_id}/{application_id}"""
        resp = await asyncio.to_thread(self._client.delete_registration, user_id, application_id)
        return _check_response(resp, "delete_registration")

    # ------------------------------------------------------------------
    # Application CRUD
    # ------------------------------------------------------------------

    async def retrieve_applications(self) -> dict[str, Any]:
        """GET /api/application — List all applications."""
        resp = await asyncio.to_thread(self._client.retrieve_applications)
        return _check_response(resp, "retrieve_applications")

    async def retrieve_application(self, application_id: str) -> dict[str, Any]:
        """GET /api/application/{application_id}"""
        resp = await asyncio.to_thread(self._client.retrieve_application, application_id)
        return _check_response(resp, "retrieve_application")

    async def create_application(self, request: dict[str, Any], application_id: str | None = None, tenant_id: str = "") -> dict[str, Any]:
        """POST /api/application"""
        if tenant_id:
            self._set_tenant(tenant_id)
        resp = await asyncio.to_thread(self._client.create_application, request, application_id)
        if tenant_id:
            self._clear_tenant()
        return _check_response(resp, "create_application")

    async def update_application(self, application_id: str, request: dict[str, Any]) -> dict[str, Any]:
        """PUT /api/application/{application_id}"""
        resp = await asyncio.to_thread(self._client.update_application, application_id, request)
        return _check_response(resp, "update_application")

    async def delete_application(self, application_id: str) -> dict[str, Any]:
        """DELETE /api/application/{application_id}"""
        resp = await asyncio.to_thread(self._client.delete_application, application_id)
        return _check_response(resp, "delete_application")

    async def deactivate_application(self, application_id: str) -> dict[str, Any]:
        """POST /api/application/{id}/deactivate"""
        resp = await asyncio.to_thread(self._client.deactivate_application, application_id)
        return _check_response(resp, "deactivate_application")

    async def reactivate_application(self, application_id: str) -> dict[str, Any]:
        """POST /api/application/{id}/reactivate"""
        resp = await asyncio.to_thread(self._client.reactivate_application, application_id)
        return _check_response(resp, "reactivate_application")

    # ------------------------------------------------------------------
    # Application roles
    # ------------------------------------------------------------------

    async def create_application_role(self, application_id: str, request: dict[str, Any], role_id: str | None = None) -> dict[str, Any]:
        """POST /api/application/{app_id}/role/{role_id}"""
        resp = await asyncio.to_thread(self._client.create_application_role, application_id, request, role_id)
        return _check_response(resp, "create_application_role")

    async def update_application_role(self, application_id: str, role_id: str, request: dict[str, Any]) -> dict[str, Any]:
        """PUT /api/application/{app_id}/role/{role_id}"""
        resp = await asyncio.to_thread(self._client.update_application_role, application_id, role_id, request)
        return _check_response(resp, "update_application_role")

    async def delete_application_role(self, application_id: str, role_id: str) -> dict[str, Any]:
        """DELETE /api/application/{app_id}/role/{role_id}"""
        resp = await asyncio.to_thread(self._client.delete_application_role, application_id, role_id)
        return _check_response(resp, "delete_application_role")

    # ------------------------------------------------------------------
    # Groups
    # ------------------------------------------------------------------

    async def retrieve_groups(self) -> dict[str, Any]:
        """GET /api/group"""
        resp = await asyncio.to_thread(self._client.retrieve_groups)
        return _check_response(resp, "retrieve_groups")

    async def create_group(self, request: dict[str, Any], group_id: str | None = None, tenant_id: str = "") -> dict[str, Any]:
        """POST /api/group"""
        if tenant_id:
            self._set_tenant(tenant_id)
        resp = await asyncio.to_thread(self._client.create_group, request, group_id)
        if tenant_id:
            self._clear_tenant()
        return _check_response(resp, "create_group")

    async def update_group(self, group_id: str, request: dict[str, Any]) -> dict[str, Any]:
        """PUT /api/group/{group_id}"""
        resp = await asyncio.to_thread(self._client.update_group, group_id, request)
        return _check_response(resp, "update_group")

    async def delete_group(self, group_id: str) -> dict[str, Any]:
        """DELETE /api/group/{group_id}"""
        resp = await asyncio.to_thread(self._client.delete_group, group_id)
        return _check_response(resp, "delete_group")

    # ------------------------------------------------------------------
    # Two-factor
    # ------------------------------------------------------------------

    async def generate_two_factor_secret(self) -> dict[str, Any]:
        """POST /api/two-factor/secret"""
        resp = await asyncio.to_thread(self._client.generate_two_factor_secret)
        return _check_response(resp, "generate_two_factor_secret")

    async def enable_two_factor(self, user_id: str, request: dict[str, Any]) -> dict[str, Any]:
        """POST /api/user/{user_id}/two-factor-enable"""
        resp = await asyncio.to_thread(self._client.enable_two_factor, user_id, request)
        return _check_response(resp, "enable_two_factor")

    async def disable_two_factor(self, user_id: str, method: str, code: str) -> dict[str, Any]:
        """POST /api/user/{user_id}/two-factor-disable"""
        resp = await asyncio.to_thread(self._client.disable_two_factor, user_id, method, code)
        return _check_response(resp, "disable_two_factor")

    async def two_factor_login(self, request: dict[str, Any]) -> dict[str, Any]:
        """POST /api/two-factor/login"""
        resp = await asyncio.to_thread(self._client.two_factor_login, request)
        return _check_response(resp, "two_factor_login")

    async def retrieve_two_factor_status(self, user_id: str, application_id: str = "", two_factor_trust_id: str = "") -> dict[str, Any]:
        """GET /api/user/{user_id}/two-factor-status"""
        resp = await asyncio.to_thread(self._client.retrieve_two_factor_status, user_id, application_id, two_factor_trust_id)
        return _check_response(resp, "retrieve_two_factor_status")

    # ------------------------------------------------------------------
    # Health check
    # ------------------------------------------------------------------

    async def health_check(self) -> bool:
        """Verify FusionAuth is reachable."""
        try:
            resp = await asyncio.to_thread(self._client.retrieve_system_health)
            return resp.was_successful()
        except Exception as exc:
            logger.warning("FusionAuth health check failed: %s", exc)
            return False


# ---------------------------------------------------------------------------
# Singleton management
# ---------------------------------------------------------------------------

_fusionauth_client: FusionAuthSDKClient | None = None


def get_fusionauth_client() -> FusionAuthSDKClient:
    global _fusionauth_client
    if _fusionauth_client is None:
        _fusionauth_client = FusionAuthSDKClient(get_settings())
    return _fusionauth_client


async def close_fusionauth_client() -> None:
    global _fusionauth_client
    _fusionauth_client = None
