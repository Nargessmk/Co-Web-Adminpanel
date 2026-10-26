from uuid import UUID, uuid4
from datetime import datetime, timezone

from sqlalchemy import select, delete

from core.mediator import IRequestHandler
from core.exceptions import (
    NotFoundError,
    DeleteForbiddenError,
    UpdateForbiddenError,
    ValidationError,
)
from Schema.base import parse_persian
from Schema.AppManagement.folder_constants import FOLDER_LIST, FOLDER_NODE_TYPE_ID
from Schema.AppManagement.node_objects.base import DtoDeserializationError, dumps_dto, loads_dto, set_base_dto_fields
from services.dto_type_service import get_dto_type_service
from services.persian_calendar_generator import get_year_days
from services.elastic_client import (
    index_constant,
    delete_constant,
    index_calendar,
    delete_calendar,
    bulk_index,
    INDEX_CALENDAR,
)
from services.redis_client import invalidate_calendar_cache
from middleware.uow_middleware import get_current_uow
from Models.constant import Constant
from Models.calendar import Calendar
from Models.permission import UserConstantPermission
from Schema.AppManagement.constant import ConstantDTO
from Schema.AppManagement.calendar import CalendarDTO, persian_to_gregorian
from Schema.AppManagement.permission import UserConstantPermissionDTO
from application.commands import (
    CreateConstantCommand,
    UpdateConstantCommand,
    DeleteConstantCommand,
    DeleteAllChildConstantsCommand,
    StoreJsonDataCommand,
    CreateCalendarEntryCommand,
    UpdateCalendarEntryCommand,
    DeleteCalendarEntryCommand,
    GenerateCalendarCommand,
    UpdateConstantPermissionCommand,
)


def _parse_datetime(value):
    if isinstance(value, datetime):
        return value
    if isinstance(value, str) and value:
        parsed = parse_persian(value)
        if parsed is not None:
            return parsed
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None
    return None


async def _find_tenant_constant(uow, constant_id: UUID | None, app_id: UUID | None):
    """Find a Constant scoped to the given application_id."""
    if constant_id is None:
        return None
    entity = await uow.constants.find(constant_id)
    if entity is None:
        return None
    if app_id is not None and entity.application_id != app_id:
        return None
    return entity


async def _find_calendar(uow, calendar_id: UUID | None) -> Calendar | None:
    """
    Find a Calendar entry by id. Calendar is a shared, tenant-agnostic table.
    """
    if calendar_id is None:
        return None
    return await uow.calendars.find(calendar_id)


# ---------------------------------------------------------------------------
# Constant handlers
# ---------------------------------------------------------------------------

class CreateConstantHandler(IRequestHandler[CreateConstantCommand, ConstantDTO | None]):
    async def handle(self, request: CreateConstantCommand) -> ConstantDTO | None:
        uow = get_current_uow()

        duplicate_stmt = select(Constant).where(
            Constant.title == request.dto.title,
            Constant.parent_id == request.dto.parent_id,
        )
        if request.application_id is not None:
            duplicate_stmt = duplicate_stmt.where(
                Constant.application_id == request.application_id
            )
        duplicate = (await uow.session.execute(duplicate_stmt)).scalar_one_or_none()
        if duplicate is not None:
            return None

        node_type_id = request.dto.node_type_id
        node_type = None
        if node_type_id is not None:
            node_type = await _find_tenant_constant(
                uow, node_type_id, request.application_id
            )

        if request.dto.parent_id is not None:
            parent = await _find_tenant_constant(
                uow, request.dto.parent_id, request.application_id
            )
            if parent is None:
                return None
            if node_type_id is None:
                node_type_id = parent.node_type_id or parent.id

        allow_delete = request.dto.allow_delete if request.dto.allow_delete is not None else (node_type.allow_delete if node_type else True)
        allow_update = request.dto.allow_update if request.dto.allow_update is not None else (node_type.allow_update if node_type else True)
        disabled = request.dto.disabled if request.dto.disabled is not None else (node_type.disabled if node_type else False)
        hidden = request.dto.hidden if request.dto.hidden is not None else (node_type.hidden if node_type else False)

        now = datetime.now(timezone.utc)
        user_id = request.user_id or UUID(int=0)

        entity = Constant(
            parent_id=request.dto.parent_id,
            title=request.dto.title,
            desc=request.dto.desc,
            value_type=request.dto.value_type,
            constant_type=request.dto.constant_type,
            node_type_id=node_type_id,
            child_must_be_show=True if request.dto.child_must_be_show is None else request.dto.child_must_be_show,
            constant_value=request.dto.constant_value or request.dto.title,
            icon=request.dto.icon or "folder",
            color=request.dto.color or "#47466d",
            json_data=request.dto.json_data,
            priority=request.dto.priority or 0,
            valid_start_date=_parse_datetime(request.dto.valid_start_date),
            valid_end_date=_parse_datetime(request.dto.valid_end_date),
            allow_delete=allow_delete,
            allow_update=allow_update,
            disabled=disabled,
            hidden=hidden,
            create_at=now,
            last_modified_at=now,
            user_created=user_id,
            last_modified_user=user_id,
            application_id=request.application_id,
            version=1,
        )
        await uow.constants.add(entity)
        await uow.flush()
        if entity.node_type_id is not None:
            await _create_folder_constants(
                uow, entity, request.user_id, request.application_id
            )
        dto = ConstantDTO.model_validate(entity)
        await index_constant(dto)
        return dto


