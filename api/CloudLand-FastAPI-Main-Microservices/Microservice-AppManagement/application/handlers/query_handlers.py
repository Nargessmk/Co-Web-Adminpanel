from uuid import UUID
from datetime import datetime
import json

from sqlalchemy import select, func, or_, text
from core.config import get_settings
from core.mediator import IRequestHandler
from core.exceptions import ValidationError
from middleware.uow_middleware import get_current_uow
from Schema.paged_result import PagedResult
from Schema.AppManagement.node_objects.base import DtoDeserializationError, dump_dto_public, loads_dto
from services.dto_type_service import get_dto_type_service
from services.redis_client import cache_get, cache_remove, cache_set
from services.persian_calendar_generator import get_day_info
from Models.constant import Constant
from Models.calendar import Calendar
from Models.permission import UserConstantPermission
from Schema.AppManagement.constant import ConstantDTO
from Schema.AppManagement.constant_recursive import ConstantRecursiveDTO
from Schema.AppManagement.calendar import CalendarDTO
from application.queries import (
    GetConstantQuery,
    GetRootConstantsQuery,
    GetRootConstantPagingQuery,
    GetChildConstantsQuery,
    GetConstantsByIdsQuery,
    GetConstantsRecursiveQuery,
    GetConstantsRecursiveWithPermissionsQuery,
    GetConstantByDateQuery,
    GetAllConstantsQuery,
    GetTreeConstantQuery,
    GetConstantNodeTypeQuery,
    RetrieveJsonDataQuery,
    GetCalendarEntryQuery,
    GetCalendarPagingQuery,
    GetCalendarDayInfoQuery,
)


def _cache_key(prefix: str, identifier: str | UUID, application_id: UUID | None) -> str:
    app_part = str(application_id) if application_id is not None else "all"
    return f"Constants_{prefix}_{identifier}_App_{app_part}"


async def _cached_get(prefix: str, identifier: str | UUID, application_id: UUID | None, settings, ttl: int | None = None, require_allowed_root: bool = False, root_id_for_allowed_check: UUID | None = None):
    check_id = str(root_id_for_allowed_check) if root_id_for_allowed_check is not None else str(identifier)
    if require_allowed_root and check_id not in settings.constants_cache_allowed_root_ids_list:
        return None
    key = _cache_key(prefix, identifier, application_id)
    cached = await cache_get(key)
    if cached:
        try:
            return json.loads(cached)
        except Exception:
            await cache_remove(key)
    return None


async def _cached_set(prefix: str, identifier: str | UUID, application_id: UUID | None, data, settings, ttl: int | None = None, require_allowed_root: bool = False, root_id_for_allowed_check: UUID | None = None):
    check_id = str(root_id_for_allowed_check) if root_id_for_allowed_check is not None else str(identifier)
    if require_allowed_root and check_id not in settings.constants_cache_allowed_root_ids_list:
        return
    key = _cache_key(prefix, identifier, application_id)
    expiration = ttl or settings.constants_cache_expiration_minutes * 60
    serialized = json.dumps(data, ensure_ascii=False, default=str)
    await cache_set(key, serialized, expiration)


async def _find_tenant_constant(uow, constant_id: UUID | None, app_id: UUID | None):
    if constant_id is None:
        return None
    entity = await uow.constants.find(constant_id)
    if entity is None:
        return None
    if app_id is not None and entity.application_id != app_id:
        return None
    return entity


async def _find_calendar(uow, calendar_id: UUID | None) -> "Calendar | None":
    """
    Find a Calendar entry by id. Calendar is a shared, tenant-agnostic table.
    """
    if calendar_id is None:
        return None
    return await uow.calendars.find(calendar_id)


class GetConstantHandler(IRequestHandler[GetConstantQuery, ConstantDTO | None]):
    async def handle(self, request: GetConstantQuery) -> ConstantDTO | None:
        uow = get_current_uow()
        settings = get_settings()
        cached = await _cached_get("ById", request.id, request.application_id, settings, require_allowed_root=False)
        if cached is not None:
            return ConstantDTO(**cached)
        entity = await _find_tenant_constant(uow, request.id, request.application_id)
        if entity is None:
            return None
        dto = ConstantDTO.model_validate(entity)
        await _cached_set("ById", request.id, request.application_id, dto.model_dump(mode="json"), settings, require_allowed_root=False)
        return dto


