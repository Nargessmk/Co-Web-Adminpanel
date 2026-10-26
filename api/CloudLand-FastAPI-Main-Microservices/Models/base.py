from uuid import UUID, uuid4
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Integer, Unicode, UnicodeText
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.types import Uuid


class Base(DeclarativeBase):
    pass


class BaseModel(Base):
    __abstract__ = True
    __tenant_scoped__ = True

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    create_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    last_modified_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    user_created: Mapped[UUID] = mapped_column(Uuid, nullable=False)
    last_modified_user: Mapped[UUID] = mapped_column(Uuid, nullable=False)
    application_id: Mapped[UUID | None] = mapped_column(Uuid, nullable=True)
    title: Mapped[str | None] = mapped_column(Unicode, nullable=True)
    desc: Mapped[str | None] = mapped_column(UnicodeText, nullable=True)
    allow_delete: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    allow_update: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    disabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    hidden: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