async def _create_folder_constants(
    uow, constant: Constant, user_id: UUID, app_id: UUID | None
) -> None:
    matching = [f for f in FOLDER_LIST if f.parent_node_type_id == constant.node_type_id]
    if not matching:
        return

    for folder in matching:
        await uow.constants.add(
            Constant(
                title=folder.folder_title,
                icon=folder.folder_icon,
                color="#93bee6",
                parent_id=constant.id,
                node_type_id=FOLDER_NODE_TYPE_ID,
                constant_value="Folder",
                allow_delete=False,
                allow_update=True,
                disabled=False,
                hidden=False,
                child_must_be_show=True,
                user_created=user_id,
                last_modified_user=user_id,
                application_id=app_id,
            )
        )


class UpdateConstantHandler(IRequestHandler[UpdateConstantCommand, ConstantDTO]):
    async def handle(self, request: UpdateConstantCommand) -> ConstantDTO:
        uow = get_current_uow()
        entity = await _find_tenant_constant(uow, request.id, request.application_id)
        if entity is None:
            raise NotFoundError(f"Constant {request.id} not found")

        if not entity.allow_update or not entity.allow_delete:
            raise UpdateForbiddenError(
                f"ویرایش ثابت «{entity.title}» غیرفعال است؛ این رکورد قفل سیستمی بوده و تغییر آن تنها از طریق پایگاه داده امکان‌پذیر است."
            )

        dto = request.dto
        updates = dto.model_dump(exclude_unset=True)
        if "parent_id" in updates and updates["parent_id"] is not None:
            parent = await _find_tenant_constant(
                uow, updates["parent_id"], request.application_id
            )
            if parent is None:
                raise NotFoundError(f"Parent constant {updates['parent_id']} not found")
        for field in (
            "title",
            "icon",
            "color",
            "parent_id",
            "constant_value",
            "json_data",
            "desc",
            "value_type",
            "node_type_id",
            "constant_type",
            "priority",
            "allow_delete",
            "allow_update",
            "hidden",
            "disabled",
            "child_must_be_show",
        ):
            if field in updates and updates[field] is not None:
                setattr(entity, field, updates[field])
        entity.last_modified_user = request.user_id or UUID(int=0)
        entity.last_modified_at = datetime.now(timezone.utc)
        entity.version = (entity.version or 1) + 1

        if entity.id == entity.node_type_id:
            stmt = select(Constant).where(
                Constant.node_type_id == entity.id,
                Constant.id != entity.id,
            )
            if request.application_id is not None:
                stmt = stmt.where(Constant.application_id == request.application_id)
            related = (await uow.session.execute(stmt)).scalars().all()
            for related_constant in related:
                related_constant.color = entity.color
                related_constant.icon = entity.icon
                related_constant.constant_value = entity.constant_value
                related_constant.allow_delete = entity.allow_delete
                related_constant.allow_update = entity.allow_update
                related_constant.disabled = entity.disabled
                related_constant.hidden = entity.hidden
                related_constant.last_modified_user = request.user_id

        await uow.constants.update(entity)
        await uow.flush()
        dto = ConstantDTO.model_validate(entity)
        await index_constant(dto)
        return dto


