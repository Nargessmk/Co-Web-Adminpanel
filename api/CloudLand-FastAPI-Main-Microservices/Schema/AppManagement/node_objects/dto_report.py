from pydantic import Field

from Schema.AppManagement.node_objects.base import NodeObjectDTO, ValidationRule

class ReportDTO(NodeObjectDTO):
    FullName: str | None = None
    Icon: str | None = None
    DataSourceID: int | None = None
    ShowInMainMenu: bool = False
    ShowParameterInLoad: bool = False
    SelectedRow: bool = False
    QueryAfterPrint: str | None = None
    QueryBeforeRun: str | None = None
    PrinterName: str | None = None
    PrintCopy: int | None = None
    QueryPrintCopy: str | None = None
    UseDefaultIconColor: bool = False
    IconColor: str | None = None

    ValidationRules: list[ValidationRule] = Field(
        default_factory=lambda: [
            ValidationRule(Title="نام گزارش", Name="FullName", InputType="text", IsRequired=True, Icon="report", Placeholder="نام گزارش را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="آیکن گزارش", Name="Icon", InputType="text", IsRequired=False, Icon="image", Placeholder="نام آیکن را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="استفاده از رنگ پیشفرض", Name="UseDefaultIconColor", InputType="switch", IsRequired=False, Icon="color", Placeholder="", IsReadonly=False, Disabled=False),
            ValidationRule(Title="رنگ آیکن", Name="IconColor", InputType="text", IsRequired=False, Icon="palette", Placeholder="کد رنگ (مثلاً #FFFFFF)", IsReadonly=False, Disabled=False),
            ValidationRule(Title="منبع داده", Name="DataSourceID", InputType="selectbox", IsRequired=False, Icon="database", Placeholder="منبع داده را انتخاب کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="نمایش در منوی اصلی", Name="ShowInMainMenu", InputType="checkbox", IsRequired=False, Icon="menu", Placeholder="", IsReadonly=False, Disabled=False),
            ValidationRule(Title="نمایش پارامترها هنگام لود", Name="ShowParameterInLoad", InputType="checkbox", IsRequired=False, Icon="parameters", Placeholder="", IsReadonly=False, Disabled=False),
            ValidationRule(Title="انتخاب ردیف", Name="SelectedRow", InputType="checkbox", IsRequired=False, Icon="row-select", Placeholder="", IsReadonly=False, Disabled=False),
            ValidationRule(Title="نام پرینتر", Name="PrinterName", InputType="text", IsRequired=False, Icon="printer", Placeholder="نام پرینتر را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="تعداد کپی", Name="PrintCopy", InputType="number", IsRequired=False, Icon="copy", Placeholder="تعداد را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="کوئری تعداد کپی", Name="QueryPrintCopy", InputType="text", IsRequired=False, Icon="query", Placeholder="کوئری را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="دستور بعد از چاپ", Name="QueryAfterPrint", InputType="text", IsRequired=False, Icon="query-after", Placeholder="دستور SQL را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="دستور قبل از اجرا", Name="QueryBeforeRun", InputType="text", IsRequired=False, Icon="query-before", Placeholder="دستور SQL را وارد کنید", IsReadonly=False, Disabled=False),
        ]
    )
