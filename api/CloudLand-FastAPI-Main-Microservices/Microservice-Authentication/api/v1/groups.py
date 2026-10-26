"""
Group management endpoints — CRUD for FusionAuth groups and membership.

Mirrors C# UserManagementController group-related endpoints.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from api.dependencies import AdminUser
from core.exceptions import FusionAuthAPIError
from services.user_service import UserService, get_user_service

router = APIRouter()


def _err(exc: FusionAuthAPIError) -> HTTPException:
    return HTTPException(status_code=exc.status_code or 400, detail=exc.message)


@router.get("/list", summary="List all groups")
async def get_groups(admin: AdminUser, svc: UserService = Depends(get_user_service)):
    try:
        return await svc.get_groups()
    except FusionAuthAPIError as e:
        raise _err(e) from e


@router.post("/", status_code=201, summary="Create group")
async def create_group(name: str, admin: AdminUser, description: str = "", svc: UserService = Depends(get_user_service)):
    try:
        return {"message": "Group created", "group": await svc.create_group(name, description)}
    except FusionAuthAPIError as e:
        raise _err(e) from e


@router.patch("/{group_id}", summary="Update group")
async def update_group(group_id: str, name: str, admin: AdminUser, description: str = "", svc: UserService = Depends(get_user_service)):
    try:
        return {"message": "Group updated", "group": await svc.update_group(group_id, name, description)}
    except FusionAuthAPIError as e:
        raise _err(e) from e


@router.delete("/{group_id}", summary="Delete group")
async def delete_group(group_id: str, admin: AdminUser, svc: UserService = Depends(get_user_service)):
    try:
        await svc.delete_group(group_id)
        return {"message": "Group deleted"}
    except FusionAuthAPIError as e:
        raise _err(e) from e


@router.post("/{group_id}/users/{user_id}", summary="Add user to group")
async def add_to_group(group_id: str, user_id: str, admin: AdminUser, svc: UserService = Depends(get_user_service)):
    try:
        return {"message": "User added", "user": await svc.add_user_to_group(user_id, group_id)}
    except FusionAuthAPIError as e:
        raise _err(e) from e
