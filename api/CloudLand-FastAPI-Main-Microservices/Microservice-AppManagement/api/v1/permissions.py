from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, Query
from sqlalchemy import select, or_

from api.dependencies import CurrentUser, require_admin, require_tenant
from Schema.AppManagement.permission import UserConstantPermissionDTO
from Schema.AppManagement.constant_recursive import ConstantRecursiveDTO
from application.queries import GetConstantsRecursiveWithPermissionsQuery
from application.commands import UpdateConstantPermissionCommand
from core.mediator import get_mediator
from services.fusionauth_client import resolve_user_roles_and_groups
from services.redis_client import invalidate_constant_cache
from fastapi import HTTPException, status
from Models.permission import UserConstantPermission
from middleware.uow_middleware import get_current_uow

router = APIRouter()


@router.get(
    "/assigned-ids-for-role/{role_id}",
    response_model=list[UUID],
)
async def get_assigned_constant_ids_for_role(
    role_id: UUID,
    tenant: tuple[UUID, CurrentUser] = Depends(require_tenant),
):
    """
    Secure and fast query to fetch all granted constant_ids for a given role in the tenant.
    Avoids heavy recursive CTEs when only the assigned IDs are required.
    """
    application_id, current_user = tenant
    uow = get_current_uow()
    stmt = select(UserConstantPermission.constant_id).where(
        UserConstantPermission.application_id == application_id,
        UserConstantPermission.role_id == role_id,
        UserConstantPermission.constant_id.isnot(None),
        UserConstantPermission.has_permission == True,
    )
    result = await uow.session.execute(stmt)
    return [cid for cid in result.scalars().all() if cid is not None]


@router.get(
    "/assigned-ids-for-user/{user_id}",
    response_model=list[UUID],
)
async def get_assigned_constant_ids_for_user(
    user_id: UUID,
    tenant: tuple[UUID, CurrentUser] = Depends(require_tenant),
):
    """
    Secure and fast query to fetch all granted constant_ids for a user.
    If user is locked, returns user-specific explicit overrides.
    If user is not locked, resolves roles/groups from FusionAuth and returns their union.
    """
    application_id, current_user = tenant
    uow = get_current_uow()

    # 1. Check if user has explicit lock/override
    lock_stmt = select(1).where(
        UserConstantPermission.application_id == application_id,
        UserConstantPermission.user_id == user_id,
    )
    is_locked = (await uow.session.execute(lock_stmt)).scalar() is not None

    if is_locked:
        stmt = select(UserConstantPermission.constant_id).where(
            UserConstantPermission.application_id == application_id,
            UserConstantPermission.user_id == user_id,
            UserConstantPermission.constant_id.isnot(None),
            UserConstantPermission.has_permission == True,
        )
        result = await uow.session.execute(stmt)
        return [cid for cid in result.scalars().all() if cid is not None]

    # 2. If not locked, inherit from roles and groups
    role_ids_str, group_ids_str, _ = await resolve_user_roles_and_groups(user_id, application_id)
    role_uuids: list[UUID] = []
    for r in role_ids_str:
        try:
            role_uuids.append(UUID(r))
        except (ValueError, TypeError):
            pass

    group_uuids: list[UUID] = []
    for g in group_ids_str:
        try:
            group_uuids.append(UUID(g))
        except (ValueError, TypeError):
            pass

    conditions = []
    if role_uuids:
        conditions.append(UserConstantPermission.role_id.in_(role_uuids))
    if group_uuids:
        conditions.append(UserConstantPermission.group_id.in_(group_uuids))

    if not conditions:
        return []

    stmt = select(UserConstantPermission.constant_id).where(
        UserConstantPermission.application_id == application_id,
        UserConstantPermission.constant_id.isnot(None),
        UserConstantPermission.has_permission == True,
        or_(*conditions),
    )
    result = await uow.session.execute(stmt)
    return list(set(cid for cid in result.scalars().all() if cid is not None))


@router.get(
    "/GetConstantWithPermissionForRole/{root_id}/{role_id}",
    response_model=list[ConstantRecursiveDTO],
)
async def get_constant_with_permission_for_role(
    root_id: UUID,
    role_id: UUID,
    tenant: tuple[UUID, CurrentUser] = Depends(require_tenant),
):
    application_id, current_user = tenant
    mediator = get_mediator()
    return await mediator.send(
        GetConstantsRecursiveWithPermissionsQuery(root_id=root_id, role_id=role_id, application_id=application_id)
    )


@router.get(
    "/GetConstantWithPermissionForUser/{root_id}/{user_id}",
    response_model=list[ConstantRecursiveDTO],
)
async def get_constant_with_permission_for_user(
    root_id: UUID,
    user_id: UUID,
    tenant: tuple[UUID, CurrentUser] = Depends(require_tenant),
):
    application_id, current_user = tenant
    role_ids, group_ids, _ = await resolve_user_roles_and_groups(user_id, application_id)
    mediator = get_mediator()
    return await mediator.send(
        GetConstantsRecursiveWithPermissionsQuery(
            root_id=root_id,
            user_id=user_id,
            role_ids=[UUID(r) for r in role_ids],
            group_ids=[UUID(g) for g in group_ids],
            application_id=application_id,
        )
    )


@router.get(
    "/GetConstantWithPermissionForGroup/{root_id}/{group_id}",
    response_model=list[ConstantRecursiveDTO],
)
async def get_constant_with_permission_for_group(
    root_id: UUID,
    group_id: UUID,
    tenant: tuple[UUID, CurrentUser] = Depends(require_tenant),
):
    application_id, current_user = tenant
    mediator = get_mediator()
    return await mediator.send(
        GetConstantsRecursiveWithPermissionsQuery(root_id=root_id, group_id=group_id, application_id=application_id)
    )


@router.post("/UpdateConstantPermission", response_model=list[UserConstantPermissionDTO])
async def update_constant_permission(
    constants: list[UUID],
    background_tasks: BackgroundTasks,
    application_id: UUID = Query(...),
    user_id: UUID | None = None,
    role_id: UUID | None = None,
    group_id: UUID | None = None,
    tenant: tuple[UUID, CurrentUser] = Depends(require_tenant),
):
    mediator = get_mediator()
    application_id, current_user = tenant
    actor_id = current_user.user_id or UUID(int=0)
    result = await mediator.send(
        UpdateConstantPermissionCommand(
            user_id=user_id,
            role_id=role_id,
            group_id=group_id,
            constants=constants,
            actor_id=actor_id,
            application_id=application_id,
        )
    )
    background_tasks.add_task(invalidate_constant_cache, application_id)
    return result
