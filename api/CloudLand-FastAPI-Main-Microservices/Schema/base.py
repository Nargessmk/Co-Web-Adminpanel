from datetime import datetime
from uuid import UUID
from typing import Any

import jdatetime
from pydantic import BaseModel, ConfigDict, field_serializer, model_validator

_PERSIAN_FORMAT = "%Y/%m/%d %H:%M:%S"
_PERSIAN_DATE_FORMAT = "%Y/%m/%d"


def dotnet_pascal(name: str) -> str:
    if not name:
        return name
    if name in ("title", "desc", "hidden", "level"):
        return name
    if "_" in name:
        return "".join(part[:1].upper() + part[1:] for part in name.split("_"))
    return name[:1].upper() + name[1:]


def datetime_to_persian(value: datetime) -> str:
    return jdatetime.datetime.fromgregorian(datetime=value).strftime(_PERSIAN_FORMAT)


def parse_persian(value: str) -> datetime | None:
    for fmt in (_PERSIAN_FORMAT, _PERSIAN_DATE_FORMAT):
        try:
            return jdatetime.datetime.strptime(value, fmt).togregorian()
        except ValueError:
            continue
    return None


class BaseDTO(BaseModel):
    model_config = ConfigDict(
        from_attributes=True, arbitrary_types_allowed=True, populate_by_name=True, alias_generator=dotnet_pascal
    )

    @model_validator(mode="before")
    @classmethod
    def _normalize_input_keys(cls, data: object) -> object:
        if not isinstance(data, dict):
            return data
        lookup: dict[str, str] = {}
        for name, field in cls.model_fields.items():
            lookup[name.casefold()] = name
            if field.alias:
                lookup[field.alias.casefold()] = name
        return {lookup.get(key.casefold(), key): value for key, value in data.items()}

    id: UUID | None = None
    title: str | None = None
    desc: str | None = None
    create_at: datetime | str | None = None
    last_modified_at: datetime | str | None = None
    user_created: UUID | None = None
    last_modified_user: UUID | None = None
    application_id: UUID | None = None
    allow_delete: bool | None = None
    allow_update: bool | None = None
    disabled: bool | None = None
    hidden: bool | None = None

    @field_serializer("create_at", "last_modified_at")
    def serialize_datetime(self, value: datetime | str | None) -> str:
        if isinstance(value, datetime):
            return datetime_to_persian(value)
        return value or ""