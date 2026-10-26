"""
User management business logic using the official FusionAuth SDK.

Covers user, application, role, and group operations.
Mirrors the C# UserManagementService + UserManagementController.
"""

from __future__ import annotations

from typing import Any

from core.config import Settings, get_settings
from core.exceptions import FusionAuthAPIError
from Schema.Authentication.user import (
    RoleAssignmentRequest,
    RoleRemovalRequest,
    UserCreateRequest,
    UserSearchRequest,
    UserUpdateRequest,
)
from services.fusionauth_client import FusionAuthSDKClient, get_fusionauth_client


class UserService:

    def __init__(
        self,
        client: FusionAuthSDKClient | None = None,
        settings: Settings | None = None,
    ) -> None:
        self._client = client or get_fusionauth_client()
        self._settings = settings or get_settings()

    # ------------------------------------------------------------------
    # User CRUD
    # ------------------------------------------------------------------

    async def get_users(self, search_key: str | None = None) -> list[dict]:
        query = search_key or "*"
        result = await self._client.search_users_by_query({
            "queryString": query, "startRow": 0, "numberOfResults": 10000,
        })
        return sorted(result.get("users", []), key=lambda u: u.get("username", ""))

    async def get_users_by_ids(self, user_ids: list[str]) -> list[dict]:
        result = await self._client.search_users_by_ids(user_ids)
        return sorted(result.get("users", []), key=lambda u: u.get("username", ""))

    async def get_users_paging(self, search: UserSearchRequest) -> dict[str, Any]:
        if search.applicationId:
            query = f"registrations.applicationId:{search.applicationId}"
        else:
            query = search.query or "*"

        start_row = search.pageIndex * search.pageSize

        result = await self._client.search_users_by_query({
            "queryString": query, "startRow": start_row, "numberOfResults": search.pageSize,
        })
        users = result.get("users", [])

        all_result = await self._client.search_users_by_query({
            "queryString": query, "startRow": 0, "numberOfResults": 0,
        })

        return {
            "users": sorted(users, key=lambda u: u.get("username", "")),
            "total": all_result.get("total", 0),
            "pageIndex": search.pageIndex,
            "pageSize": search.pageSize,
        }

    async def get_user(self, user_id: str) -> dict[str, Any] | None:
        result = await self._client.retrieve_user(user_id)
        return result.get("user")

    async def get_user_by_email(self, email: str) -> dict[str, Any] | None:
        result = await self._client.retrieve_user_by_email(email)
        return result.get("user")

    async def create_user(self, model: UserCreateRequest) -> dict[str, Any]:
        result = await self._client.register({
            "user": {
                "username": model.username, "email": model.email,
                "password": model.password, "firstName": model.firstName,
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
        return result.get("user", {})

    async def update_user(self, user_id: str, model: UserUpdateRequest) -> dict[str, Any] | None:
        current = await self.get_user(user_id)
        if not current:
            return None

        update_data: dict[str, Any] = {
            "email": current.get("email"),
            "username": current.get("username"),
        }
        if model.username is not None:
            update_data["username"] = model.username
        if model.email is not None:
            update_data["email"] = model.email
        if model.firstName is not None:
            update_data["firstName"] = model.firstName
        if model.lastName is not None:
            update_data["lastName"] = model.lastName
        if model.mobilePhone is not None:
            update_data["mobilePhone"] = model.mobilePhone
        if model.imageUrl is not None:
            update_data["imageUrl"] = model.imageUrl
        if model.data is not None:
            existing_data = current.get("data") or {}
            existing_data.update(model.data)
            update_data["data"] = existing_data

        result = await self._client.update_user(user_id, {"user": update_data})
        return result.get("user")

    async def change_password_self(self, user_id: str, current_password: str, new_password: str, application_id: str) -> bool:
        current = await self.get_user(user_id)
        if not current:
            raise FusionAuthNotFoundError("کاربر یافت نشد")

        login_id = current.get("username") or current.get("email")
        if not login_id:
            raise FusionAuthAPIError("اطلاعات هویتی کاربر ناقص است", status_code=400)

        # Verify current password by attempting authentication with applicationId
        try:
            await self._client.login({
                "loginId": login_id,
                "password": current_password,
                "applicationId": application_id,
                "noJWT": True,
            })
        except FusionAuthAPIError as e:
            if e.status_code == 401:
                raise FusionAuthAPIError("رمز عبور فعلی نادرست است", status_code=400) from e
            if e.status_code == 409:
                raise FusionAuthAPIError("حساب کاربری قفل شده است. لطفاً بعداً تلاش کنید.", status_code=423) from e
            # Pass through the actual FusionAuth error for other cases
            raise

        # Update to new password (FusionAuth requires full user object or user from retrieve_user)
        user_data = await self._client.retrieve_user(user_id)
        user = user_data.get("user", {})
        if not user:
            raise FusionAuthNotFoundError("کاربر یافت نشد")

        user["password"] = new_password
        await self._client.update_user(user_id, {"user": user})
        return True

    async def delete_user(self, user_id: str) -> bool:
        await self._client.delete_user(user_id)
        return True

    async def deactivate_user(self, user_id: str) -> bool:
        await self._client.deactivate_user(user_id)
        return True

    async def reactivate_user(self, user_id: str) -> bool:
        await self._client.reactivate_user(user_id)
        return True

    # ------------------------------------------------------------------
    # Applications
    # ------------------------------------------------------------------

    async def get_applications(self) -> list[dict]:
        result = await self._client.retrieve_applications()
        return result.get("applications", [])

    async def get_application_by_id(self, application_id: str) -> dict[str, Any] | None:
        result = await self._client.retrieve_application(application_id)
        return result.get("application")

    async def create_application(self, name: str, description: str = "") -> dict[str, Any] | None:
        result = await self._client.create_application({"application": {"name": name, "description": description}})
        app = result.get("application")
        if app:
            await self.create_application_role(app["id"], name="user", description="Default Application Role", is_default=True)
        return app

    async def update_application(self, application_id: str, name: str | None = None, description: str | None = None) -> dict[str, Any] | None:
        app_data: dict[str, Any] = {}
        if name is not None:
            app_data["name"] = name
        if description is not None:
            app_data["description"] = description
        result = await self._client.update_application(application_id, {"application": app_data})
        return result.get("application")

    async def delete_application(self, application_id: str) -> bool:
        await self._client.delete_application(application_id)
        return True

    async def deactivate_application(self, application_id: str) -> bool:
        await self._client.deactivate_application(application_id)
        return True

    async def reactivate_application(self, application_id: str) -> bool:
        await self._client.reactivate_application(application_id)
        return True

    # ------------------------------------------------------------------
    # Application roles
    # ------------------------------------------------------------------

    async def get_application_roles(self, application_id: str) -> list[dict]:
        result = await self._client.retrieve_application(application_id)
        return result.get("application", {}).get("roles", [])

    async def get_application_role_by_id(self, application_id: str, role_id: str) -> dict | None:
        roles = await self.get_application_roles(application_id)
        for role in roles:
            if role.get("id") == role_id:
                return role
        return None

    async def create_application_role(
        self, application_id: str, name: str, description: str = "",
        is_default: bool = False, is_super_role: bool = False,
    ) -> dict | None:
        result = await self._client.create_application_role(application_id, {
            "role": {"name": name, "description": description, "isDefault": is_default, "isSuperRole": is_super_role},
        })
        return result.get("role")

    async def update_application_role(self, application_id: str, role_id: str, name: str, description: str = "") -> dict | None:
        result = await self._client.update_application_role(application_id, role_id, {
            "role": {"name": name, "description": description},
        })
        return result.get("role")

    async def delete_application_role(self, application_id: str, role_id: str) -> bool:
        await self._client.delete_application_role(application_id, role_id)
        return True

    async def get_application_role_with_users(self, application_id: str, role_id: str) -> dict[str, Any] | None:
        role = await self.get_application_role_by_id(application_id, role_id)
        if not role:
            return None
        query = f"registrations.applicationId:{application_id} AND registrations.roles:{role['name']}"
        result = await self._client.search_users_by_query({
            "queryString": query, "startRow": 0, "numberOfResults": 10000,
        })
        app = await self.get_application_by_id(application_id)
        return {"applicationName": app.get("name", "") if app else "", "role": role, "users": result.get("users", [])}

    # ------------------------------------------------------------------
    # Groups
    # ------------------------------------------------------------------

    async def get_groups(self) -> list[dict]:
        result = await self._client.retrieve_groups()
        return result.get("groups", [])

    async def create_group(self, name: str, description: str = "") -> dict | None:
        result = await self._client.create_group({"group": {"name": name, "description": description}})
        return result.get("group")

    async def update_group(self, group_id: str, name: str, description: str = "") -> dict | None:
        result = await self._client.update_group(group_id, {"group": {"name": name, "description": description}})
        return result.get("group")

    async def delete_group(self, group_id: str) -> bool:
        await self._client.delete_group(group_id)
        return True

    async def add_user_to_group(self, user_id: str, group_id: str) -> dict | None:
        user = await self.get_user(user_id)
        if not user:
            return None
        memberships = user.get("memberships", [])
        memberships.append({"groupId": group_id, "userId": user_id})
        result = await self._client.update_user(user_id, {"user": {"memberships": memberships}})
        return result.get("user")

    async def set_user_group_membership(self, user_id: str, group_ids: list[str]) -> dict | None:
        memberships = [{"groupId": gid, "userId": user_id} for gid in group_ids]
        result = await self._client.update_user(user_id, {"user": {"memberships": memberships}})
        return result.get("user")

    # ------------------------------------------------------------------
    # Role assignment
    # ------------------------------------------------------------------

    async def assign_roles(self, model: RoleAssignmentRequest) -> dict | None:
        try:
            result = await self._client.update_registration(model.userId, {
                "registration": {"applicationId": model.applicationId, "roles": model.roles},
            })
            return result.get("registration")
        except Exception:
            result = await self._client.register({
                "registration": {"applicationId": model.applicationId, "roles": model.roles},
                "sendSetPasswordEmail": False,
                "skipRegistrationVerification": True,
                "skipVerification": True,
            }, user_id=model.userId)
            return result.get("registration")

    async def remove_roles(self, model: RoleRemovalRequest) -> dict | None:
        user = await self.get_user(model.userId)
        if not user:
            return None
        current_roles: list[str] = []
        for reg in user.get("registrations", []):
            if str(reg.get("applicationId")).lower() == model.applicationId.lower():
                current_roles = reg.get("roles", [])
                break
        remaining = [r for r in current_roles if r not in model.roles]
        try:
            result = await self._client.update_registration(model.userId, {
                "registration": {"applicationId": model.applicationId, "roles": remaining},
            })
            return result.get("registration")
        except Exception:
            result = await self._client.register({
                "registration": {"applicationId": model.applicationId, "roles": remaining},
                "sendSetPasswordEmail": False,
                "skipRegistrationVerification": True,
                "skipVerification": True,
            }, user_id=model.userId)
            return result.get("registration")

    # ------------------------------------------------------------------
    # Application registration
    # ------------------------------------------------------------------

    async def register_user_to_application(self, user_id: str, application_id: str, roles: list[str] | None = None) -> dict | None:
        await self._client.register({
            "registration": {"applicationId": application_id, "roles": roles or []},
            "sendSetPasswordEmail": False,
            "skipRegistrationVerification": True,
            "skipVerification": True,
        }, user_id=user_id)
        return await self.get_user(user_id)

    async def remove_user_from_application(self, user_id: str, application_id: str) -> bool:
        await self._client.delete_registration(user_id, application_id)
        return True

    # ------------------------------------------------------------------
    # Security questions
    # ------------------------------------------------------------------

    async def set_security_questions(self, user_id: str, questions_json: str) -> bool:
        user = await self.get_user(user_id)
        if not user:
            return False
        data = user.get("data", {})
        data["securityQuestions"] = questions_json
        result = await self._client.update_user(user_id, {"user": {"data": data}})
        return "user" in result


_user_service: UserService | None = None


def get_user_service() -> UserService:
    global _user_service
    if _user_service is None:
        _user_service = UserService()
    return _user_service
