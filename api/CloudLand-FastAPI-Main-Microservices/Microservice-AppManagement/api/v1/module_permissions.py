from datetime import datetime, timezone
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, delete

from api.dependencies import CurrentUser, require_tenant
from Models.permission import UserConstantPermission
from Schema.AppManagement.module_permission import (
    ModulePermissionItemDTO,
    ModulePermissionDTO,
    UpdateModulePermissionsRequest,
    EffectivePermissionsResponse,
)
from middleware.uow_middleware import get_current_uow
from services.fusionauth_client import resolve_user_roles_and_groups

router = APIRouter()

# Active system modules currently available
ALL_SYSTEM_MODULES = [
    "user_management",
    "roles_permissions",
    "settings",
    "constants",
    "calendar",
    "contracts",
]


@router.get("/for-role/{role_id}", response_model=list[ModulePermissionItemDTO])
async def get_permissions_for_role(
    role_id: UUID,
    tenant: tuple[UUID, CurrentUser] = Depends(require_tenant),
):
    application_id, current_user = tenant
    uow = get_current_uow()

    stmt = select(UserConstantPermission).where(
        UserConstantPermission.application_id == application_id,
        UserConstantPermission.role_id == role_id,
        UserConstantPermission.module_key.isnot(None),
        UserConstantPermission.action_key.isnot(None),
    )
    result = await uow.session.execute(stmt)
    items = result.scalars().all()
    return [
        ModulePermissionItemDTO(
            module_key=p.module_key,
            action_key=p.action_key,
            has_permission=p.has_permission,
        )
        for p in items
        if p.module_key and p.action_key
    ]


@router.get("/for-user/{user_id}", response_model=list[ModulePermissionItemDTO])
async def get_permissions_for_user(
    user_id: UUID,
    tenant: tuple[UUID, CurrentUser] = Depends(require_tenant),
):
    application_id, current_user = tenant
    uow = get_current_uow()

    stmt = select(UserConstantPermission).where(
        UserConstantPermission.application_id == application_id,
        UserConstantPermission.user_id == user_id,
        UserConstantPermission.module_key.isnot(None),
        UserConstantPermission.action_key.isnot(None),
    )
    result = await uow.session.execute(stmt)
    items = result.scalars().all()
    return [
        ModulePermissionItemDTO(
            module_key=p.module_key,
            action_key=p.action_key,
            has_permission=p.has_permission,
        )
        for p in items
        if p.module_key and p.action_key
    ]


@router.post("/update", response_model=list[ModulePermissionItemDTO])
async def update_module_permissions(
    request: UpdateModulePermissionsRequest,
    tenant: tuple[UUID, CurrentUser] = Depends(require_tenant),
):
    application_id, current_user = tenant
    uow = get_current_uow()

    target_role_id: UUID | None = None
    target_user_id: UUID | None = None

    if request.role_id:
        try:
            target_role_id = UUID(str(request.role_id))
        except (ValueError, TypeError):
            target_role_id = None

    if request.user_id:
        try:
            target_user_id = UUID(str(request.user_id))
        except (ValueError, TypeError):
            target_user_id = None

    if not target_role_id and not target_user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either role_id or user_id must be provided",
        )

    actor_id = current_user.user_id or UUID(int=0)
    now = datetime.now(timezone.utc)

    # 1. Delete existing module permission records for this target from tblUserConstantPermission
    del_stmt = delete(UserConstantPermission).where(
        UserConstantPermission.application_id == application_id,
        UserConstantPermission.module_key.isnot(None),
    )
    if target_role_id:
        del_stmt = del_stmt.where(UserConstantPermission.role_id == target_role_id)
    else:
        del_stmt = del_stmt.where(UserConstantPermission.user_id == target_user_id)

    await uow.session.execute(del_stmt)

    # 2. Insert newly submitted granted module permissions with strict deduplication
    seen_pairs: set[tuple[str, str]] = set()
    created_entities: list[UserConstantPermission] = []
    for item in request.permissions:
        if not item.has_permission:
            continue
        m_key = item.module_key.strip().lower()
        a_key = item.action_key.strip().lower()
        if not m_key or not a_key or (m_key, a_key) in seen_pairs:
            continue
        seen_pairs.add((m_key, a_key))

        entity = UserConstantPermission(
            id=uuid4(),
            application_id=application_id,
            role_id=target_role_id,
            user_id=target_user_id,
            group_id=None,
            constant_id=None,  # Not a constant tree node
            module_key=m_key,
            action_key=a_key,
            has_permission=True,
            create_at=now,
            last_modified_at=now,
            user_created=actor_id,
            last_modified_user=actor_id,
            title="",
            desc=None,
            allow_delete=False,
            allow_update=True,
            disabled=False,
            hidden=False,
        )
        uow.session.add(entity)
        created_entities.append(entity)

    await uow.flush()

    return [
        ModulePermissionItemDTO(
            module_key=e.module_key or "",
            action_key=e.action_key or "",
            has_permission=e.has_permission,
        )
        for e in created_entities
    ]