class DeleteConstantHandler(IRequestHandler[DeleteConstantCommand, bool]):
    async def handle(self, request: DeleteConstantCommand) -> bool:
        uow = get_current_uow()
        entity = await _find_tenant_constant(uow, request.id, request.application_id)
        if entity is None:
            return True

        if not entity.allow_delete or not entity.allow_update:
            raise DeleteForbiddenError(
                f"حذف ثابت «{entity.title}» غیرفعال است؛ این رکورد قفل سیستمی بوده و حذف آن تنها از طریق پایگاه داده امکان‌پذیر است."
            )

        await _cascade_delete_constants(uow, request.id, request.application_id)
        await uow.session.execute(
            delete(UserConstantPermission).where(UserConstantPermission.constant_id == request.id)
        )
        await uow.constants.delete(request.id)
        await delete_constant(request.id)
        return True


async def _cascade_delete_constants(uow, root_id: UUID, application_id: UUID | None) -> None:
    """Delete all descendants of a constant, leaf-first."""
    boundary = [root_id]
    descendants: list[UUID] = []
    while boundary:
        stmt = select(Constant.id).where(Constant.parent_id.in_(boundary))
        if application_id is not None:
            stmt = stmt.where(Constant.application_id == application_id)
        child_ids = list((await uow.session.execute(stmt)).scalars().all())
        if not child_ids:
            break
        descendants.extend(child_ids)
        boundary = child_ids

    for constant_id in reversed(descendants):
        child = await _find_tenant_constant(uow, constant_id, application_id)
        if child and (not child.allow_delete or not child.allow_update):
            raise DeleteForbiddenError(
                f"امکان حذف وجود ندارد؛ زیرشاخه «{child.title}» قفل سیستمی بوده و غیرقابل حذف است."
            )
        await uow.session.execute(
            delete(UserConstantPermission).where(UserConstantPermission.constant_id == constant_id)
        )
        await uow.constants.delete(constant_id)
        await delete_constant(constant_id)


class DeleteAllChildConstantsHandler(IRequestHandler[DeleteAllChildConstantsCommand, bool]):
    async def handle(self, request: DeleteAllChildConstantsCommand) -> bool:
        uow = get_current_uow()
        parent = await _find_tenant_constant(
            uow, request.parent_id, request.application_id
        )
        if parent is None:
            return False

        await _cascade_delete_constants(uow, request.parent_id, request.application_id)
        return True


class StoreJsonDataHandler(IRequestHandler[StoreJsonDataCommand, bool]):
    async def handle(self, request: StoreJsonDataCommand) -> bool:
        if not request.node_type or not request.node_type.strip():
            raise ValidationError("Node type cannot be null or empty.")
        if not request.data_object or not request.data_object.strip():
            raise ValidationError("DataObject cannot be null or empty.")

        uow = get_current_uow()
        constant = await _find_tenant_constant(
            uow, request.node_id, request.application_id
        )
        if constant is None or constant.parent_id is None:
            return False

        dto_type = get_dto_type_service().resolve_dto_type(request.node_type)
        try:
            dto = loads_dto(dto_type, request.data_object)
        except DtoDeserializationError as e:
            raise ValidationError(str(e))

        basic_errors = dto.basic_errors()
        if basic_errors:
            raise ValidationError("\n".join(basic_errors))
        custom_errors = dto.is_valid(dto)
        if custom_errors:
            raise ValidationError("\n".join(custom_errors))

        set_base_dto_fields(dto, request.user_id)
        constant.json_data = dumps_dto(dto)
        await uow.constants.update(constant)
        return True


# ---------------------------------------------------------------------------
# Calendar handlers — Calendar is a shared, tenant-agnostic table.
# No Constant mirroring.  No application_id filtering.
# ---------------------------------------------------------------------------