class GetAllConstantsHandler(IRequestHandler[GetAllConstantsQuery, list[ConstantDTO]]):
    async def handle(self, request: GetAllConstantsQuery) -> list[ConstantDTO]:
        uow = get_current_uow()
        settings = get_settings()
        cache_id = "all"
        cached = await _cached_get("All", cache_id, request.application_id, settings, require_allowed_root=False)
        if cached is not None:
            return [ConstantDTO(**item) for item in cached]
        stmt = select(Constant).order_by(Constant.priority)
        if request.application_id is not None:
            stmt = stmt.where(Constant.application_id == request.application_id)
        result = await uow.session.execute(stmt)
        entities = result.scalars().all()
        dtos = [ConstantDTO.model_validate(e) for e in entities]
        await _cached_set("All", cache_id, request.application_id, [d.model_dump(mode="json") for d in dtos], settings, require_allowed_root=False)
        return dtos


class GetRootConstantsHandler(IRequestHandler[GetRootConstantsQuery, list[ConstantDTO]]):
    async def handle(self, request: GetRootConstantsQuery) -> list[ConstantDTO]:
        uow = get_current_uow()
        settings = get_settings()
        cache_id = "root"
        cached = await _cached_get("Root", cache_id, request.application_id, settings, require_allowed_root=False)
        if cached is not None:
            return [ConstantDTO(**item) for item in cached]
        stmt = select(Constant).where(Constant.parent_id.is_(None)).order_by(Constant.priority)
        if request.application_id is not None:
            stmt = stmt.where(Constant.application_id == request.application_id)
        result = await uow.session.execute(stmt)
        entities = result.scalars().all()
        dtos = [ConstantDTO.model_validate(e) for e in entities]
        await _cached_set("Root", cache_id, request.application_id, [d.model_dump(mode="json") for d in dtos], settings, require_allowed_root=False)
        return dtos


class GetRootConstantPagingHandler(
    IRequestHandler[GetRootConstantPagingQuery, PagedResult[ConstantDTO]]
):
    async def handle(self, request: GetRootConstantPagingQuery) -> PagedResult[ConstantDTO]:
        uow = get_current_uow()
        settings = get_settings()
        cache_id = f"Paging_{request.root_id}_{request.page_number}_{request.page_size}"
        cached = await _cached_get("RootPaging", cache_id, request.application_id, settings, require_allowed_root=True, root_id_for_allowed_check=request.root_id)
        if cached is not None:
            return PagedResult[ConstantDTO](**cached)
        conditions = [Constant.parent_id == request.root_id]
        if request.application_id is not None:
            conditions.append(Constant.application_id == request.application_id)
        total = await uow.session.scalar(
            select(func.count())
            .select_from(Constant)
            .where(*conditions)
        )
        stmt = (
            select(Constant)
            .where(*conditions)
            .order_by(Constant.priority)
            .offset((request.page_number - 1) * request.page_size)
            .limit(request.page_size)
        )
        result = await uow.session.execute(stmt)
        entities = result.scalars().all()
        dtos = [ConstantDTO.model_validate(e) for e in entities]
        paged = PagedResult[ConstantDTO](
            items=dtos,
            total_count=int(total or 0),
            page_index=request.page_number,
            page_size=request.page_size,
        )
        await _cached_set("RootPaging", cache_id, request.application_id, paged.model_dump(mode="json"), settings, require_allowed_root=True, root_id_for_allowed_check=request.root_id)
        return paged


