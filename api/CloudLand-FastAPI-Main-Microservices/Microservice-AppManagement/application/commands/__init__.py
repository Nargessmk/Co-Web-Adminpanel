from uuid import UUID
from dataclasses import dataclass, field

from Schema.AppManagement.constant import ConstantDTO
from Schema.AppManagement.calendar import CalendarDTO
from Schema.AppManagement.permission import UserConstantPermissionDTO
from core.mediator import Request, Notification


@dataclass
class UpdateConstantPermissionCommand(Request[list[UserConstantPermissionDTO]]):
    user_id: UUID | None = None
    role_id: UUID | None = None
    group_id: UUID | None = None
    constants: list[UUID] = field(default_factory=list)
    actor_id: UUID = UUID(int=0)
    application_id: UUID | None = None


@dataclass
class CreateConstantCommand(Request[ConstantDTO | None]):
    dto: ConstantDTO
    user_id: UUID
    application_id: UUID | None = None


@dataclass
class UpdateConstantCommand(Request[ConstantDTO]):
    id: UUID
    dto: ConstantDTO
    user_id: UUID
    application_id: UUID | None = None


@dataclass
class DeleteConstantCommand(Request[bool]):
    id: UUID
    user_id: UUID
    application_id: UUID | None = None


@dataclass
class DeleteAllChildConstantsCommand(Request[bool]):
    parent_id: UUID
    user_id: UUID
    application_id: UUID | None = None


@dataclass
class StoreJsonDataCommand(Request[bool]):
    node_id: UUID
    node_type: str | None
    data_object: str
    user_id: UUID
    application_id: UUID | None = None


@dataclass
class CreateCalendarEntryCommand(Request[CalendarDTO | None]):
    dto: CalendarDTO
    user_id: UUID


@dataclass
class UpdateCalendarEntryCommand(Request[CalendarDTO]):
    id: UUID
    dto: CalendarDTO
    user_id: UUID


@dataclass
class DeleteCalendarEntryCommand(Request[bool]):
    id: UUID
    user_id: UUID


@dataclass
class GenerateCalendarCommand(Request[int]):
    year: int
    parent_id: UUID
    node_type_id: UUID | None = None
    user_id: UUID = UUID(int=0)


@dataclass
class ConstantChangedNotification(Notification):
    constant_id: UUID
    action: str
    user_id: UUID
