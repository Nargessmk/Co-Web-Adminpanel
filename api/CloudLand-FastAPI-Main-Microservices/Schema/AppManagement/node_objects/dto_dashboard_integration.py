from pydantic import Field

from Schema.AppManagement.node_objects.base import DropdownOption, NodeObjectDTO, ValidationRule

class DashboardIntegrationDTO(NodeObjectDTO):
    FullName: str | None = None
    GroupField: int | None = None
    ChartCalculationType: int | None = None
    CategoryAxisQuery: str | None = None
    Condition: str | None = None

    ValidationRules: list[ValidationRule] = Field(
        default_factory=lambda: [
            ValidationRule(Title="نام یکپارچه‌سازی", Name="FullName", InputType="text", IsRequired=True, Icon="integration", Placeholder="نام یکپارچه‌سازی داشبورد را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="فیلد گروه‌بندی", Name="GroupField", InputType="dropdown", IsRequired=False, Icon="group", Placeholder="فیلد گروه‌بندی را انتخاب کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="نوع محاسبه نمودار", Name="ChartCalculationType", InputType="dropdown", IsRequired=True, Icon="chart", Placeholder="نوع محاسبه را انتخاب کنید", IsReadonly=False, Disabled=False, Options=[
                DropdownOption(Label="هیچکدام", Value=0),
                DropdownOption(Label="تعداد", Value=1),
                DropdownOption(Label="مجموع", Value=2),
            ]),
            ValidationRule(Title="کوئری محور دسته‌بندی", Name="CategoryAxisQuery", InputType="textarea", IsRequired=False, Icon="query", Placeholder="کوئری محور دسته‌بندی را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="شرط", Name="Condition", InputType="textarea", IsRequired=False, Icon="filter", Placeholder="شرط اعمالی را وارد کنید", IsReadonly=False, Disabled=False),
        ]
    )