class GetChildConstantsHandler(IRequestHandler[GetChildConstantsQuery, list[ConstantDTO]]):
    async def handle(self, request: GetChildConstantsQuery) -> list[ConstantDTO]:
        uow = get_current_uow()
        settings = get_settings()
        cache_id = request.root_id
        cached = await _cached_get("ChildsByRootId", cache_id, request.application_id, settings, require_allowed_root=True)
        if cached is not None:
            return [ConstantDTO(**item) for item in cached]
        stmt = select(Constant).where(Constant.parent_id == request.root_id).order_by(Constant.priority)
        if request.application_id is not None:
            stmt = stmt.where(Constant.application_id == request.application_id)
        result = await uow.session.execute(stmt)
        entities = result.scalars().all()
        dtos = [ConstantDTO.model_validate(e) for e in entities]
        await _cached_set("ChildsByRootId", cache_id, request.application_id, [d.model_dump(mode="json") for d in dtos], settings, require_allowed_root=True)
        return dtos


class GetConstantsByIdsHandler(IRequestHandler[GetConstantsByIdsQuery, list[ConstantDTO]]):
    async def handle(self, request: GetConstantsByIdsQuery) -> list[ConstantDTO]:
        uow = get_current_uow()
        settings = get_settings()
        cache_id = ",".join(str(i) for i in sorted(request.ids))
        cached = await _cached_get("ByIds", cache_id, request.application_id, settings, require_allowed_root=False)
        if cached is not None:
            return [ConstantDTO(**item) for item in cached]
        valid_ids = [i for i in dict.fromkeys(request.ids) if i != UUID(int=0)]
        stmt = (
            select(Constant)
            .where(Constant.id.in_(valid_ids))
            .order_by(Constant.priority, Constant.title)
        )
        if request.application_id is not None:
            stmt = stmt.where(Constant.application_id == request.application_id)
        result = await uow.session.execute(stmt)
        entities = result.scalars().all()
        dtos = [ConstantDTO.model_validate(e) for e in entities]
        await _cached_set("ByIds", cache_id, request.application_id, [d.model_dump(mode="json") for d in dtos], settings, require_allowed_root=False)
        return dtos


def _build_flat_tree(
    nodes: dict[UUID, dict],
    root_id: UUID,
    root_title: str,
    level: int = 1,
    rank: str = "1",
) -> list[ConstantRecursiveDTO]:
    root = nodes.get(root_id)
    if root is None:
        return []

    dto = ConstantRecursiveDTO(
        id=root["id"],
        parent_id=root["parent_id"],
        title=root["title"],
        desc=root["desc"],
        valid_start_date=root["valid_start_date"],
        valid_end_date=root["valid_end_date"],
        value_type=root["value_type"],
        constant_type=root["constant_type"],
        node_type_id=root["node_type_id"],
        child_must_be_show=root["child_must_be_show"],
        constant_value=root["constant_value"],
        icon=root["icon"],
        color=root["color"],
        root_title=root_title,
        level=level,
        rank=rank,
        priority=root["priority"],
    )

    result = [dto]
    for index, child_id in enumerate(root["children"], start=1):
        result.extend(
            _build_flat_tree(nodes, child_id, root_title, level + 1, f"{rank}.{index}")
        )
    return result


def _load_tree_rows(rows: list[Constant]) -> dict[UUID, dict]:
    nodes: dict[UUID, dict] = {}
    for entity in rows:
        nodes[entity.id] = {
            "id": entity.id,
            "parent_id": entity.parent_id,
            "title": entity.title,
            "desc": entity.desc,
            "valid_start_date": (
                entity.valid_start_date.isoformat() if entity.valid_start_date else None
            ),
            "valid_end_date": (
                entity.valid_end_date.isoformat() if entity.valid_end_date else None
            ),
            "value_type": entity.value_type,
            "constant_type": entity.constant_type,
            "node_type_id": entity.node_type_id,
            "child_must_be_show": entity.child_must_be_show,
            "constant_value": entity.constant_value,
            "icon": entity.icon,
            "color": entity.color,
            "priority": entity.priority,
            "children": [],
        }

    for entity_id, node in nodes.items():
        parent_id = node["parent_id"]
        if parent_id is not None and parent_id in nodes:
            nodes[parent_id]["children"].append(entity_id)

    return nodes


