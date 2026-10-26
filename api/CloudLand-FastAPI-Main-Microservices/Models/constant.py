from uuid import UUID
from datetime import datetime

from sqlalchemy import Boolean, Unicode, UnicodeText, Integer, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Uuid

from Models.base import BaseModel


class Constant(BaseModel):
    __tablename__ = "tblConstant"

    parent_id: Mapped[UUID | None] = mapped_column(
        Uuid, ForeignKey("tblConstant.id"), nullable=True
    )
    parent_constant: Mapped["Constant | None"] = relationship(
        "Constant", remote_side="Constant.id", backref="children", lazy="selectin"
    )
    valid_start_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    valid_end_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    value_type: Mapped[int | None] = mapped_column(Integer, nullable=True)
    constant_type: Mapped[UUID | None] = mapped_column(Uuid, nullable=True)
    node_type_id: Mapped[UUID | None] = mapped_column(Uuid, nullable=True)
    child_must_be_show: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    constant_value: Mapped[str | None] = mapped_column(UnicodeText, nullable=True)
    icon: Mapped[str | None] = mapped_column(Unicode(100), nullable=True)
    color: Mapped[str | None] = mapped_column(Unicode(100), nullable=True)
    json_data: Mapped[str | None] = mapped_column(UnicodeText, nullable=True)
    priority: Mapped[int | None] = mapped_column(Integer, nullable=True)
