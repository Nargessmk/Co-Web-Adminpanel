from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from api.dependencies import CurrentUser, require_admin, require_tenant, require_user
from Schema.AppManagement.calendar import CalendarDTO
from Schema.paged_result import PagedResult
from application.queries import GetCalendarEntryQuery, GetCalendarPagingQuery, GetCalendarDayInfoQuery
from application.commands import (
    CreateCalendarEntryCommand,
    UpdateCalendarEntryCommand,
    DeleteCalendarEntryCommand,
    GenerateCalendarCommand,
)
from core.mediator import get_mediator
from core.exceptions import NotFoundError

router = APIRouter()


@router.get("/ById/{entry_id}", response_model=CalendarDTO)
async def get_calendar_entry(
    entry_id: UUID,
    current_user: CurrentUser = Depends(require_user),
):
    mediator = get_mediator()
    result = await mediator.send(GetCalendarEntryQuery(id=entry_id))
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return result


@router.get("/Paging/{year}/{page_number}/{page_size}", response_model=PagedResult[CalendarDTO])
async def get_calendar_paging(
    year: int,
    page_number: int,
    page_size: int,
    current_user: CurrentUser = Depends(require_user),
):
    if year < 1300 or year > 1500:
        raise HTTPException(status_code=400, detail="Year must be between 1300 and 1500")
    mediator = get_mediator()
    return await mediator.send(
        GetCalendarPagingQuery(year=year, page_number=page_number, page_size=page_size)
    )


@router.get("/DayInfo/{date_str:path}", response_model=dict)
async def get_calendar_day_info(
    date_str: str,
    current_user: CurrentUser = Depends(require_user),
):
    mediator = get_mediator()
    result = await mediator.send(GetCalendarDayInfoQuery(date_str=date_str))
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid date format. Expected YYYY/MM/DD")
    return result


@router.post("/Generate/{year}/{parent_id}")
async def generate_calendar(
    year: int,
    parent_id: UUID,
    node_type_id: UUID | None = None,
    _admin: CurrentUser = Depends(require_admin),
    tenant: tuple[UUID, CurrentUser] = Depends(require_tenant),
):
    if year < 1300 or year > 1500:
        raise HTTPException(status_code=400, detail="Year must be between 1300 and 1500")
    application_id, current_user = tenant
    mediator = get_mediator()
    user_id = current_user.user_id or UUID(int=0)
    command = GenerateCalendarCommand(
        year=year,
        parent_id=parent_id,
        node_type_id=node_type_id,
        user_id=user_id,
        application_id=application_id,
    )
    return await mediator.send(command)


@router.post("/", response_model=CalendarDTO)
async def create_calendar_entry(
    dto: CalendarDTO,
    _admin: CurrentUser = Depends(require_admin),
    tenant: tuple[UUID, CurrentUser] = Depends(require_tenant),
):
    application_id, current_user = tenant
    mediator = get_mediator()
    user_id = current_user.user_id or UUID(int=0)
    result = await mediator.send(CreateCalendarEntryCommand(dto=dto, user_id=user_id, application_id=application_id))
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Calendar entry already exists for this date or invalid data",
        )
    return result


@router.put("/", response_model=CalendarDTO)
async def update_calendar_entry(
    dto: CalendarDTO,
    _admin: CurrentUser = Depends(require_admin),
    tenant: tuple[UUID, CurrentUser] = Depends(require_tenant),
):
    application_id, current_user = tenant
    mediator = get_mediator()
    user_id = current_user.user_id or UUID(int=0)
    if dto.id is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    try:
        return await mediator.send(UpdateCalendarEntryCommand(id=dto.id, dto=dto, user_id=user_id, application_id=application_id))
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_calendar_entry(
    entry_id: UUID,
    _admin: CurrentUser = Depends(require_admin),
    tenant: tuple[UUID, CurrentUser] = Depends(require_tenant),
):
    application_id, current_user = tenant
    mediator = get_mediator()
    user_id = current_user.user_id or UUID(int=0)
    try:
        await mediator.send(DeleteCalendarEntryCommand(id=entry_id, user_id=user_id, application_id=application_id))
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
