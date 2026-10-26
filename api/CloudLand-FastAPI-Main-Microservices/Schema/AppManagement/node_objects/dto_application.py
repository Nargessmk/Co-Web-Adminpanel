from uuid import UUID

from pydantic import Field

from Schema.AppManagement.node_objects.base import NodeObjectDTO, ValidationRule

class ApplicationDTO(NodeObjectDTO):
    ApplicationId: UUID | None = None
    Name: str | None = None
    Description: str | None = None
    Active: bool = False

    ValidationRules: list[ValidationRule] = Field(
        default_factory=lambda: [
            ValidationRule(Title="شناسه نرم افزار", Name="ApplicationId", InputType="text", IsRequired=False, Icon="general", Placeholder="", IsReadonly=True, Disabled=False),
            ValidationRule(Title="عنوان نرم افزار", Name="Name", InputType="text", IsRequired=True, Icon="general", Placeholder="عنوان نرم افزار را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="توضیحات نرم افزار", Name="Description", InputType="text", IsRequired=True, Icon="general", Placeholder="توضیحات نرم افزار را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="فعال", Name="Active", InputType="checkbox", IsRequired=False, Icon="general", Placeholder="", IsReadonly=False, Disabled=False),
        ]
    )
