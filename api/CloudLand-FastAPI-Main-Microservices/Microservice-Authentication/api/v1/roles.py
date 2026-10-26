"""
Application role management endpoints — CRUD for roles within a FusionAuth application.

Mirrors C# UserManagementController role-related endpoints.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from api.dependencies import AuthenticatedUser
from core.exceptions import FusionAuthAPIError
from services.user_service import UserService, get_user_service
from pydantic import BaseModel

class RoleDTO(BaseModel):
    name: str | None = None
    description: str = ""
    isDefault: bool = False
    isSuperRole: bool = False

router = APIRouter()


def _err(exc: FusionAuthAPIError) -> HTTPException:
    return HTTPException(status_code=exc.status_code or 400, detail=exc.message)


@router.get("/{application_id}/roles", summary="List roles for an application")
async def get_roles(application_id: str, user: AuthenticatedUser, svc: UserService = Depends(get_user_service)):
    try:
        return await svc.get_application_roles(application_id)
    except FusionAuthAPIError as e:
        raise _err(e) from e


@router.get("/{application_id}/roles/{role_id}", summary="Get role by ID")
async def get_role(application_id: str, role_id: str, user: AuthenticatedUser, svc: UserService = Depends(get_user_service)):
    try:
        result = await svc.get_application_role_by_id(application_id, role_id)
        if not result:
            raise HTTPException(status_code=404, detail="Role not found")
        return result
    except FusionAuthAPIError as e:
        raise _err(e) from e


@router.get("/{application_id}/roles/{role_id}/users", summary="Get users assigned to a role")
async def get_role_users(application_id: str, role_id: str, user: AuthenticatedUser, svc: UserService = Depends(get_user_service)):
    try:
        result = await svc.get_application_role_with_users(application_id, role_id)
        if not result:
            raise HTTPException(status_code=404, detail="Role not found")
        return result
    except FusionAuthAPIError as e:
        raise _err(e) from e


@router.post("/{application_id}/roles/", status_code=201, summary="Create role in application")
async def create_role(application_id: str, data: RoleDTO, user: AuthenticatedUser, svc: UserService = Depends(get_user_service)):
    try:
        if not data.name:
            raise HTTPException(status_code=400, detail="Role name is required")
        return {"message": "Role created", "role": await svc.create_application_role(application_id, data.name, data.description)}
    except FusionAuthAPIError as e:
        raise _err(e) from e


@router.patch("/{application_id}/roles/{role_id}", summary="Update role")
async def update_role(application_id: str, role_id: str, data: RoleDTO, user: AuthenticatedUser, svc: UserService = Depends(get_user_service)):
    try:
        return {"message": "Role updated", "role": await svc.update_application_role(application_id, role_id, data.name, data.description)}
    except FusionAuthAPIError as e:
        raise _err(e) from e


@router.delete("/{application_id}/roles/{role_id}", summary="Delete role")
async def delete_role(application_id: str, role_id: str, user: AuthenticatedUser, svc: UserService = Depends(get_user_service)):
    try:
        await svc.delete_application_role(application_id, role_id)
        return {"message": "Role deleted"}
    except FusionAuthAPIError as e:
        raise _err(e) from e