class CreateCalendarEntryHandler(IRequestHandler[CreateCalendarEntryCommand, CalendarDTO | None]):
    async def handle(self, request: CreateCalendarEntryCommand) -> CalendarDTO | None:
        uow = get_current_uow()

        # Prevent duplicate entries for the same date within the same tenant
        parsed_date = persian_to_gregorian(request.dto.date)
        if parsed_date is None:
            raise ValidationError(f"Invalid date: {request.dto.date!r}")

        existing_stmt = select(Calendar.id).where(Calendar.date == parsed_date)
        existing_id = (await uow.session.execute(existing_stmt)).scalar_one_or_none()
        if existing_id is not None:
            return None  # Duplicate — same behaviour as before

        # Validate parent_id tenant isolation
        if request.dto.parent_id is not None:
            parent = await _find_tenant_constant(uow, request.dto.parent_id, request.application_id)
            if parent is None:
                raise NotFoundError(f"Parent constant {request.dto.parent_id} not found")

        title = request.dto.title or request.dto.occasion or "Calendar Entry"

        calendar = Calendar(
            title=title,
            date=parsed_date,
            occasion=request.dto.occasion,
            additional_description=request.dto.additional_description,
            is_holiday=request.dto.is_holiday,
            is_thursday=request.dto.is_thursday,
            is_friday=request.dto.is_friday,
            user_created=request.user_id,
            last_modified_user=request.user_id,
        )
        await uow.calendars.add(calendar)
        await uow.flush()
        dto = CalendarDTO.model_validate(calendar)
        await index_calendar(dto)
        await invalidate_calendar_cache()
        return dto


class UpdateCalendarEntryHandler(IRequestHandler[UpdateCalendarEntryCommand, CalendarDTO]):
    async def handle(self, request: UpdateCalendarEntryCommand) -> CalendarDTO:
        uow = get_current_uow()
        existing = await _find_calendar(uow, request.id)
        if existing is None:
            raise NotFoundError(f"Calendar with Id {request.id} not found")

        if request.dto.date:
            parsed = persian_to_gregorian(request.dto.date)
            if parsed is not None:
                existing.date = parsed
        existing.title = request.dto.title or request.dto.occasion or existing.title
        existing.occasion = request.dto.occasion or existing.occasion
        existing.additional_description = (
            request.dto.additional_description or existing.additional_description
        )
        existing.is_holiday = request.dto.is_holiday
        existing.is_thursday = request.dto.is_thursday
        existing.is_friday = request.dto.is_friday
        existing.last_modified_at = datetime.now(timezone.utc)
        existing.last_modified_user = request.user_id

        await uow.calendars.update(existing)
        await uow.flush()
        dto = CalendarDTO.model_validate(existing)
        await index_calendar(dto)
        await invalidate_calendar_cache()
        return dto


class DeleteCalendarEntryHandler(IRequestHandler[DeleteCalendarEntryCommand, bool]):
    async def handle(self, request: DeleteCalendarEntryCommand) -> bool:
        uow = get_current_uow()
        existing = await _find_calendar(uow, request.id)
        if existing is None:
            raise NotFoundError(f"Calendar with Id {request.id} not found")

        await uow.calendars.delete(request.id)
        await uow.flush()
        await delete_calendar(request.id)
        await invalidate_calendar_cache()
        return True


