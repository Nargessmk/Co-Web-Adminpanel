from uuid import UUID
from datetime import datetime
from urllib.parse import unquote

from fastapi import APIRouter, BackgroundTasks, Body, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse

from api.dependencies import CurrentUser, require_admin, require_tenant
from Schema.base import parse_persian
from Schema.AppManagement.constant import ConstantDTO
from Schema.AppManagement.constant_recursive import ConstantRecursiveDTO
from Schema.paged_result import PagedResult
from application.queries import (
    GetConstantQuery,
    GetRootConstantsQuery,
    GetRootConstantPagingQuery,
    GetChildConstantsQuery,
    GetConstantsByIdsQuery,
    GetConstantsRecursiveWithPermissionsQuery,
    GetAllConstantsQuery,
    GetConstantsRecursiveQuery,
    GetConstantByDateQuery,
    GetTreeConstantQuery,
    GetConstantNodeTypeQuery,
    RetrieveJsonDataQuery,
)
from application.commands import (
    CreateConstantCommand,
    UpdateConstantCommand,
    DeleteConstantCommand,
    DeleteAllChildConstantsCommand,
    StoreJsonDataCommand,
)
from core.mediator import get_mediator
from core.exceptions import DeleteForbiddenError
from services.redis_client import invalidate_constant_cache

router = APIRouter()


@router.get("/", response_model=list[ConstantDTO])
async def get_root_constants(
    tenant: tuple[UUID, CurrentUser] = Depends(require_tenant),
):
    application_id, current_user = tenant
    mediator = get_mediator()
    return await mediator.send(GetRootConstantsQuery(application_id=application_id))


@router.get("/All", response_model=list[ConstantDTO])
async def get_all_constants(
    tenant: tuple[UUID, CurrentUser] = Depends(require_tenant),
):
    application_id, current_user = tenant
    mediator = get_mediator()
    return await mediator.send(GetAllConstantsQuery(application_id=application_id))


@router.get("/ById/{constant_id}", response_model=ConstantDTO | None)
async def get_constant_by_id(
    constant_id: UUID,
    tenant: tuple[UUID, CurrentUser] = Depends(require_tenant),
):
    application_id, current_user = tenant
    mediator = get_mediator()
    return await mediator.send(GetConstantQuery(id=constant_id, application_id=application_id))


@router.get("/ByIds", response_model=list[ConstantDTO])
async def get_constants_by_ids(
    ids: list[UUID] = Body(...),
    tenant: tuple[UUID, CurrentUser] = Depends(require_tenant),
):
    application_id, current_user = tenant
    if not ids:
        raise HTTPException(status_code=400, detail="IDs list cannot be null or empty")
    mediator = get_mediator()
    return await mediator.send(GetConstantsByIdsQuery(ids=ids, application_id=application_id))


@router.get("/ChildsByRootId/{root_id}", response_model=list[ConstantDTO])
async def get_child_constants(
    root_id: UUID,
    tenant: tuple[UUID, CurrentUser] = Depends(require_tenant),
):
    application_id, current_user = tenant
    mediator = get_mediator()
    return await mediator.send(GetChildConstantsQuery(root_id=root_id, application_id=application_id))


@router.get("/ByDate/{root_id}/{date_time:path}", response_model=list[ConstantRecursiveDTO])
async def get_constant_by_date(
    root_id: UUID,
    date_time: str,
    tenant: tuple[UUID, CurrentUser] = Depends(require_tenant),
):
    application_id, current_user = tenant
    mediator = get_mediator()
    parsed = parse_persian(unquote(date_time))
    if parsed is None:
        try:
            parsed = datetime.fromisoformat(unquote(date_time).replace("Z", "+00:00"))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date time format")
    return await mediator.send(GetConstantByDateQuery(root_id=root_id, date_time=parsed, application_id=application_id))


@router.get("/ByToday/{root_id}", response_model=list[ConstantRecursiveDTO])
async def get_constant_by_today(
    root_id: UUID,
    tenant: tuple[UUID, CurrentUser] = Depends(require_tenant),
):
    application_id, current_user = tenant
    mediator = get_mediator()
    return await mediator.send(GetConstantByDateQuery(root_id=root_id, date_time=datetime.now(), application_id=application_id))


@router.get("/TreeViewByRootId/{root_id}", response_model=list[ConstantDTO])
async def get_tree_constant(
    root_id: UUID,
    tenant: tuple[UUID, CurrentUser] = Depends(require_tenant),
):
    application_id, current_user = tenant
    mediator = get_mediator()
    return await mediator.send(GetTreeConstantQuery(root_id=root_id, application_id=application_id))


@router.get("/PagingChildsByRootId/{root_id}/{page_number}/{page_size}", response_model=PagedResult[ConstantDTO])
async def get_root_constant_paging(
    root_id: UUID,
    page_number: int,
    page_size: int,
    tenant: tuple[UUID, CurrentUser] = Depends(require_tenant),
):
    application_id, current_user = tenant
    mediator = get_mediator()
    return await mediator.send(
        GetRootConstantPagingQuery(root_id=root_id, page_number=page_number, page_size=page_size, application_id=application_id)
    )


