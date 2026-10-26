from pydantic import Field

from Schema.AppManagement.node_objects.base import DropdownOption, NodeObjectDTO, ValidationRule

class SubDashboardDTO(NodeObjectDTO):
    FullName: str | None = None
    ChartTypes: int | None = None
    Title: str | None = None
    CategoryAxisQuery: str | None = None
    Condition: str | None = None
    IsWide: bool = False
    GroupField: int | None = None
    DateField: int | None = None
    ParentID: int | None = None
    ReloadTime: int | None = None
    ChartGroupDateType: int | None = None
    ChartCalculationType: int | None = None
    ColumnSpan: int | None = None
    RowSpan: int | None = None
    MaxValue: int | None = None
    IndicatorValue: int | None = None
    MinValue: int | None = None
    InformationEntryForm: int | None = None
    CalculationField: int | None = None
    Theme: str | None = None
    GroupByQuery: str | None = None
    OrderByQuery: str | None = None
    Icon: str | None = None
    BackgroundColor: str | None = None
    TextColor: str | None = None

    ValidationRules: list[ValidationRule] = Field(
        default_factory=lambda: [
            ValidationRule(Title="نام زیرداشبورد", Name="FullName", InputType="text", IsRequired=True, Icon="dashboard", Placeholder="نام زیرداشبورد را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="عنوان", Name="Title", InputType="text", IsRequired=False, Icon="title", Placeholder="عنوان نمودار را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="نوع نمودار", Name="ChartTypes", InputType="selectbox", IsRequired=True, Icon="chart", Placeholder="نوع نمودار را انتخاب کنید", IsReadonly=False, Disabled=False, Options=[
                DropdownOption(Label="میله_ای", Value=0),
                DropdownOption(Label="ستونی", Value=1),
                DropdownOption(Label="خطی", Value=2),
                DropdownOption(Label="دایره_ای", Value=3),
                DropdownOption(Label="قیفی", Value=4),
                DropdownOption(Label="جدول", Value=5),
                DropdownOption(Label="منطقه", Value=6),
                DropdownOption(Label="قوس_سنج", Value=7),
                DropdownOption(Label="تکی", Value=8),
            ]),
            ValidationRule(Title="نوع محاسبه", Name="ChartCalculationType", InputType="selectbox", IsRequired=True, Icon="calculator", Placeholder="نوع محاسبه را انتخاب کنید", IsReadonly=False, Disabled=False, Options=[
                DropdownOption(Label="هیچکدام", Value=0),
                DropdownOption(Label="تعداد", Value=1),
                DropdownOption(Label="مجموع", Value=2),
            ]),
            ValidationRule(Title="نوع گروه‌بندی تاریخ", Name="ChartGroupDateType", InputType="selectbox", IsRequired=False, Icon="calendar-group", Placeholder="نوع گروه‌بندی تاریخ را انتخاب کنید", IsReadonly=False, Disabled=False, Options=[
                DropdownOption(Label="هیچکدام", Value=0),
                DropdownOption(Label="سال", Value=1),
                DropdownOption(Label="ماه", Value=2),
                DropdownOption(Label="روز", Value=3),
            ]),
            ValidationRule(Title="کوئری محور دسته‌بندی", Name="CategoryAxisQuery", InputType="textarea", IsRequired=False, Icon="query", Placeholder="کوئری محور دسته‌بندی را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="کوئری گروه‌بندی", Name="GroupByQuery", InputType="textarea", IsRequired=False, Icon="group", Placeholder="کوئری گروه‌بندی را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="کوئری مرتب‌سازی", Name="OrderByQuery", InputType="textarea", IsRequired=False, Icon="sort", Placeholder="کوئری مرتب‌سازی را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="شرط", Name="Condition", InputType="textarea", IsRequired=False, Icon="filter", Placeholder="شرط اعمالی را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="فیلد گروه‌بندی", Name="GroupField", InputType="dropdown", IsRequired=False, Icon="group-field", Placeholder="فیلد گروه‌بندی را انتخاب کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="فیلد تاریخ", Name="DateField", InputType="dropdown", IsRequired=False, Icon="calendar", Placeholder="فیلد تاریخ را انتخاب کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="فرم ورود اطلاعات", Name="InformationEntryForm", InputType="dropdown", IsRequired=False, Icon="form", Placeholder="فرم ورود اطلاعات را انتخاب کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="فیلد محاسباتی", Name="CalculationField", InputType="dropdown", IsRequired=False, Icon="calculate", Placeholder="فیلد محاسباتی را انتخاب کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="نمایش عریض", Name="IsWide", InputType="checkbox", IsRequired=False, Icon="width", Placeholder="", IsReadonly=False, Disabled=False),
            ValidationRule(Title="تعداد ستون‌ها", Name="ColumnSpan", InputType="number", IsRequired=False, Icon="columns", Placeholder="تعداد ستون‌های اشغالی را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="تعداد ردیف‌ها", Name="RowSpan", InputType="number", IsRequired=False, Icon="rows", Placeholder="تعداد ردیف‌های اشغالی را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="زمان بارگذاری مجدد (ثانیه)", Name="ReloadTime", InputType="number", IsRequired=False, Icon="refresh", Placeholder="زمان به ثانیه را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="حداکثر مقدار", Name="MaxValue", InputType="number", IsRequired=False, Icon="max", Placeholder="حداکثر مقدار را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="حداقل مقدار", Name="MinValue", InputType="number", IsRequired=False, Icon="min", Placeholder="حداقل مقدار را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="مقدار نشانگر", Name="IndicatorValue", InputType="number", IsRequired=False, Icon="indicator", Placeholder="مقدار نشانگر را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="تم", Name="Theme", InputType="dropdown", IsRequired=False, Icon="palette", Placeholder="تم را انتخاب کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="آیکون", Name="Icon", InputType="icon-picker", IsRequired=False, Icon="image", Placeholder="آیکون را انتخاب کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="رنگ پس‌زمینه", Name="BackgroundColor", InputType="color", IsRequired=False, Icon="background", Placeholder="رنگ پس‌زمینه را انتخاب کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="رنگ متن", Name="TextColor", InputType="color", IsRequired=False, Icon="text-color", Placeholder="رنگ متن را انتخاب کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="شناسه والد", Name="ParentID", InputType="number", IsRequired=False, Icon="parent", Placeholder="شناسه داشبورد والد را وارد کنید", IsReadonly=False, Disabled=False),
        ]
    )
