from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from uuid import UUID

from api.dependencies import CurrentUser, require_admin, require_tenant, require_user
from Schema.AppManagement.reindex_result import ReindexResult
from services.reindex_service import SUPPORTED_VIEWS, reindex_all, reindex_by_view_name

router = APIRouter()


@router.get("/views", response_model=list[str])
async def get_available_views(
    current_user: CurrentUser = Depends(require_user),
):
    try:
        return list(SUPPORTED_VIEWS)
    except Exception as e:
        return JSONResponse(status_code=500, content="Internal server error")


@router.get("/status")
async def get_scheduler_status(
    current_user: CurrentUser = Depends(require_user),
):
    return {
        "scheduler_running": False,
        "jobs": [],
        "note": "AppManagement does not run a local scheduler. The weekly reindex job is managed by Service-BackgroundTask.",
    }


@router.post("/reindex/{view_name}", response_model=ReindexResult)
async def reindex_view(
    view_name: str,
    application_id: UUID = Query(..., description="Tenant to reindex"),
    tenant: tuple[UUID, CurrentUser] = Depends(require_tenant),
):
    try:
        result = await reindex_by_view_name(view_name, application_id)
    except HTTPException:
        raise
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content=ReindexResult.failure(f"Internal server error: {e}").model_dump(by_alias=True, mode="json"),
        )
    if not result.is_success:
        return JSONResponse(
            status_code=400,
            content=result.model_dump(by_alias=True, mode="json"),
        )
    return result


@router.post("/reindex-all", response_model=ReindexResult)
async def reindex_all_views(
    application_id: UUID = Query(..., description="Tenant to reindex"),
    tenant: tuple[UUID, CurrentUser] = Depends(require_tenant),
):
    try:
        result = await reindex_all(application_id)
    except HTTPException:
        raise
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content=ReindexResult.failure(f"Internal server error: {e}").model_dump(by_alias=True, mode="json"),
        )
    if not result.is_success:
        return JSONResponse(
            status_code=400,
            content=result.model_dump(by_alias=True, mode="json"),
        )
    return result
