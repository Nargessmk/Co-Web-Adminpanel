"""
User management endpoints — CRUD, search, profile, security questions.

Mirrors C# UserManagementController user-related endpoints.
Permissions to access these panels are governed by the dynamic application permission matrix.
"""

from __future__ import annotations

import json
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, status

from api.dependencies import AuthenticatedUser
from core.exceptions import FusionAuthAPIError, FusionAuthNotFoundError
from Schema.Authentication.user import (
    RoleAssignmentRequest,
    RoleRemovalRequest,
    UserChangePasswordRequest,
    UserSelfChangePasswordRequest,
    UserCreateRequest,
    UserSearchRequest,
    UserUpdateRequest,
)
from services.file_upload import FileUploadService, get_file_upload_service
from services.user_service import UserService, get_user_service

router = APIRouter()


def _err(exc: FusionAuthAPIError) -> HTTPException:
    detail = exc.message
    if exc.details:
        detail = {"message": exc.message, "details": exc.details}
    return HTTPException(status_code=exc.status_code or 400, detail=detail)


# ---- [AllowAnonymous] ----

@router.post("/", status_code=201, summary="Create user (public)")
async def create_user(model: UserCreateRequest, svc: UserService = Depends(get_user_service)):
    try:
        return {"message": "User created", "user": await svc.create_user(model)}
    except FusionAuthAPIError as e:
        raise _err(e) from e


# ---- [Authenticated User endpoints] ----

@router.get("/search/{search_key}", summary="Search users")
async def get_users(search_key: str, user: AuthenticatedUser, svc: UserService = Depends(get_user_service)):
    try:
        return await svc.get_users(search_key)
    except FusionAuthAPIError as e:
        raise _err(e) from e


@router.get("/search", summary="List all users")
async def get_users_all(user: AuthenticatedUser, svc: UserService = Depends(get_user_service)):
    try:
        return await svc.get_users()
    except FusionAuthAPIError as e:
        raise _err(e) from e


@router.post("/by-ids", summary="Get users by IDs")
async def get_users_by_ids(ids: list[str], user: AuthenticatedUser, svc: UserService = Depends(get_user_service)):
    try:
        return await svc.get_users_by_ids(ids)
    except FusionAuthAPIError as e:
        raise _err(e) from e


@router.get("/paging", summary="Paginated users")
async def get_users_paging(
    user: AuthenticatedUser,
    query: str = "*",
    pageIndex: int = Query(default=0, ge=0),
    pageSize: int = Query(default=25, ge=1, le=100),
    applicationId: str | None = Query(default=None, description="Filter by FusionAuth applicationId"),
    svc: UserService = Depends(get_user_service),
):
    try:
        return await svc.get_users_paging(UserSearchRequest(
            query=query, pageIndex=pageIndex, pageSize=pageSize, applicationId=applicationId,
        ))
    except FusionAuthAPIError as e:
        raise _err(e) from e


@router.get("/{user_id}", summary="Get user by ID")
async def get_user(user_id: str, current_user: AuthenticatedUser, svc: UserService = Depends(get_user_service)):
    try:
        result = await svc.get_user(user_id)
        if not result:
            raise HTTPException(status_code=404, detail="User not found")
        return result
    except FusionAuthNotFoundError:
        raise HTTPException(status_code=404, detail="User not found")
    except FusionAuthAPIError as e:
        raise _err(e) from e


@router.patch("/{user_id}", summary="Update user")
async def update_user(user_id: str, model: UserUpdateRequest, current_user: AuthenticatedUser, svc: UserService = Depends(get_user_service)):
    try:
        result = await svc.update_user(user_id, model)
        if not result:
            raise HTTPException(status_code=404, detail="User not found")
        return {"message": "User updated", "user": result}
    except FusionAuthNotFoundError:
        raise HTTPException(status_code=404, detail="User not found")
    except FusionAuthAPIError as e:
        raise _err(e) from e


