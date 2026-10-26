from pydantic import Field

from Schema.AppManagement.node_objects.base import DropdownOption, NodeObjectDTO, ValidationRule

class DisplayFieldDTO(NodeObjectDTO):
    TableButtonEventsType: int | None = None
    ReportID: int | None = None
    ParameterReportID: int | None = None
    Template: str | None = None
    FullName: str | None = None
    DisplayName: str | None = None
    ShowInStart: bool = False
    UseDefaultReportSetting: bool = False
    PrinterName: str | None = None
    PrintCopy: int | None = None
    QueryPrintCopy: str | None = None
    ExecutionConditionQuery: str | None = None
    Query: str | None = None
    Icon: str | None = None
    ShowTitle: bool = False
    RelatedForm: int | None = None
    RelatedField: int | None = None
    IsReloadGrid: bool = False
    EMail: str | None = None
    EMailUserName: str | None = None
    EMailPassWord: str | None = None
    EMailServer: str | None = None
    EMailPort: str | None = None
    ReceivingUsers: list[str] | None = None
    ReceivingRole: list[str] | None = None
    InsertingUser: bool = False
    ReceivingQuery: str | None = None
    SendAttachmentFile: bool = False
    EnableSsl: bool = False
    UsePublicEmail: bool = False
    SendReport: list[str] | None = None
    Title: str | None = None
    TitleQuery: str | None = None
    BodyMessage: str | None = None
    BodyMessageQuery: str | None = None
    URL: str | None = None

    ValidationRules: list[ValidationRule] = Field(
        default_factory=lambda: [
            ValidationRule(Title="نام کامل", Name="FullName", InputType="text", IsRequired=True, Icon="field", Placeholder="نام کامل فیلد را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="نام نمایشی", Name="DisplayName", InputType="text", IsRequired=False, Icon="text-field", Placeholder="نام نمایشی فیلد را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="نمایش در ابتدای ستون", Name="ShowInStart", InputType="checkbox", IsRequired=False, Icon="column-first", Placeholder="", IsReadonly=False, Disabled=False),
            ValidationRule(Title="نمایش عنوان", Name="ShowTitle", InputType="checkbox", IsRequired=False, Icon="title", Placeholder="", IsReadonly=False, Disabled=False),
            ValidationRule(Title="بروز رسانی داده", Name="IsReloadGrid", InputType="checkbox", IsRequired=False, Icon="refresh", Placeholder="", IsReadonly=False, Disabled=False),
            ValidationRule(Title="نوع عملیات", Name="TableButtonEventsType", InputType="selectbox", IsRequired=True, Icon="action", Placeholder="نوع عملیات را انتخاب کنید", IsReadonly=False, Disabled=False, Options=[
                DropdownOption(Label="خالی", Value=0),
                DropdownOption(Label="اجرای_رویداد", Value=1),
                DropdownOption(Label="اجرای_وب_سرویس", Value=2),
                DropdownOption(Label="ارسال_ایمیل", Value=3),
                DropdownOption(Label="انتقال_فایل", Value=4),
                DropdownOption(Label="باز_کردن_فرم", Value=5),
                DropdownOption(Label="باز_کردن_فرم_فقط_خواندنی", Value=6),
                DropdownOption(Label="نمایش_ضمیمه", Value=7),
                DropdownOption(Label="باز_کردن_فرم_به_صورت_ویرایش", Value=8),
                DropdownOption(Label="تولید_کلید_عمومی_مالیاتی", Value=9),
                DropdownOption(Label="بروزرسانی_کالا_مالیات", Value=10),
                DropdownOption(Label="ارسال_صورتحساب_به_سامانه_مودیان", Value=11),
                DropdownOption(Label="باز_کردن_فرم_با_لینک", Value=12),
                DropdownOption(Label="باز_کردن_فرم_به_صورت_ویرایش_با_لینک", Value=13),
                DropdownOption(Label="نمایش_گزارش", Value=15),
                DropdownOption(Label="پرینت_گزارش", Value=16),
            ]),
            ValidationRule(Title="فرم مرتبط", Name="RelatedForm", InputType="dropdown", IsRequired=False, Icon="form", Placeholder="فرم مرتبط را انتخاب کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="فیلد مرتبط", Name="RelatedField", InputType="dropdown", IsRequired=False, Icon="field-link", Placeholder="فیلد مرتبط را انتخاب کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="گزارش", Name="ReportID", InputType="dropdown", IsRequired=False, Icon="report", Placeholder="گزارش را انتخاب کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="پارامتر گزارش", Name="ParameterReportID", InputType="dropdown", IsRequired=False, Icon="report-parameter", Placeholder="پارامتر گزارش را انتخاب کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="دستور", Name="Template", InputType="textarea", IsRequired=True, Icon="code", Placeholder="دستور نمایش را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="کوئری", Name="Query", InputType="textarea", IsRequired=False, Icon="query", Placeholder="کوئری را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="شرط اجرای کوئری", Name="ExecutionConditionQuery", InputType="textarea", IsRequired=False, Icon="conditional", Placeholder="شرط اجرای کوئری را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="آیکن", Name="Icon", InputType="icon-picker", IsRequired=False, Icon="image", Placeholder="آیکن را انتخاب کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="URL", Name="URL", InputType="url", IsRequired=False, Icon="link", Placeholder="آدرس URL را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="استفاده از ایمیل پیشفرض", Name="UsePublicEmail", InputType="checkbox", IsRequired=False, Icon="email-public", Placeholder="", IsReadonly=False, Disabled=False),
            ValidationRule(Title="ایمیل", Name="EMail", InputType="email", IsRequired=False, Icon="email", Placeholder="آدرس ایمیل را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="نام کاربری", Name="EMailUserName", InputType="text", IsRequired=False, Icon="user", Placeholder="نام کاربری ایمیل را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="کلمه عبور", Name="EMailPassWord", InputType="password", IsRequired=False, Icon="password", Placeholder="کلمه عبور ایمیل را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="سرور", Name="EMailServer", InputType="text", IsRequired=False, Icon="server", Placeholder="آدرس سرور ایمیل را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="پورت", Name="EMailPort", InputType="text", IsRequired=False, Icon="port", Placeholder="پورت ایمیل را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="فعال کردن SSL", Name="EnableSsl", InputType="checkbox", IsRequired=False, Icon="security", Placeholder="", IsReadonly=False, Disabled=False),
            ValidationRule(Title="کاربران دریافت کننده", Name="ReceivingUsers", InputType="multiselect", IsRequired=False, Icon="users", Placeholder="کاربران دریافت کننده را انتخاب کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="نقش کاربر دریافت کننده", Name="ReceivingRole", InputType="multiselect", IsRequired=False, Icon="roles", Placeholder="نقش های دریافت کننده را انتخاب کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="کاربر درج کننده", Name="InsertingUser", InputType="checkbox", IsRequired=False, Icon="user-add", Placeholder="", IsReadonly=False, Disabled=False),
            ValidationRule(Title="کوئری دریافت کنندگان", Name="ReceivingQuery", InputType="textarea", IsRequired=False, Icon="query", Placeholder="کوئری دریافت کنندگان را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="ارسال پیوست", Name="SendAttachmentFile", InputType="checkbox", IsRequired=False, Icon="attachment", Placeholder="", IsReadonly=False, Disabled=False),
            ValidationRule(Title="ارسال گزارش", Name="SendReport", InputType="multiselect", IsRequired=False, Icon="report-send", Placeholder="گزارش های ارسالی را انتخاب کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="عنوان", Name="Title", InputType="text", IsRequired=False, Icon="title", Placeholder="عنوان ایمیل را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="کوئری عنوان", Name="TitleQuery", InputType="textarea", IsRequired=False, Icon="query", Placeholder="کوئری عنوان ایمیل را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="متن", Name="BodyMessage", InputType="textarea", IsRequired=False, Icon="message", Placeholder="متن ایمیل را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="کوئری متن", Name="BodyMessageQuery", InputType="textarea", IsRequired=False, Icon="query", Placeholder="کوئری متن ایمیل را وارد کنید", IsReadonly=False, Disabled=False),
        ]
    )