async def _load_subtree(uow, root_id: UUID, app_id: UUID | None = None) -> list[Constant]:
    ids = [root_id]
    rows: list[Constant] = []
    while ids:
        stmt = (
            select(Constant)
            .where(Constant.parent_id.in_(ids))
            .order_by(Constant.priority, Constant.title)
        )
        if app_id is not None:
            stmt = stmt.where(Constant.application_id == app_id)
        result = await uow.session.execute(stmt)
        children = list(result.scalars().all())
        if not children:
            break
        rows.extend(children)
        ids = [c.id for c in children]
    return rows


def _is_mssql(uow) -> bool:
    return uow.session.bind is not None and uow.session.bind.dialect.name == "mssql"


def _function_rows_to_dtos(rows) -> list[ConstantRecursiveDTO]:
    dtos: list[ConstantRecursiveDTO] = []
    for row in rows:
        data = dict(row)
        for key in ("ValidStartDate", "ValidEndDate"):
            value = data.get(key)
            if isinstance(value, datetime):
                data[key] = value.isoformat()
        dtos.append(ConstantRecursiveDTO.model_validate(data))
    return dtos


class GetConstantsRecursiveHandler(
    IRequestHandler[GetConstantsRecursiveQuery, list[ConstantRecursiveDTO]]
):
    async def handle(self, request: GetConstantsRecursiveQuery) -> list[ConstantRecursiveDTO]:
        uow = get_current_uow()
        settings = get_settings()
        cached = await _cached_get("Recursive", request.root_id, request.application_id, settings, require_allowed_root=True)
        if cached is not None:
            return [ConstantRecursiveDTO(**item) for item in cached]
        if _is_mssql(uow):
            result = await uow.session.execute(
                text("SELECT * FROM dbo.GetConstantsRecursive(:root_id, :app_id)"),
                {"root_id": request.root_id, "app_id": request.application_id},
            )
            dtos = _function_rows_to_dtos(result.mappings().all())
            await _cached_set("Recursive", request.root_id, request.application_id, [d.model_dump(mode="json") for d in dtos], settings, require_allowed_root=True)
            return dtos

        root = await _find_tenant_constant(uow, request.root_id, request.application_id)
        if root is None:
            return []

        rows = [root] + await _load_subtree(uow, request.root_id, request.application_id)
        nodes = _load_tree_rows(rows)
        dtos = _build_flat_tree(nodes, request.root_id, root.title or "")
        await _cached_set("Recursive", request.root_id, request.application_id, [d.model_dump(mode="json") for d in dtos], settings, require_allowed_root=True)
        return dtos


class GetConstantByDateHandler(IRequestHandler[GetConstantByDateQuery, list[ConstantRecursiveDTO]]):
    async def handle(self, request: GetConstantByDateQuery) -> list[ConstantRecursiveDTO]:
        uow = get_current_uow()
        settings = get_settings()
        target_date = request.date_time.date().isoformat()
        cache_id = f"{request.root_id}_{target_date}"
        cached = await _cached_get("ByDate", cache_id, request.application_id, settings, require_allowed_root=True, root_id_for_allowed_check=request.root_id)
        if cached is not None:
            return [ConstantRecursiveDTO(**item) for item in cached]
        root = await _find_tenant_constant(uow, request.root_id, request.application_id)
        if root is None:
            return []

        rows = [root] + await _load_subtree(uow, request.root_id, request.application_id)
        nodes = _load_tree_rows(rows)
        flat = _build_flat_tree(nodes, request.root_id, root.title or "")

        target = request.date_time
        if target.tzinfo is not None:
            target = target.astimezone().replace(tzinfo=None)

        def _naive(value: datetime) -> datetime:
            return value.replace(tzinfo=None) if value.tzinfo is not None else value

        filtered_ids = {
            row.id
            for row in rows
            if row.valid_start_date is not None
            and row.valid_end_date is not None
            and _naive(row.valid_start_date) <= target <= _naive(row.valid_end_date)
        }
        dtos = [dto for dto in flat if dto.id in filtered_ids]
        await _cached_set("ByDate", cache_id, request.application_id, [d.model_dump(mode="json") for d in dtos], settings, require_allowed_root=True, root_id_for_allowed_check=request.root_id)
        return dtos


