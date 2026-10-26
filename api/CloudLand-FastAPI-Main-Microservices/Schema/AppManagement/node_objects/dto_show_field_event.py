from pydantic import Field

from Schema.AppManagement.node_objects.base import NodeObjectDTO, ValidationRule

class ShowFieldEventDTO(NodeObjectDTO):
    FieldValue: str | None = None
    SelectedConstantID: int | None = None
    ShowObject: bool = False

    ValidationRules: list[ValidationRule] = Field(
        default_factory=lambda: [
            ValidationRule(Title="مقدار فیلد", Name="FieldValue", InputType="text", IsRequired=False, Icon="field-value", Placeholder="مقدار فیلد را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="انتخابی", Name="SelectedConstantID", InputType="selectbox", IsRequired=False, Icon="object-select", Placeholder="آیتم را انتخاب کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="وضعیت نمایش", Name="ShowObject", InputType="switch", IsRequired=False, Icon="visibility", Placeholder="", IsReadonly=False, Disabled=False),
        ]
    )