@router.get("/GetConstantRecursiveByRootId/{root_id}", response_model=list[ConstantRecursiveDTO])
async def get_constants_recursive(
    root_id: UUID,
    tenant: tuple[UUID, CurrentUser] = Depends(require_tenant),
):
    application_id, current_user = tenant
    mediator = get_mediator()
    return await mediator.send(GetConstantsRecursiveQuery(root_id=root_id, application_id=application_id))


@router.get(
    "/GetConstantNodeType/{node_id}/{node_type_id}",
    response_model=list[ConstantDTO],
)
async def get_constant_node_type(
    node_id: UUID,
    node_type_id: UUID,
    tenant: tuple[UUID, CurrentUser] = Depends(require_tenant),
):
    application_id, current_user = tenant
    mediator = get_mediator()
    return await mediator.send(
        GetConstantNodeTypeQuery(node_id=node_id, node_type_id=node_type_id, application_id=application_id)
    )


@router.put("/StoreJsonData/{node_id}", status_code=status.HTTP_200_OK)
async def store_json_data(
    node_id: UUID,
    background_tasks: BackgroundTasks,
    node_type: str | None = Query(default=None),
    data_object: str = Body(...),
    tenant: tuple[UUID, CurrentUser] = Depends(require_tenant),
):
    application_id, current_user = tenant
    mediator = get_mediator()
    user_id = current_user.user_id or UUID(int=0)
    command = StoreJsonDataCommand(
        node_id=node_id,
        node_type=node_type,
        data_object=data_object,
        user_id=user_id,
        application_id=application_id,
    )
    result = await mediator.send(command)
    background_tasks.add_task(invalidate_constant_cache, application_id)
    return JSONResponse(content=result)


@router.get("/RetrieveJsonData/{node_id}")
async def retrieve_json_data(
    node_id: UUID,
    node_type: str | None = Query(default=None),
    tenant: tuple[UUID, CurrentUser] = Depends(require_tenant),
):
    application_id, current_user = tenant
    mediator = get_mediator()
    result = await mediator.send(RetrieveJsonDataQuery(node_id=node_id, node_type=node_type, application_id=application_id))
    return JSONResponse(content=result)


@router.post("/", response_model=ConstantDTO)
async def create_constant(
    dto: ConstantDTO,
    background_tasks: BackgroundTasks,
    _admin: CurrentUser = Depends(require_admin),
    tenant: tuple[UUID, CurrentUser] = Depends(require_tenant),
):
    application_id, current_user = tenant
    mediator = get_mediator()
    user_id = current_user.user_id or UUID(int=0)
    command = CreateConstantCommand(dto=dto, user_id=user_id, application_id=application_id)
    result = await mediator.send(command)
    background_tasks.add_task(invalidate_constant_cache, application_id)
    if result is None:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content="")
    return result


@router.put("/", response_model=ConstantDTO)
async def update_constant(
    dto: ConstantDTO,
    background_tasks: BackgroundTasks,
    _admin: CurrentUser = Depends(require_admin),
    tenant: tuple[UUID, CurrentUser] = Depends(require_tenant),
):
    application_id, current_user = tenant
    mediator = get_mediator()
    user_id = current_user.user_id or UUID(int=0)
    if dto.id is None:
        raise HTTPException(status_code=400, detail="Constant id is null")
    command = UpdateConstantCommand(id=dto.id, dto=dto, user_id=user_id, application_id=application_id)
    result = await mediator.send(command)
    background_tasks.add_task(invalidate_constant_cache, application_id)
    return result


@router.delete("/{constant_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_constant(
    constant_id: UUID,
    background_tasks: BackgroundTasks,
    _admin: CurrentUser = Depends(require_admin),
    tenant: tuple[UUID, CurrentUser] = Depends(require_tenant),
):
    application_id, current_user = tenant
    mediator = get_mediator()
    user_id = current_user.user_id or UUID(int=0)
    command = DeleteConstantCommand(id=constant_id, user_id=user_id, application_id=application_id)
    try:
        await mediator.send(command)
    except DeleteForbiddenError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    background_tasks.add_task(invalidate_constant_cache, application_id)


@router.delete("/DeleteAllChild/{parent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_all_child_constants(
    parent_id: UUID,
    background_tasks: BackgroundTasks,
    _admin: CurrentUser = Depends(require_admin),
    tenant: tuple[UUID, CurrentUser] = Depends(require_tenant),
):
    application_id, current_user = tenant
    mediator = get_mediator()
    user_id = current_user.user_id or UUID(int=0)
    command = DeleteAllChildConstantsCommand(parent_id=parent_id, user_id=user_id, application_id=application_id)
    result = await mediator.send(command)
    if result is False:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Node has a child")
    background_tasks.add_task(invalidate_constant_cache, application_id)
