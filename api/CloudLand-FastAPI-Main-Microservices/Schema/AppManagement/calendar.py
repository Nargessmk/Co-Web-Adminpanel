"""
CalendarDTO — data-transfer object for the shared Calendar table.

Intentionally does NOT include application_id,
parent_id, or node_type_id because Calendar is a shared,
tenant-agnostic entity.
"""

from datetime import datetime
from uuid import UUID

import jdatetime
from pydantic import ConfigDict, field_validator

from Schema.base import BaseDTO

_DATE_FORMAT = "%Y/%m/%d"


def persian_to_gregorian(value: str) -> datetime | None:
    try:
        return jdatetime.datetime.strptime(value, _DATE_FORMAT).togregorian()
    except (ValueError, TypeError):
        return None


def gregorian_to_persian(value: datetime) -> str:
    return jdatetime.datetime.fromgregorian(datetime=value).strftime(_DATE_FORMAT)


class CalendarDTO(BaseDTO):
    model_config = ConfigDict(from_attributes=True)

    date: str = ""
    occasion: str | None = None
    additional_description: str | None = None
    is_holiday: bool = False
    is_thursday: bool = False
    is_friday: bool = False
    parent_id: UUID | None = None

    @field_validator("date", mode="before")
    @classmethod
    def _normalize_date(cls, value: object) -> object:
        if isinstance(value, datetime):
            return gregorian_to_persian(value)
        return value or ""
