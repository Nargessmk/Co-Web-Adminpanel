from __future__ import annotations

from uuid import UUID

from pydantic import ConfigDict

from Schema.base import BaseDTO


class ConstantRecursiveDTO(BaseDTO):
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
    root_title: str | None = None
    level: int = 0
    rank: str | None = None
    node_type: str | None = None
    priority: int | None = None
