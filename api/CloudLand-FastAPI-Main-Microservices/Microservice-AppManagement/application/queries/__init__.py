from uuid import UUID
from dataclasses import dataclass, field
from datetime import datetime

from core.mediator import Request
from Schema.AppManagement.constant import ConstantDTO
from Schema.AppManagement.constant_recursive import ConstantRecursiveDTO
from Schema.AppManagement.calendar import CalendarDTO


@dataclass
class GetConstantQuery(Request[ConstantDTO | None]):
    id: UUID
    application_id: UUID | None = None


@dataclass
class GetAllConstantsQuery(Request[list[ConstantDTO]]):
    application_id: UUID | None = None

@dataclass
class GetRootConstantsQuery(Request[list[ConstantDTO]]):
    application_id: UUID | None = None


@dataclass
class GetRootConstantPagingQuery(Request[list[ConstantDTO]]):
    root_id: UUID
    page_number: int = 1
    page_size: int = 50
    application_id: UUID | None = None


@dataclass
class GetChildConstantsQuery(Request[list[ConstantDTO]]):
    root_id: UUID
    application_id: UUID | None = None


@dataclass
class GetConstantsByIdsQuery(Request[list[ConstantDTO]]):
    ids: list[UUID] = field(default_factory=list)
    application_id: UUID | None = None


@dataclass
class GetConstantsRecursiveQuery(Request[list[ConstantRecursiveDTO]]):
    root_id: UUID
    application_id: UUID | None = None


@dataclass
class GetConstantByDateQuery(Request[list[ConstantRecursiveDTO]]):
    root_id: UUID
    date_time: datetime
    application_id: UUID | None = None


@dataclass
class GetTreeConstantQuery(Request[list[ConstantDTO]]):
    root_id: UUID
    application_id: UUID | None = None


@dataclass
class GetConstantNodeTypeQuery(Request[list[ConstantDTO]]):
    node_id: UUID
    node_type_id: UUID | None = None
    application_id: UUID | None = None


@dataclass
class RetrieveJsonDataQuery(Request[dict | None]):
    node_id: UUID
    node_type: str | None
    application_id: UUID | None = None


@dataclass
class GetConstantsRecursiveWithPermissionsQuery(Request[list[ConstantRecursiveDTO]]):
    root_id: UUID
    user_id: UUID | None = None
    role_id: UUID | None = None
    group_id: UUID | None = None
    role_ids: list[UUID] = field(default_factory=list)
    group_ids: list[UUID] = field(default_factory=list)
    application_id: UUID | None = None


@dataclass
class GetCalendarEntryQuery(Request[CalendarDTO | None]):
    id: UUID
    application_id: UUID | None = None


@dataclass
class GetCalendarPagingQuery(Request[list[CalendarDTO]]):
    year: int
    page_number: int = 1
    page_size: int = 50
    application_id: UUID | None = None


@dataclass
class GetCalendarDayInfoQuery(Request[dict | None]):
    date_str: str
