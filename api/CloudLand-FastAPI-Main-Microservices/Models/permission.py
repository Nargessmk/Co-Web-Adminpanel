from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Uuid

from Models.base import BaseModel

if TYPE_CHECKING:
    from Models.constant import Constant


class UserConstantPermission(BaseModel):
    """
    Unified Application Permission Model (tblUserConstantPermission).
    Manages both:
    1. Constant Tree Permissions (when constant_id is set)
    2. Module & Action Page Permissions (when module_key and action_key are set)
    Supports assignment to roles (role_id), users (user_id), and groups (group_id).
    """
    __tablename__ = "tblUserConstantPermission"

    user_id: Mapped[UUID | None] = mapped_column(Uuid, nullable=True, index=True)
    role_id: Mapped[UUID | None] = mapped_column(Uuid, nullable=True, index=True)
    group_id: Mapped[UUID | None] = mapped_column(Uuid, nullable=True, index=True)

    # Constant hierarchy permission target
    constant_id: Mapped[UUID | None] = mapped_column(
        Uuid, ForeignKey("tblConstant.id"), nullable=True, index=True
    )
    constant: Mapped["Constant | None"] = relationship(
        "Constant", lazy="selectin"
    )

    # Module & Action page permission targets
    module_key: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    action_key: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)

    has_permission: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
