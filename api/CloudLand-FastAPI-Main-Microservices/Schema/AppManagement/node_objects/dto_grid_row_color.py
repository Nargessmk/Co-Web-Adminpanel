from pydantic import Field

from Schema.AppManagement.node_objects.base import NodeObjectDTO, ValidationRule

class GridRowColorDTO(NodeObjectDTO):
    RowColorColumnName: int | None = None
    RowColorColumnFullName: str | None = None
    RowColorOperator: str | None = None
    RowColorColumnValue: str | None = None
    RowColorOperator2: str | None = None
    RowColorColumnValue2: str | None = None
    RowColorSelectedColor: str | None = None

    ValidationRules: list[ValidationRule] = Field(
        default_factory=lambda: [
            ValidationRule(Title="نام کامل ستون", Name="RowColorColumnFullName", InputType="text", IsRequired=False, Icon="column", Placeholder="نام کامل ستون را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="نام ستون", Name="RowColorColumnName", InputType="dropdown", IsRequired=True, Icon="field-select", Placeholder="ستون مورد نظر را انتخاب کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="نوع عملگر", Name="RowColorOperator", InputType="dropdown", IsRequired=False, Icon="operator", Placeholder="عملگر را انتخاب کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="مقدار ستون", Name="RowColorColumnValue", InputType="text", IsRequired=False, Icon="value", Placeholder="مقدار مقایسه را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="نوع عملگر دوم", Name="RowColorOperator2", InputType="dropdown", IsRequired=False, Icon="operator", Placeholder="عملگر دوم را انتخاب کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="مقدار ستون دوم", Name="RowColorColumnValue2", InputType="text", IsRequired=False, Icon="value", Placeholder="مقدار مقایسه دوم را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="رنگ سطر", Name="RowColorSelectedColor", InputType="dropdown", IsRequired=True, Icon="color", Placeholder="رنگ سطر را انتخاب کنید", IsReadonly=False, Disabled=False),
        ]
    )