class GenerateCalendarHandler(IRequestHandler[GenerateCalendarCommand, int]):
    async def handle(self, request: GenerateCalendarCommand) -> int:
        uow = get_current_uow()

        # Validate parent_id belongs to the authenticated tenant
        if request.parent_id is not None:
            parent = await _find_tenant_constant(uow, request.parent_id, request.application_id)
            if parent is None:
                raise NotFoundError(f"Parent constant {request.parent_id} not found")

        day_infos = get_year_days(request.year)

        # Fetch all existing calendars for the requested year dates within the same tenant
        dates = [day_info.Date for day_info in day_infos]
        existing_stmt = select(Calendar).where(Calendar.date.in_(dates))
        existing_calendars = list(
            (await uow.session.execute(existing_stmt)).scalars().all()
        )
        existing_by_date: dict[datetime, Calendar] = {
            cal.date: cal for cal in existing_calendars
        }

        new_calendars: list[Calendar] = []
        updated_calendars: list[Calendar] = []

        for day_info in day_infos:
            existing = existing_by_date.get(day_info.Date)

            if existing is not None:
                existing.title = day_info.Title
                existing.occasion = day_info.Occasion
                existing.is_holiday = day_info.IsHoliday
                existing.is_thursday = day_info.IsThursday
                existing.is_friday = day_info.IsFriday
                existing.last_modified_at = datetime.now(timezone.utc)
                existing.last_modified_user = request.user_id
                await uow.calendars.update(existing)
                updated_calendars.append(existing)
                continue

            calendar = Calendar(
                title=day_info.Title,
                date=day_info.Date,
                occasion=day_info.Occasion,
                is_holiday=day_info.IsHoliday,
                is_thursday=day_info.IsThursday,
                is_friday=day_info.IsFriday,
                user_created=request.user_id,
                last_modified_user=request.user_id,
                application_id=request.application_id,
            )
            new_calendars.append(calendar)

        for calendar in new_calendars:
            await uow.calendars.add(calendar)
        await uow.flush()

        all_dtos = [CalendarDTO.model_validate(c) for c in new_calendars + updated_calendars]
        if all_dtos:
            await bulk_index(
                INDEX_CALENDAR,
                [(d.id, d.model_dump(by_alias=True, mode="json")) for d in all_dtos],
            )
        await invalidate_calendar_cache()
        return len(new_calendars)


# ---------------------------------------------------------------------------
# Permission handler
# ---------------------------------------------------------------------------

class UpdateConstantPermissionHandler(
    IRequestHandler[UpdateConstantPermissionCommand, list[UserConstantPermissionDTO]]
):
    async def handle(self, request: UpdateConstantPermissionCommand) -> list[UserConstantPermissionDTO]:
        uow = get_current_uow()

        stmt = select(UserConstantPermission).where(
            UserConstantPermission.constant_id.isnot(None)
        )
        if request.application_id is not None:
            stmt = stmt.where(
                UserConstantPermission.application_id == request.application_id
            )
        if request.user_id is not None:
            stmt = stmt.where(UserConstantPermission.user_id == request.user_id)
        if request.role_id is not None:
            stmt = stmt.where(UserConstantPermission.role_id == request.role_id)
        if request.group_id is not None:
            stmt = stmt.where(UserConstantPermission.group_id == request.group_id)
        result = await uow.session.execute(stmt)
        exists_items = list(result.scalars().all())

        requested = set(request.constants)
        existing_ids = {p.constant_id for p in exists_items if p.constant_id is not None}
        to_remove = [p for p in exists_items if (p.constant_id or UUID(int=0)) not in requested]
        for p in to_remove:
            await uow.session.delete(p)

        valid_ids: set[UUID] = set()
        if requested:
            valid_stmt = select(Constant.id).where(Constant.id.in_(list(requested)))
            if request.application_id is not None:
                valid_stmt = valid_stmt.where(
                    Constant.application_id == request.application_id
                )
            valid_ids = set((await uow.session.execute(valid_stmt)).scalars().all())

        now = datetime.now(timezone.utc)
        new_entities: list[UserConstantPermission] = []
        for constant_id in request.constants:
            if constant_id in existing_ids or constant_id not in valid_ids:
                continue
            entity = UserConstantPermission(
                id=uuid4(),
                user_id=request.user_id,
                group_id=request.group_id,
                role_id=request.role_id,
                create_at=now,
                last_modified_at=now,
                constant_id=constant_id,
                user_created=request.actor_id,
                last_modified_user=request.actor_id,
                application_id=request.application_id,
                title="",
                disabled=False,
                allow_delete=False,
                hidden=False,
            )
            uow.session.add(entity)
            new_entities.append(entity)

        await uow.flush()
        from services.redis_client import invalidate_constant_cache
        await invalidate_constant_cache()
        result_entities = [p for p in exists_items if p not in to_remove] + new_entities
        return [UserConstantPermissionDTO.model_validate(e) for e in result_entities]