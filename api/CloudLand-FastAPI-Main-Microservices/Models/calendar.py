"""
Calendar model — shared across all tenants.

Calendar is completely independent from BaseModel and does NOT have
application_id. It defines all fields manually.

This table is shared across all tenants and does not require
any tenant isolation.
"""

from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, Integer, Unicode, UnicodeText
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.types import Uuid


class _CalendarBase(DeclarativeBase):
    pass


class Calendar(_CalendarBase):
    __tablename__ = "tblCalendar"

    # Primary key
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)

    # Audit fields
    create_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    last_modified_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    user_created: Mapped[UUID] = mapped_column(Uuid, nullable=False)
    last_modified_user: Mapped[UUID] = mapped_column(Uuid, nullable=False)

    # Content fields
    title: Mapped[str | None] = mapped_column(Unicode, nullable=True)
    desc: Mapped[str | None] = mapped_column(UnicodeText, nullable=True)

    # Soft delete / update control
    allow_delete: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    allow_update: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    disabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    hidden: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    # Calendar specific fields
    date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    occasion: Mapped[str | None] = mapped_column(Unicode(4000), nullable=True)
    additional_description: Mapped[str | None] = mapped_column(
        UnicodeText, nullable=True
    )
    is_holiday: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    is_thursday: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    is_friday: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
