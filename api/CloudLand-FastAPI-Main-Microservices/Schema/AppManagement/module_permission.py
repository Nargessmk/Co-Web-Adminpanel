from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, AliasChoices


def _camel(name: str) -> str:
    """Convert snake_case to camelCase for JSON serialization (JS-friendly)."""
    parts = name.split("_")
    return parts[0] + "".join(p.capitalize() for p in parts[1:])


class ModulePermissionItemDTO(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        alias_generator=_camel,
        # Serialize with camelCase aliases so frontend receives moduleKey, actionKey etc.
        ser_json_by_alias=True,
    )

    module_key: str = Field(
        validation_alias=AliasChoices("module_key", "moduleKey", "ModuleKey")
    )
    action_key: str = Field(
        validation_alias=AliasChoices("action_key", "actionKey", "ActionKey")
    )
    has_permission: bool = Field(
        default=True,
        validation_alias=AliasChoices("has_permission", "hasPermission", "HasPermission"),
    )


class ModulePermissionDTO(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        alias_generator=_camel,
        ser_json_by_alias=True,
    )

    id: UUID | None = None
    application_id: UUID | None = None
    role_id: UUID | None = None
    user_id: UUID | None = None
    module_key: str
    action_key: str
    has_permission: bool = True


class UpdateModulePermissionsRequest(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        alias_generator=_camel,
    )

    role_id: UUID | str | None = Field(
        default=None,
        validation_alias=AliasChoices("role_id", "roleId", "RoleId"),
    )
    user_id: UUID | str | None = Field(
        default=None,
        validation_alias=AliasChoices("user_id", "userId", "UserId"),
    )
    permissions: list[ModulePermissionItemDTO] = Field(
        default_factory=list,
        validation_alias=AliasChoices("permissions", "Permissions"),
    )


class EffectivePermissionsResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        alias_generator=_camel,
        ser_json_by_alias=True,
    )

    is_admin: bool = False
    is_user_locked: bool = False
    permissions: list[ModulePermissionItemDTO] = []
    modules: list[str] = []
