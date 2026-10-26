from pydantic import Field

from Schema.AppManagement.node_objects.base import DropdownOption, NodeObjectDTO, ValidationRule

class PublicJobDTO(NodeObjectDTO):
    FullName: str | None = None
    Query: str | None = None
    StartDate: str | None = None
    EndDate: str | None = None
    StartTime: str | None = None
    EndTime: str | None = None
    RelatedDatasource: int | None = None
    RepeatDay: int | None = None
    RepeatClock: int | None = None
    PublicJobType: int | None = None

    ValidationRules: list[ValidationRule] = Field(
        default_factory=lambda: [
            ValidationRule(Title="نام کار", Name="FullName", InputType="text", IsRequired=True, Icon="job", Placeholder="نام کار را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="نوع عملیات", Name="PublicJobType", InputType="selectbox", IsRequired=True, Icon="job-type", Placeholder="نوع عملیات را انتخاب کنید", IsReadonly=False, Disabled=False, Options=[
                DropdownOption(Label="خالی", Value=0),
                DropdownOption(Label="اجرای_رویداد", Value=1),
                DropdownOption(Label="ارسال_پیامک", Value=2),
                DropdownOption(Label="ارسال_ایمیل", Value=3),
                DropdownOption(Label="انتقال_فایل", Value=4),
                DropdownOption(Label="ارسال_گزارش", Value=5),
            ]),
            ValidationRule(Title="منبع مرتبط", Name="RelatedDatasource", InputType="dropdown", IsRequired=False, Icon="database", Placeholder="منبع داده را انتخاب کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="تاریخ شروع", Name="StartDate", InputType="date", IsRequired=False, Icon="calendar-start", Placeholder="تاریخ شروع را انتخاب کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="تاریخ پایان", Name="EndDate", InputType="date", IsRequired=False, Icon="calendar-end", Placeholder="تاریخ پایان را انتخاب کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="ساعت شروع", Name="StartTime", InputType="time", IsRequired=False, Icon="clock-start", Placeholder="ساعت شروع را انتخاب کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="ساعت پایان", Name="EndTime", InputType="time", IsRequired=False, Icon="clock-end", Placeholder="ساعت پایان را انتخاب کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="تکرار روز", Name="RepeatDay", InputType="number", IsRequired=False, Icon="repeat-day", Placeholder="تعداد روزهای تکرار را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="تکرار ساعت", Name="RepeatClock", InputType="number", IsRequired=False, Icon="repeat-hour", Placeholder="تعداد ساعات تکرار را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="کوئری", Name="Query", InputType="textarea", IsRequired=False, Icon="query", Placeholder="کوئری اجرایی را وارد کنید", IsReadonly=False, Disabled=False),
        ]
    )
