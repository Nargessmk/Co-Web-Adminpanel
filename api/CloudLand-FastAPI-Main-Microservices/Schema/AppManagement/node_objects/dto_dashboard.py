from pydantic import Field

from Schema.AppManagement.node_objects.base import NodeObjectDTO, ValidationRule

class DashboardDTO(NodeObjectDTO):
    FullName: str | None = None
    StartDate: str | None = None
    InformationEntryForm: int | None = None
    EndDate: str | None = None
    ShowDate: bool = False

    ValidationRules: list[ValidationRule] = Field(
        default_factory=lambda: [
            ValidationRule(Title="نام داشبورد", Name="FullName", InputType="text", IsRequired=True, Icon="dashboard", Placeholder="نام داشبورد را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="فرم ورود اطلاعات", Name="InformationEntryForm", InputType="dropdown", IsRequired=False, Icon="form", Placeholder="فرم مرتبط را انتخاب کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="تاریخ شروع", Name="StartDate", InputType="date", IsRequired=False, Icon="calendar-start", Placeholder="تاریخ شروع را انتخاب کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="تاریخ پایان", Name="EndDate", InputType="date", IsRequired=False, Icon="calendar-end", Placeholder="تاریخ پایان را انتخاب کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="نمایش تاریخ", Name="ShowDate", InputType="checkbox", IsRequired=False, Icon="calendar", Placeholder="", IsReadonly=False, Disabled=False),
        ]
    )