class GetTreeConstantHandler(IRequestHandler[GetTreeConstantQuery, list[ConstantDTO]]):
    async def handle(self, request: GetTreeConstantQuery) -> list[ConstantDTO]:
        uow = get_current_uow()
        settings = get_settings()
        cached = await _cached_get("TreeView", request.root_id, request.application_id, settings, require_allowed_root=False)
        if cached is not None:
            return [ConstantDTO(**item) for item in cached]
        entity = await _find_tenant_constant(uow, request.root_id, request.application_id)
        if entity is None:
            return []
        dtos = [ConstantDTO.model_validate(entity)]
        await _cached_set("TreeView", request.root_id, request.application_id, [d.model_dump(mode="json") for d in dtos], settings, require_allowed_root=False)
        return dtos


class GetConstantNodeTypeHandler(IRequestHandler[GetConstantNodeTypeQuery, list[ConstantDTO]]):
    SPECIAL_NODE_TYPE_ID = UUID("ec640c73-0bda-42ee-b7f7-f946ea3354dd")

    async def handle(self, request: GetConstantNodeTypeQuery) -> list[ConstantDTO]:
        uow = get_current_uow()
        settings = get_settings()

        if request.node_type_id is None:
            cache_id = f"NodeType_{request.node_id}_none"
            cached = await _cached_get("NodeType", cache_id, request.application_id, settings, require_allowed_root=False)
            if cached is not None:
                return [ConstantDTO(**item) for item in cached]
            entity = await _find_tenant_constant(uow, request.node_id, request.application_id)
            if entity is None:
                raise RuntimeError(f"Constant {request.node_id} not found")
            dto = ConstantDTO.model_validate(entity)
            dto.title = "افزودن جدید"
            dtos = [dto]
            await _cached_set("NodeType", cache_id, request.application_id, [d.model_dump(mode="json") for d in dtos], settings, require_allowed_root=False)
            return dtos

        cache_id = f"{request.node_id}_{request.node_type_id}"
        cached = await _cached_get("NodeType", cache_id, request.application_id, settings, require_allowed_root=False)
        if cached is not None:
            return [ConstantDTO(**item) for item in cached]

        if request.node_type_id == self.SPECIAL_NODE_TYPE_ID:
            current_node_type_id: UUID | None = request.node_type_id
            current_id: UUID | None = request.node_id
            while current_node_type_id == self.SPECIAL_NODE_TYPE_ID:
                constant = await _find_tenant_constant(uow, current_id, request.application_id)
                if constant is None or constant.parent_id is None:
                    break
                parent = await _find_tenant_constant(uow, constant.parent_id, request.application_id)
                if parent is None:
                    break
                current_id = parent.id
                current_node_type_id = parent.node_type_id
            if current_node_type_id is None:
                return []
            node_type_id: UUID = current_node_type_id
        else:
            node_type_id = request.node_type_id

        stmt = (
            select(Constant)
            .where(
                (Constant.parent_id == node_type_id) | (Constant.id == node_type_id)
            )
            .order_by(Constant.priority)
        )
        if request.application_id is not None:
            stmt = stmt.where(Constant.application_id == request.application_id)
        result = await uow.session.execute(stmt)
        entities = result.scalars().all()
        dtos = [ConstantDTO.model_validate(e) for e in entities]
        await _cached_set("NodeType", cache_id, request.application_id, [d.model_dump(mode="json") for d in dtos], settings, require_allowed_root=False)
        return dtos


