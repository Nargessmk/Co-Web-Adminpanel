from pydantic import Field

from Schema.AppManagement.node_objects.base import NodeObjectDTO, ValidationRule

class NewButtonFormDTO(NodeObjectDTO):
    UseUrl: bool = False
    Url: str | None = None
    RelatedInformationForm: int | None = None
    FullName: str | None = None
    Icon: str | None = None

    ValidationRules: list[ValidationRule] = Field(
        default_factory=lambda: [
            ValidationRule(Title="نام دکمه", Name="FullName", InputType="text", IsRequired=True, Icon="button", Placeholder="نام دکمه را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="آیکن", Name="Icon", InputType="icon-picker", IsRequired=False, Icon="image", Placeholder="آیکن را انتخاب کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="استفاده از لینک", Name="UseUrl", InputType="checkbox", IsRequired=False, Icon="link", Placeholder="", IsReadonly=False, Disabled=False),
            ValidationRule(Title="فرم مرتبط", Name="RelatedInformationForm", InputType="dropdown", IsRequired=False, Icon="form", Placeholder="فرم مرتبط را انتخاب کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="آدرس لینک", Name="Url", InputType="url", IsRequired=False, Icon="link", Placeholder="آدرس URL را وارد کنید", IsReadonly=False, Disabled=False),
        ]
    )
