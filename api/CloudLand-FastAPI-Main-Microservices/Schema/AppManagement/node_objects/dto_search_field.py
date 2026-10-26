from pydantic import Field

from Schema.AppManagement.node_objects.base import NodeObjectDTO, ValidationRule

class SearchFieldDTO(NodeObjectDTO):
    RelatedField: int | None = None
    DefaultOperator: str | None = None
    DefaultValue: str | None = None
    ShowField: bool = False
    ShowOperator: bool = False

    ValidationRules: list[ValidationRule] = Field(
        default_factory=lambda: [
            ValidationRule(Title="فیلد مرتبط", Name="RelatedField", InputType="selectbox", IsRequired=True, Icon="field-link", Placeholder="فیلد مرتبط را انتخاب کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="عملگر پیشفرض", Name="DefaultOperator", InputType="selectbox", IsRequired=True, Icon="operator", Placeholder="عملگر را انتخاب کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="مقدار پیشفرض", Name="DefaultValue", InputType="text", IsRequired=True, Icon="default-value", Placeholder="مقدار پیشفرض را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="نمایش فیلد", Name="ShowField", InputType="switch", IsRequired=True, Icon="eye", Placeholder="", IsReadonly=False, Disabled=False),
            ValidationRule(Title="نمایش عملگر", Name="ShowOperator", InputType="switch", IsRequired=True, Icon="operator-visibility", Placeholder="", IsReadonly=False, Disabled=False),
        ]
    )
