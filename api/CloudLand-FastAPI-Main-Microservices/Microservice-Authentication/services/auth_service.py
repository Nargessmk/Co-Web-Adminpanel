"""
Authentication business logic using the official FusionAuth SDK.

All FusionAuth interactions go through the SDK-based FusionAuthSDKClient.
Issues own JWTs via core.security for multi-tenant access control.

Mirrors the C# AuthController + JWTService + parts of UserManagementService.
"""

from __future__ import annotations

import secrets
import string
from typing import Any

from core.config import Settings, get_settings
from core.exceptions import FusionAuthAPIError, FusionAuthNotFoundError
from core.security import (
    InvalidTokenError,
    TokenType,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from Schema.Authentication.auth import (
    ChangePasswordWithTokenRequest,
    ForgotPasswordRequest,
    LoginRequest,
    ResolveApplicationRequest,
    SecurityQuestionsRequest,
    TwoFactorLoginRequest,
)
from services.fusionauth_client import FusionAuthSDKClient, get_fusionauth_client


class AuthService:
    """Encapsulates all authentication flows backed by FusionAuth SDK."""

    def __init__(
        self,
        client: FusionAuthSDKClient | None = None,
        settings: Settings | None = None,
    ) -> None:
        self._client = client or get_fusionauth_client()
        self._settings = settings or get_settings()

    # ------------------------------------------------------------------
    # Login
    # ------------------------------------------------------------------

    async def login(
        self,
        model: LoginRequest,
        ip_address: str | None = None,
    ) -> dict[str, Any]:
        """
        Authenticate a user via FusionAuth SDK.

        Handles response codes:
        - 200: success — mints own JWT
        - 203: forced password change — returns changePasswordId
        - 242: two-factor required — returns twoFactorId
        """
        body: dict[str, Any] = {
            "loginId": model.userName,
            "password": model.password,
            "applicationId": model.applicationId,
            "noJWT": True,
        }
        if ip_address:
            body["ipAddress"] = ip_address

        result = await self._client.login(body)

        # --- Forced password change (203) ---
        if result.get("changePasswordId"):
            return {
                "statusCode": 203,
                "changePasswordId": result["changePasswordId"],
                "loginId": model.userName,
                "applicationId": model.applicationId,
            }

        # --- Two-factor challenge (242) ---
        if result.get("twoFactorId"):
            return {
                "statusCode": 242,
                "twoFactorId": result["twoFactorId"],
                "applicationId": model.applicationId,
            }

        # --- Successful login ---
        user = result.get("user", {})
        roles = self._extract_roles(user, model.applicationId)

        access_token = create_access_token(
            user_id=user.get("id", ""),
            application_id=model.applicationId,
            roles=roles,
            settings=self._settings,
        )
        refresh_token = create_refresh_token(
            user_id=user.get("id", ""),
            application_id=model.applicationId,
            settings=self._settings,
        )

        return {
            "statusCode": 202,
            "accessToken": access_token,
            "refreshToken": refresh_token,
            "tokenType": "Bearer",
            "expiresIn": self._settings.access_token_expire_minutes * 60,
            "userId": user.get("id", ""),
            "applicationId": model.applicationId,
            "userName": user.get("username", model.userName).lower(),
            "roles": roles,
            "user": user,
        }

    # ------------------------------------------------------------------
    # Resolve application from credentials
    # ------------------------------------------------------------------

    async def resolve_application(
        self,
        model: ResolveApplicationRequest,
    ) -> dict[str, Any]:
        """
        Find which application a user belongs to based on username + password.

        Since the same username can exist in multiple applications with
        different passwords, we search for the user, collect all applicationIds
        from their registrations, and try login with each one until the
        password matches.
        """
        search_result = await self._client.search_users_by_query({
            "queryString": f'username:"{model.userName}"',
            "startRow": 0,
            "numberOfResults": 50,
        })

        users = search_result.get("users", [])
        if not users:
            raise FusionAuthAPIError("User not found", status_code=404)

        user = users[0]
        registrations = user.get("registrations", [])

        if not registrations:
            raise FusionAuthAPIError("User has no application registrations", status_code=404)

        for reg in registrations:
            app_id = reg.get("applicationId")
            if not app_id:
                continue

            try:
                body = {
                    "loginId": model.userName,
                    "password": model.password,
                    "applicationId": app_id,
                    "noJWT": True,
                }
                result = await self._client.login(body)

                if result.get("user"):
                    return {
                        "applicationId": app_id,
                        "userName": user.get("username", model.userName),
                        "userId": user.get("id", ""),
                    }
            except FusionAuthAPIError:
                continue

        raise FusionAuthAPIError("Invalid credentials for this user", status_code=401)

    # ------------------------------------------------------------------
    # Two-factor login
    # ------------------------------------------------------------------

    async def login_with_two_factor(
        self,
        model: TwoFactorLoginRequest,
        ip_address: str | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {
            "code": model.code,
            "applicationId": str(model.applicationId),
            "twoFactorId": model.twoFactorId,
            "noJWT": True,
            "newDevice": True,
            "trustComputer": False,
        }
        if ip_address:
            body["ipAddress"] = ip_address

        result = await self._client.two_factor_login(body)

        user = result.get("user", {})
        roles = self._extract_roles(user, str(model.applicationId))

        access_token = create_access_token(
            user_id=user.get("id", ""),
            application_id=str(model.applicationId),
            roles=roles,
            settings=self._settings,
        )
        refresh_token = create_refresh_token(
            user_id=user.get("id", ""),
            application_id=str(model.applicationId),
            settings=self._settings,
        )

        return {
            "statusCode": 202,
            "accessToken": access_token,
            "refreshToken": refresh_token,
            "tokenType": "Bearer",
            "expiresIn": self._settings.access_token_expire_minutes * 60,
            "userId": user.get("id", ""),
            "applicationId": str(model.applicationId),
            "userName": user.get("username", ""),
            "roles": roles,
            "user": user,
        }

    # ------------------------------------------------------------------
    # Token refresh
    # ------------------------------------------------------------------

    async def refresh_token(self, refresh_token_str: str) -> dict[str, Any]:
        try:
            payload = decode_token(refresh_token_str, expected_type=TokenType.REFRESH, settings=self._settings)
        except InvalidTokenError as exc:
            raise FusionAuthAPIError(f"Invalid refresh token: {exc}", status_code=401) from exc

        user_data = await self._client.retrieve_user(payload.sub)
        user = user_data.get("user", {})
        roles = self._extract_roles(user, payload.app_id)

        new_access = create_access_token(
            user_id=payload.sub,
            application_id=payload.app_id,
            roles=roles,
            settings=self._settings,
        )
        new_refresh = create_refresh_token(
            user_id=payload.sub,
            application_id=payload.app_id,
            settings=self._settings,
        )

        return {
            "accessToken": new_access,
            "refreshToken": new_refresh,
            "tokenType": "Bearer",
            "expiresIn": self._settings.access_token_expire_minutes * 60,
        }

    # ------------------------------------------------------------------
    # Logout
    # ------------------------------------------------------------------

    async def logout(self, refresh_token_str: str | None = None) -> dict[str, str]:
        if refresh_token_str:
            try:
                await self._client.logout(True, refresh_token_str)
            except FusionAuthAPIError:
                pass
        return {"message": "Logged out successfully"}

    # ------------------------------------------------------------------
    # Password management
    # ------------------------------------------------------------------

    async def forgot_password(self, model: ForgotPasswordRequest) -> str:
        result = await self._client.forgot_password({
            "loginId": model.email,
            "sendForgotPasswordEmail": True,
        })
        return result.get("changePasswordId", "")

    async def change_password_with_token(self, model: ChangePasswordWithTokenRequest) -> dict[str, Any]:
        result = await self._client.change_password(model.changePasswordId, {
            "changePasswordId": model.changePasswordId,
            "currentPassword": model.currentPassword,
            "password": model.password,
            "loginId": model.id,
        })
        return result.get("state", {})

    async def change_password_for_login(
        self, change_password_id: str, password: str, email: str
    ) -> dict[str, Any]:
        user_data = await self._client.retrieve_user_by_email(email)
        user = user_data.get("user", {})

        result = await self._client.change_password(change_password_id, {
            "changePasswordId": change_password_id,
            "currentPassword": user.get("password", ""),
            "password": password,
            "loginId": email,
        })
        return result.get("state", {})

    async def reset_password(self, user_id: str, new_password: str | None = None) -> dict[str, Any] | None:
        """Admin reset — auto-generates password if none supplied (matches C# behavior)."""
        user_data = await self._client.retrieve_user(user_id)
        user = user_data.get("user", {})
        if not user:
            return None

        if not new_password:
            alphabet = string.ascii_letters + string.digits + string.ascii_uppercase + "!@#$%^&*"
            new_password = "".join(secrets.choice(alphabet) for _ in range(12))

        user["password"] = new_password
        result = await self._client.update_user(user_id, {"user": user})
        return {"user": result.get("user"), "newPassword": new_password}

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    async def register(self, model) -> dict[str, Any]:
        search_result = await self._client.search_users_by_query({
            "queryString": f'username:"{model.username}"',
            "startRow": 0,
            "numberOfResults": 50,
        })

        existing_users = search_result.get("users", [])
        for existing_user in existing_users:
            for reg in existing_user.get("registrations", []):
                if str(reg.get("applicationId")) == model.applicationId:
                    raise FusionAuthAPIError(
                        "Username already exists in this application",
                        status_code=409,
                    )

        if existing_users:
            try:
                test_body = {
                    "loginId": model.username,
                    "password": model.password,
                    "applicationId": existing_users[0].get("registrations", [{}])[0].get("applicationId", ""),
                    "noJWT": True,
                }
                test_result = await self._client.login(test_body)
                if test_result.get("user"):
                    raise FusionAuthAPIError(
                        "Password must be different when using the same username across applications",
                        status_code=409,
                    )
            except FusionAuthAPIError as exc:
                if exc.status_code == 409:
                    raise
                pass

        result = await self._client.register({
            "user": {
                "username": model.username,
                "email": model.email,
                "password": model.password,
                "firstName": model.firstName,
                "lastName": model.lastName,
            },
            "registration": {
                "applicationId": model.applicationId,
                "roles": ["user"] + (model.roles or []),
                "username": model.username,
            },
            "sendSetPasswordEmail": False,
            "skipRegistrationVerification": True,
            "skipVerification": True,
        })
        user = result.get("user", {})
        return {"user": user, "userId": user.get("id", "")}

    # ------------------------------------------------------------------
    # Verify security questions
    # ------------------------------------------------------------------

    async def verify_security_questions(self, model: SecurityQuestionsRequest) -> str:
        user_data = await self._client.retrieve_user_by_email(model.Email)
        user = user_data.get("user", {})
        user_data_blob = user.get("data", {})

        stored_json = user_data_blob.get("securityQuestions")
        if not stored_json:
            raise FusionAuthAPIError("Security questions not configured", status_code=400)

        stored = json.loads(stored_json) if isinstance(stored_json, str) else stored_json
        stored_map = {q["QuestionId"]: q["Answer"] for q in stored.get("Questions", [])}

        for submitted in model.Questions:
            stored_answer = stored_map.get(submitted.QuestionId)
            if stored_answer is None:
                raise FusionAuthAPIError("Invalid security question", status_code=400)
            if stored_answer.lower() != submitted.Answer.lower():
                raise FusionAuthAPIError("Incorrect answer", status_code=400)

        fp_result = await self._client.forgot_password({
            "loginId": model.Email,
            "sendForgotPasswordEmail": False,
        })
        change_password_id = fp_result.get("changePasswordId", "")
        if not change_password_id:
            raise FusionAuthAPIError("Failed to generate change password token", status_code=500)

        return change_password_id

    # ------------------------------------------------------------------
    # Get user
    # ------------------------------------------------------------------

    async def get_me(self, user_id: str) -> dict[str, Any] | None:
        result = await self._client.retrieve_user(user_id)
        return result.get("user")

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _extract_roles(self, user: dict, application_id: str) -> list[str]:
        for reg in user.get("registrations", []):
            if str(reg.get("applicationId")) == application_id:
                roles = reg.get("roles", [])
                if roles:
                    return roles
        return user.get("roles") or []


_auth_service: AuthService | None = None


def get_auth_service() -> AuthService:
    global _auth_service
    if _auth_service is None:
        _auth_service = AuthService()
    return _auth_service
