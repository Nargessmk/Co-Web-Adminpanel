from uuid import UUID
from sqlalchemy import BigInteger, Unicode, UnicodeText
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Uuid

from Models.base import BaseModel


class EntityFileAttachment(BaseModel):
    """
    EntityFileAttachment model — stores file metadata and S3 URLs for attached entities.
    Inherits from BaseModel (provides id, create_at, last_modified_at, user_created,
    last_modified_user, application_id, title, desc, allow_delete,
    allow_update, disabled, hidden, version).
    """

    __tablename__ = "tblEntityFileAttachment"

    record_id: Mapped[UUID | None] = mapped_column(Uuid, nullable=True)
    file_url: Mapped[str | None] = mapped_column(UnicodeText, nullable=True)
    file_extension: Mapped[str | None] = mapped_column(Unicode(50), nullable=True)
    original_file_name: Mapped[str | None] = mapped_column(Unicode(255), nullable=True)
    file_size_in_bytes: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
