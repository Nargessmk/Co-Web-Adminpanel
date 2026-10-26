from pydantic import Field

from Schema.AppManagement.node_objects.base import DropdownOption, NodeObjectDTO, ValidationRule

class FolderDTO(NodeObjectDTO):
    FullName: str | None = None
    Icon: str | None = None
    IconColor: str | None = None
    IsExpand: bool = False
    IconSize: int | None = None

    ValidationRules: list[ValidationRule] = Field(
        default_factory=lambda: [
            ValidationRule(Title="نام پوشه", Name="FullName", InputType="text", Placeholder="نام پوشه را وارد کنید", Icon="folder", IsReadonly=False, IsRequired=True, Disabled=False),
            ValidationRule(Title="آیکن", Name="Icon", InputType="icon-picker", Placeholder="آیکن را انتخاب کنید", Icon="image", IsReadonly=False, IsRequired=False, Disabled=False),
            ValidationRule(Title="رنگ آیکن", Name="IconColor", InputType="color", Placeholder="رنگ آیکن را انتخاب کنید", Icon="palette", IsReadonly=False, IsRequired=False, Disabled=False),
            ValidationRule(Title="اندازه آیکن", Name="IconSize", InputType="number", Placeholder="اندازه آیکن را وارد کنید (پیشفرض: 12)", Icon="ruler", IsReadonly=False, IsRequired=False, Disabled=False),
            ValidationRule(Title="قابل گسترش", Name="IsExpand", InputType="checkbox", Placeholder="", Icon="expand", IsReadonly=False, IsRequired=False, Disabled=False),
        ]
    )