@router.post("/{user_id}/change-password", summary="Change password for current user")
async def change_password_self(
    user_id: str,
    model: UserSelfChangePasswordRequest,
    current_user: AuthenticatedUser,
    svc: UserService = Depends(get_user_service),
):
    is_admin = "admin" in current_user.roles
    if not is_admin and current_user.sub != user_id:
        raise HTTPException(status_code=403, detail="دسترسی غیرمجاز")
    # Validate applicationId from body matches the one in the JWT token
    if model.applicationId != current_user.app_id:
        raise HTTPException(status_code=403, detail="applicationId با توکن احراز هویت مطابقت ندارد")
    try:
        await svc.change_password_self(user_id, model.currentPassword, model.password, model.applicationId)
        return {"message": "رمز عبور با موفقیت تغییر کرد"}
    except FusionAuthAPIError as e:
        raise _err(e) from e


@router.delete("/{user_id}", summary="Delete user")
async def delete_user(user_id: str, user: AuthenticatedUser, svc: UserService = Depends(get_user_service)):
    try:
        await svc.delete_user(user_id)
        return {"message": "User deleted"}
    except FusionAuthNotFoundError:
        raise HTTPException(status_code=404, detail="User not found")
    except FusionAuthAPIError as e:
        raise _err(e) from e


@router.post("/{user_id}/deactivate", summary="Deactivate user")
async def deactivate_user(user_id: str, user: AuthenticatedUser, svc: UserService = Depends(get_user_service)):
    try:
        await svc.deactivate_user(user_id)
        return {"message": "User deactivated"}
    except FusionAuthAPIError as e:
        raise _err(e) from e


@router.post("/{user_id}/reactivate", summary="Reactivate user")
async def reactivate_user(user_id: str, user: AuthenticatedUser, svc: UserService = Depends(get_user_service)):
    try:
        await svc.reactivate_user(user_id)
        return {"message": "User reactivated"}
    except FusionAuthAPIError as e:
        raise _err(e) from e


# ---- Role assignment (belongs to user context) ----

@router.post("/roles/assign", summary="Assign roles to user")
async def assign_roles(model: RoleAssignmentRequest, user: AuthenticatedUser, svc: UserService = Depends(get_user_service)):
    try:
        return {"message": "Roles assigned", "registration": await svc.assign_roles(model)}
    except FusionAuthAPIError as e:
        raise _err(e) from e


@router.post("/roles/remove", summary="Remove roles from user")
async def remove_roles(model: RoleRemovalRequest, user: AuthenticatedUser, svc: UserService = Depends(get_user_service)):
    try:
        return {"message": "Roles removed", "registration": await svc.remove_roles(model)}
    except FusionAuthAPIError as e:
        raise _err(e) from e


@router.post("/register-application/{user_id}/{application_id}", summary="Register user to application")
async def register_to_app(user_id: str, application_id: str, user: AuthenticatedUser, roles: list[str] | None = None, svc: UserService = Depends(get_user_service)):
    try:
        return {"message": "Registered", "user": await svc.register_user_to_application(user_id, application_id, roles)}
    except FusionAuthAPIError as e:
        raise _err(e) from e


@router.delete("/register-application/{user_id}/{application_id}", summary="Remove user from application")
async def unregister_from_app(user_id: str, application_id: str, user: AuthenticatedUser, svc: UserService = Depends(get_user_service)):
    try:
        await svc.remove_user_from_application(user_id, application_id)
        return {"message": "Removed from application"}
    except FusionAuthAPIError as e:
        raise _err(e) from e


# ---- Profile image & security questions ----

@router.put("/profile-image/{user_id}", summary="Upload profile image")
async def upload_image(user_id: str, file: UploadFile, current_user: AuthenticatedUser, svc: FileUploadService = Depends(get_file_upload_service)):
    content = await file.read()
    result = await svc.upload_profile_image(user_id, file.filename or "unknown", content)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return {"message": "Uploaded", "imageUrl": result["imageUrl"]}


@router.delete("/profile-image/{user_id}", summary="Delete profile image")
async def delete_image(user_id: str, current_user: AuthenticatedUser, svc: FileUploadService = Depends(get_file_upload_service)):
    if not await svc.delete_profile_image(user_id):
        raise HTTPException(status_code=400, detail="Failed to delete")
    return {"message": "Deleted"}


@router.put("/security-questions/{user_id}", summary="Set security questions")
async def set_questions(user_id: str, questions: dict, current_user: AuthenticatedUser, svc: UserService = Depends(get_user_service)):
    if not await svc.set_security_questions(user_id, json.dumps(questions)):
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "Security questions set"}
