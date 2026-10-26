from typing import List
from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from uuid import UUID

from api.dependencies import CurrentUser, require_tenant
from Schema.AppManagement.reindex_result import ReindexResult
from services.reindex_service import SUPPORTED_VIEWS, ReindexJobService
from core.scheduler import get_scheduler

router = APIRouter(prefix="/api/v1/reindex", tags=["Reindex v1"])


@router.get("/views", response_model=List[str])
async def get_available_views(
    tenant: tuple[UUID, CurrentUser] = Depends(require_tenant),
):
    application_id, current_user = tenant
    """Returns available database views supported for reindexing."""
    return list(SUPPORTED_VIEWS)


@router.get("/status")
async def get_scheduler_status(
    tenant: tuple[UUID, CurrentUser] = Depends(require_tenant),
):
    application_id, current_user = tenant
    """Returns background scheduler status and registered jobs."""
    scheduler = get_scheduler()
    jobs = []
    if scheduler and scheduler.running:
        for job in scheduler.get_jobs():
            jobs.append(
                {
                    "id": job.id,
                    "name": job.name,
                    "next_run_time": str(job.next_run_time),
                    "trigger": str(job.trigger),
                }
            )
    return {"scheduler_running": bool(scheduler and scheduler.running), "jobs": jobs}


@router.post("/reindex/{view_name}", response_model=ReindexResult)
async def reindex_view(
    view_name: str,
    application_id: UUID | None = Query(None, description="Tenant to reindex (admin-only; defaults to caller's tenant)"),
    tenant: tuple[UUID, CurrentUser] = Depends(require_tenant),
):
    tenant_app_id, current_user = tenant
    try:
        if application_id is not None and application_id != tenant_app_id:
            if "admin" not in current_user.roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied: cannot reindex another tenant",
                )
        target_app_id = application_id or tenant_app_id
        if target_app_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="application_id is required",
            )
        result = await ReindexJobService.execute_reindex_by_view_job_async(
            view_name=view_name, application_id=target_app_id
        )
    except HTTPException:
        raise
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content=ReindexResult.failure(f"Internal server error: {e}").model_dump(
                by_alias=True, mode="json"
            ),
        )
    if not result.is_success:
        return JSONResponse(
            status_code=400,
            content=result.model_dump(by_alias=True, mode="json"),
        )
    return result


@router.post("/reindex-all", response_model=ReindexResult)
async def reindex_all_views(
    application_id: UUID | None = Query(None, description="Tenant to reindex (admin-only; defaults to caller's tenant)"),
    tenant: tuple[UUID, CurrentUser] = Depends(require_tenant),
):
    tenant_app_id, current_user = tenant
    try:
        if application_id is not None and application_id != tenant_app_id:
            if "admin" not in current_user.roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied: cannot reindex another tenant",
                )
        target_app_id = application_id or tenant_app_id
        if target_app_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="application_id is required",
            )
        result = await ReindexJobService.execute_reindex_all_job_async(
            application_id=target_app_id
        )
    except HTTPException:
        raise
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content=ReindexResult.failure(f"Internal server error: {e}").model_dump(
                by_alias=True, mode="json"
            ),
        )
    if not result.is_success:
        return JSONResponse(
            status_code=400,
            content=result.model_dump(by_alias=True, mode="json"),
        )
    return result
