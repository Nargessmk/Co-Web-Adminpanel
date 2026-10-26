import json
import re
from datetime import datetime, timezone
from typing import Any, ClassVar, get_args
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, ValidationError as PydanticValidationError

from Schema.base import dotnet_pascal

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+$")

ZERO_UUID = UUID(int=0)


class DtoDeserializationError(ValueError):
    pass


class DropdownOption(BaseModel):
    model_config = ConfigDict(alias_generator=dotnet_pascal, populate_by_name=True)

    Label: str = ""
    Value: int = 0


class ValidationRule(BaseModel):
    model_config = ConfigDict(alias_generator=dotnet_pascal, populate_by_name=True)

    Title: str = ""
    Name: str = ""
    InputType: str = ""
    Placeholder: str = ""
    Icon: str | None = None
    IsReadonly: bool = False
    IsRequired: bool = False
    Disabled: bool = False
    Options: list[DropdownOption] | None = None


class NodeObjectDTO(BaseModel):
    model_config = ConfigDict(extra="ignore", alias_generator=dotnet_pascal, populate_by_name=True)

    Id: UUID | None = None
    CreateAt: str = ""
    LastModifiedAt: str = ""
    UserCreated: UUID | None = None
    LastModifiedUser: UUID | None = None
    ApplicationId: UUID | str | None = None
    title: str | None = None
    desc: str | None = None
    AllowDelete: bool = False
    AllowUpdate: bool = False
    Disabled: bool = False
    hidden: bool = False
    ValidationRules: list[ValidationRule] = Field(default_factory=list)

    REQUIRED_FIELDS: ClassVar[tuple[str, ...]] = ()

    def basic_errors(self) -> list[str]:
        return [
            f"The {name} field is required."
            for name in self.REQUIRED_FIELDS
            if getattr(self, name, None) in (None, False)
        ]

    def is_valid(self, original: "NodeObjectDTO | None" = None) -> list[str]:
        errors: list[str] = []
        for rule in self.ValidationRules:
            if not hasattr(self, rule.Name):
                continue
            current = getattr(self, rule.Name)
            if original is not None and (rule.IsReadonly or rule.Disabled):
                if current != getattr(original, rule.Name):
                    errors.append(f"فیلد '{rule.Title}' قابل ویرایش نیست.")
                    continue
            if rule.IsRequired and _is_missing(current):
                errors.append(f"فیلد '{rule.Title}' الزامی است.")
                continue
            if current is None or (isinstance(current, str) and not current.strip()):
                continue
            input_type = rule.InputType.lower()
            if input_type == "number":
                try:
                    int(str(current))
                except ValueError:
                    errors.append(f"مقدار وارد شده برای '{rule.Title}' باید یک عدد معتبر باشد.")
            elif input_type == "email" and isinstance(current, str) and not EMAIL_PATTERN.match(current):
                errors.append(f"فرمت ایمیل برای فیلد '{rule.Title}' نامعتبر است.")
        return errors


def _is_missing(value: Any) -> bool:
    if isinstance(value, str):
        return not value.strip()
    if isinstance(value, int) and not isinstance(value, bool):
        return value == 0
    return value is None


def _child_model(field: Any) -> type[BaseModel] | None:
    annotation = field.annotation
    args = get_args(annotation)
    candidate = args[0] if args else annotation
    if isinstance(candidate, type) and issubclass(candidate, (NodeObjectDTO, ValidationRule, DropdownOption)):
        return candidate
    return None


def _casefold_keys(data: Any, model: type[BaseModel]) -> Any:
    if isinstance(data, list):
        return [_casefold_keys(item, model) for item in data]
    if not isinstance(data, dict):
        return data
    lookup = {name.casefold(): name for name in model.model_fields}
    out: dict[str, Any] = {}
    for key, value in data.items():
        name = lookup.get(key.casefold())
        if name is None:
            out[key] = value
            continue
        out[name] = value
        child = _child_model(model.model_fields[name])
        if child is not None:
            out[name] = _casefold_keys(value, child)
    return out


def loads_dto(dto_type: type[NodeObjectDTO], raw: str) -> NodeObjectDTO:
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise DtoDeserializationError("Invalid JSON data object") from exc
    try:
        return dto_type.model_validate(_casefold_keys(data, dto_type))
    except PydanticValidationError as exc:
        raise DtoDeserializationError(f"Invalid {dto_type.__name__} payload: {exc}") from exc


def dumps_dto(dto: NodeObjectDTO) -> str:
    return dto.model_dump_json(by_alias=False)


def dump_dto_public(dto: NodeObjectDTO) -> dict[str, Any]:
    return dto.model_dump(mode="json", by_alias=True)


def set_base_dto_fields(dto: NodeObjectDTO, user_id: UUID) -> None:
    now = _utc_now_o()
    if dto.Id is None or dto.Id == ZERO_UUID:
        dto.Id = uuid4()
        dto.CreateAt = now
        dto.UserCreated = user_id
    dto.LastModifiedAt = now
    dto.LastModifiedUser = user_id
    dto.AllowDelete = False
    dto.AllowUpdate = True
    dto.Disabled = False
    dto.hidden = False


def _utc_now_o() -> str:
    now = datetime.now(timezone.utc)
    return f"{now:%Y-%m-%dT%H:%M:%S}.{now.microsecond:06d}0Z"