class GetConstantsRecursiveWithPermissionsHandler(
    IRequestHandler[GetConstantsRecursiveWithPermissionsQuery, list[ConstantRecursiveDTO]]
):
    async def handle(
        self, request: GetConstantsRecursiveWithPermissionsQuery
    ) -> list[ConstantRecursiveDTO]:
        uow = get_current_uow()
        settings = get_settings()
        cache_id = f"Perm_{request.root_id}_{request.user_id}_{request.role_id or 'none'}_{request.group_id or 'none'}"
        cached = await _cached_get("RecursivePerm", cache_id, request.application_id, settings, require_allowed_root=True, root_id_for_allowed_check=request.root_id)
        if cached is not None:
            return [ConstantRecursiveDTO(**item) for item in cached]
        if _is_mssql(uow):
            role_ids = list(request.role_ids) or ([request.role_id] if request.role_id else [])
            group_ids = list(request.group_ids) or ([request.group_id] if request.group_id else [])
            result = await uow.session.execute(
                text(
                    "SELECT * FROM dbo.GetConstantsRecursiveWithPermissions("
                    ":root_id, :user_id, :role_ids, :group_ids, :app_id)"
                ),
                {
                    "root_id": request.root_id,
                    "user_id": request.user_id,
                    "role_ids": ",".join(str(r) for r in role_ids) if role_ids else None,
                    "group_ids": ",".join(str(g) for g in group_ids) if group_ids else None,
                    "app_id": request.application_id,
                },
            )
            dtos = _function_rows_to_dtos(result.mappings().all())
            await _cached_set("RecursivePerm", cache_id, request.application_id, [d.model_dump(mode="json") for d in dtos], settings, require_allowed_root=True, root_id_for_allowed_check=request.root_id)
            return dtos

        root = await _find_tenant_constant(uow, request.root_id, request.application_id)
        if root is None:
            return []

        rows = [root] + await _load_subtree(uow, request.root_id, request.application_id)

        permission_stmt = select(UserConstantPermission.constant_id).where(
            UserConstantPermission.constant_id.in_([r.id for r in rows])
        )
        if request.application_id is not None:
            permission_stmt = permission_stmt.where(
                UserConstantPermission.application_id == request.application_id
            )
        conditions = []
        is_locked = False
        if request.user_id is not None:
            lock_stmt = select(1).where(
                UserConstantPermission.user_id == request.user_id
            )
            if request.application_id is not None:
                lock_stmt = lock_stmt.where(UserConstantPermission.application_id == request.application_id)
            if (await uow.session.execute(lock_stmt)).scalar() is not None:
                is_locked = True
                conditions.append(UserConstantPermission.user_id == request.user_id)

        if not is_locked:
            if request.role_ids:
                conditions.append(UserConstantPermission.role_id.in_(request.role_ids))
            elif request.role_id is not None:
                conditions.append(UserConstantPermission.role_id == request.role_id)
            if request.group_ids:
                conditions.append(UserConstantPermission.group_id.in_(request.group_ids))
            elif request.group_id is not None:
                conditions.append(UserConstantPermission.group_id == request.group_id)

        if not conditions:
            return []

        permission_stmt = permission_stmt.where(or_(*conditions))
        permitted_ids = set(
            (await uow.session.execute(permission_stmt)).scalars().all()
        )
        if not permitted_ids:
            return []

        nodes = _load_tree_rows(rows)
        included: set[UUID] = set()
        for node_id in permitted_ids:
            current: UUID | None = node_id
            while current is not None and current in nodes:
                included.add(current)
                current = nodes[current]["parent_id"]

        filtered_rows = [r for r in rows if r.id in included]
        nodes = _load_tree_rows(filtered_rows)
        dtos = _build_flat_tree(nodes, request.root_id, root.title or "")
        await _cached_set("RecursivePerm", cache_id, request.application_id, [d.model_dump(mode="json") for d in dtos], settings, require_allowed_root=True, root_id_for_allowed_check=request.root_id)
        return dtos


class GetCalendarEntryHandler(IRequestHandler[GetCalendarEntryQuery, CalendarDTO | None]):
    async def handle(self, request: GetCalendarEntryQuery) -> CalendarDTO | None:
        uow = get_current_uow()
        # Calendar reads always go directly to the database — no cache.
        entity = await _find_calendar(uow, request.id)
        if entity is None:
            return None
        return CalendarDTO.model_validate(entity)