@router.get("/my-effective-permissions", response_model=EffectivePermissionsResponse)
async def get_my_effective_permissions(
    tenant: tuple[UUID, CurrentUser] = Depends(require_tenant),
):
    application_id, current_user = tenant
    uow = get_current_uow()

    user_id = current_user.user_id
    roles = current_user.roles or []

    # ── 1. Resolve roles for this specific application ─────────────────────────
    role_ids, _, role_names = await resolve_user_roles_and_groups(user_id, application_id)
    
    # ── 2. Admin shortcut (Scoped to this application!) ──────────────────────
    is_admin = any(r.lower() in ("admin", "superadmin", "super_admin", "مدیر سیستم", "مدیر") for r in role_names)
    if is_admin:
        all_items = []
        for mod in ALL_SYSTEM_MODULES:
            for act in ("*", "view", "create", "edit", "delete", "export", "assign"):
                all_items.append(ModulePermissionItemDTO(module_key=mod, action_key=act, has_permission=True))
        return EffectivePermissionsResponse(
            is_admin=True,
            is_user_locked=False,
            permissions=all_items,
            modules=list(ALL_SYSTEM_MODULES),
        )

    if not user_id:
        return EffectivePermissionsResponse(is_admin=False, is_user_locked=False, permissions=[], modules=["dashboard"])

    # ── 3. Check user-specific overrides ("locked") ────────────────────────────
    # User is locked if they have ANY record in tblUserConstantPermission
    lock_stmt = select(1).where(
        UserConstantPermission.application_id == application_id,
        UserConstantPermission.user_id == user_id
    )
    is_user_locked = (await uow.session.execute(lock_stmt)).scalar() is not None

    perm_dict: dict[tuple[str, str], bool] = {}

    if is_user_locked:
        # ── 4a. User has explicit overrides → honour them exclusively ──────────
        user_stmt = select(UserConstantPermission).where(
            UserConstantPermission.application_id == application_id,
            UserConstantPermission.user_id == user_id,
            UserConstantPermission.module_key.isnot(None),
            UserConstantPermission.action_key.isnot(None),
        )
        user_records = (await uow.session.execute(user_stmt)).scalars().all()
        for p in user_records:
            if p.module_key and p.action_key and p.module_key != "_user_lock":
                perm_dict[(p.module_key.lower(), p.action_key.lower())] = p.has_permission
    else:
        # ── 4b. No user override → inherit from assigned roles ─────────────────
        role_uuids: list[UUID] = []
        for r in role_ids:
            try:
                role_uuids.append(UUID(r))
            except (ValueError, TypeError):
                pass

        if role_uuids:
            role_stmt = select(UserConstantPermission).where(
                UserConstantPermission.application_id == application_id,
                UserConstantPermission.role_id.in_(role_uuids),
                UserConstantPermission.module_key.isnot(None),
                UserConstantPermission.action_key.isnot(None),
            )
            role_records = (await uow.session.execute(role_stmt)).scalars().all()
            for p in role_records:
                if p.module_key and p.action_key:
                    perm_dict[(p.module_key.lower(), p.action_key.lower())] = p.has_permission

    effective_list = [
        ModulePermissionItemDTO(module_key=k[0], action_key=k[1], has_permission=v)
        for k, v in perm_dict.items()
        if v
    ]
    allowed_modules = {"dashboard"}
    for item in effective_list:
        if item.action_key in ("view", "*", "access"):
            allowed_modules.add(item.module_key)

    return EffectivePermissionsResponse(
        is_admin=False,
        is_user_locked=is_user_locked,
        permissions=effective_list,
        modules=list(allowed_modules),
    )
