from datetime import datetime
from uuid import UUID

from pydantic import ConfigDict, field_validator

from Schema.base import BaseDTO


class ConstantDTO(BaseDTO):
    model_config = ConfigDict(from_attributes=True)

    parent_id: UUID | None = None
    valid_start_date: str | None = None
    valid_end_date: str | None = None
    value_type: int | None = None
    constant_type: UUID | None = None
    node_type_id: UUID | None = None
    child_must_be_show: bool = True
    constant_value: str | None = None
    icon: str | None = None
    color: str | None = None
    json_data: str | None = None
    priority: int | None = None

    @field_validator("valid_start_date", "valid_end_date", mode="before")
    @classmethod
    def _to_iso_string(cls, value):
        if isinstance(value, datetime):
            return value.isoformat()
        return value