class GetCalendarPagingHandler(IRequestHandler[GetCalendarPagingQuery, PagedResult[CalendarDTO]]):
    async def handle(self, request: GetCalendarPagingQuery) -> PagedResult[CalendarDTO]:
        uow = get_current_uow()
        # Calendar reads always go directly to the database — no cache.
        from persiantools.jdatetime import JalaliDate
        start_d = JalaliDate(request.year, 1, 1).to_gregorian()
        end_d = JalaliDate(request.year + 1, 1, 1).to_gregorian()
        start = datetime(start_d.year, start_d.month, start_d.day)
        end = datetime(end_d.year, end_d.month, end_d.day)
        conditions = [Calendar.date >= start, Calendar.date < end]
        total = await uow.session.scalar(
            select(func.count())
            .select_from(Calendar)
            .where(*conditions)
        )
        stmt = (
            select(Calendar)
            .where(*conditions)
            .order_by(Calendar.date)
            .offset((request.page_number - 1) * request.page_size)
            .limit(request.page_size)
        )
        result = await uow.session.execute(stmt)
        entities = result.scalars().all()
        return PagedResult[CalendarDTO](
            items=[CalendarDTO.model_validate(e) for e in entities],
            total_count=int(total or 0),
            page_index=request.page_number,
            page_size=request.page_size,
        )


class GetCalendarDayInfoHandler(IRequestHandler[GetCalendarDayInfoQuery, dict | None]):
    async def handle(self, request: GetCalendarDayInfoQuery) -> dict | None:
        uow = get_current_uow()
        # Calendar reads always go directly to the database — no cache.
        from persiantools.jdatetime import JalaliDate, JalaliDateTime

        try:
            parts = [int(p) for p in request.date_str.split("/")]
            if len(parts) != 3:
                return None
            gregorian_dt = JalaliDate(parts[0], parts[1], parts[2]).to_gregorian()
        except (ValueError, TypeError, IndexError):
            return None

        date_only = datetime(gregorian_dt.year, gregorian_dt.month, gregorian_dt.day)
        stmt = select(Calendar).where(Calendar.date == date_only)
        entity = (await uow.session.execute(stmt)).scalar_one_or_none()

        if entity is not None:
            return {
                "date": request.date_str,
                "is_holiday": entity.is_holiday,
                "is_workday": not entity.is_holiday,
                "title": entity.title,
                "occasion": entity.occasion,
                "is_thursday": entity.is_thursday,
                "is_friday": entity.is_friday,
            }

        # Fallback: compute on-the-fly if date not in DB
        day_info = get_day_info(date_only.date())
        return {
            "date": request.date_str,
            "is_holiday": day_info.IsHoliday,
            "is_workday": not day_info.IsHoliday,
            "title": day_info.Title,
            "occasion": day_info.Occasion,
            "is_thursday": day_info.IsThursday,
            "is_friday": day_info.IsFriday,
        }


class RetrieveJsonDataQueryHandler(IRequestHandler[RetrieveJsonDataQuery, dict | None]):
    async def handle(self, request: RetrieveJsonDataQuery) -> dict | None:
        if not request.node_type or not request.node_type.strip():
            raise ValidationError("Node type cannot be null or empty.")

        dto_type = get_dto_type_service().resolve_dto_type(request.node_type)
        uow = get_current_uow()
        settings = get_settings()
        cache_id = f"{request.node_id}_{request.node_type}"
        cached = await _cached_get("JsonData", cache_id, request.application_id, settings, require_allowed_root=False)
        if cached is not None:
            return cached
        constant = await _find_tenant_constant(uow, request.node_id, request.application_id)
        if constant is None:
            return None

        if not constant.json_data:
            result = dump_dto_public(dto_type())
            await _cached_set("JsonData", cache_id, request.application_id, result, settings, require_allowed_root=False)
            return result

        try:
            dto = loads_dto(dto_type, constant.json_data)
        except DtoDeserializationError as e:
            raise ValidationError(str(e))
        result = dump_dto_public(dto)
        await _cached_set("JsonData", cache_id, request.application_id, result, settings, require_allowed_root=False)
        return result