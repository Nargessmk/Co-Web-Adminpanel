from uuid import UUID

from pydantic import BaseModel, ConfigDict

from Schema.base import dotnet_pascal


class UserConstantPermissionDTO(BaseModel):
    model_config = ConfigDict(
        from_attributes=True, populate_by_name=True, alias_generator=dotnet_pascal
    )

    user_id: UUID | None = None
    role_id: UUID | None = None
    group_id: UUID | None = None
    has_permission: bool = True
    constant_id: UUID | None = None
    module_key: str | None = None
    action_key: str | None = None
    application_id: UUID | None = None
