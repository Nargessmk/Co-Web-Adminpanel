from pydantic import Field

from Schema.AppManagement.node_objects.base import NodeObjectDTO, ValidationRule

class TableFunctionDTO(NodeObjectDTO):
    FullName: str | None = None
    ReturnDataType: str | None = None
    Query: str | None = None

    ValidationRules: list[ValidationRule] = Field(
        default_factory=lambda: [
            ValidationRule(Title="نام تابع", Name="FullName", InputType="text", IsRequired=True, Icon="function", Placeholder="نام تابع را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="نوع داده خروجی", Name="ReturnDataType", InputType="text", IsRequired=True, Icon="data-type", Placeholder="نوع خروجی را انتخاب کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="کوئری تابع", Name="Query", InputType="textarea", IsRequired=True, Icon="sql-query", Placeholder="کوئری SQL تابع را وارد کنید", IsReadonly=False, Disabled=False),
        ]
    )
