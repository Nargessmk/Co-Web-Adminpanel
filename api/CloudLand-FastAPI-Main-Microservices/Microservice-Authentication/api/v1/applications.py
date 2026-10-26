"""
Application management endpoints — CRUD for FusionAuth applications.

Mirrors C# UserManagementController application-related endpoints.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from api.dependencies import AdminUser
from core.exceptions import FusionAuthAPIError, FusionAuthNotFoundError
from services.user_service import UserService, get_user_service

router = APIRouter()


def _err(exc: FusionAuthAPIError) -> HTTPException:
    return HTTPException(status_code=exc.status_code or 400, detail=exc.message)


@router.get("/list", summary="List all applications")
async def get_applications(admin: AdminUser, svc: UserService = Depends(get_user_service)):
    try:
        return await svc.get_applications()
    except FusionAuthAPIError as e:
        raise _err(e) from e


@router.get("/{application_id}", summary="Get application by ID")
async def get_application(application_id: str, admin: AdminUser, svc: UserService = Depends(get_user_service)):
    try:
        result = await svc.get_application_by_id(application_id)
        if not result:
            raise HTTPException(status_code=404, detail="Application not found")
        return result
    except FusionAuthNotFoundError:
        raise HTTPException(status_code=404, detail="Application not found")
    except FusionAuthAPIError as e:
        raise _err(e) from e


@router.post("/", status_code=201, summary="Create application")
async def create_application(name: str, admin: AdminUser, description: str = "", svc: UserService = Depends(get_user_service)):
    try:
        return {"message": "Application created", "application": await svc.create_application(name, description)}
    except FusionAuthAPIError as e:
        raise _err(e) from e


@router.patch("/{application_id}", summary="Update application")
async def update_application(application_id: str, admin: AdminUser, name: str | None = None, description: str | None = None, svc: UserService = Depends(get_user_service)):
    try:
        return {"message": "Updated", "application": await svc.update_application(application_id, name, description)}
    except FusionAuthAPIError as e:
        raise _err(e) from e


@router.delete("/{application_id}", summary="Delete application")
async def delete_application(application_id: str, admin: AdminUser, svc: UserService = Depends(get_user_service)):
    try:
        await svc.delete_application(application_id)
        return {"message": "Application deleted"}
    except FusionAuthAPIError as e:
        raise _err(e) from e


@router.post("/{application_id}/deactivate", summary="Deactivate application")
async def deactivate_application(application_id: str, admin: AdminUser, svc: UserService = Depends(get_user_service)):
    try:
        await svc.deactivate_application(application_id)
        return {"message": "Deactivated"}
    except FusionAuthAPIError as e:
        raise _err(e) from e


@router.post("/{application_id}/reactivate", summary="Reactivate application")
async def reactivate_application(application_id: str, admin: AdminUser, svc: UserService = Depends(get_user_service)):
    try:
        await svc.reactivate_application(application_id)
        return {"message": "Reactivated"}
    except FusionAuthAPIError as e:
        raise _err(e) from e
