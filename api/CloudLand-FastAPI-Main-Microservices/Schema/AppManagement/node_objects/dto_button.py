from pydantic import Field

from Schema.AppManagement.node_objects.base import DropdownOption, NodeObjectDTO, ValidationRule

class ButtonDTO(NodeObjectDTO):
    FullName: str | None = None
    Icon: str | None = None
    Query: str | None = None
    ExecutionConditionQuery: str | None = None
    TableButtonEventsType: int | None = None
    CoreObjectID: int | None = None
    RelatedForm: int | None = None
    RelatedField: int | None = None
    RelatedWebService: int | None = None
    IsReloadGrid: bool = False
    IsShowText: bool = False
    IsShowIcon: bool = False
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
            ValidationRule(Title="نام دکمه", Name="FullName", InputType="text", IsRequired=True, Icon="button", Placeholder="نام دکمه را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="آیکون", Name="Icon", InputType="icon-picker", IsRequired=False, Icon="image", Placeholder="آیکون را انتخاب کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="نمایش متن", Name="IsShowText", InputType="checkbox", IsRequired=False, Icon="text", Placeholder="", IsReadonly=False, Disabled=False),
            ValidationRule(Title="نمایش آیکون", Name="IsShowIcon", InputType="checkbox", IsRequired=False, Icon="image", Placeholder="", IsReadonly=False, Disabled=False),
            ValidationRule(Title="بارگذاری مجدد گرید", Name="IsReloadGrid", InputType="checkbox", IsRequired=False, Icon="refresh", Placeholder="", IsReadonly=False, Disabled=False),
            ValidationRule(Title="نوع رویداد", Name="TableButtonEventsType", InputType="dropdown", IsRequired=True, Icon="event", Placeholder="نوع رویداد را انتخاب کنید", IsReadonly=False, Disabled=False, Options=[
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
            ValidationRule(Title="فرم مرتبط", Name="RelatedForm", InputType="number", IsRequired=False, Icon="form", Placeholder="شناسه فرم را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="فیلد مرتبط", Name="RelatedField", InputType="number", IsRequired=False, Icon="field", Placeholder="شناسه فیلد را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="وب سرویس مرتبط", Name="RelatedWebService", InputType="number", IsRequired=False, Icon="web-service", Placeholder="شناسه وب سرویس را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="URL", Name="URL", InputType="url", IsRequired=False, Icon="link", Placeholder="آدرس URL را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="کوئری", Name="Query", InputType="textarea", IsRequired=False, Icon="code", Placeholder="کوئری را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="کوئری شرط اجرا", Name="ExecutionConditionQuery", InputType="textarea", IsRequired=False, Icon="conditional", Placeholder="شرط اجرا را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="ایمیل", Name="EMail", InputType="email", IsRequired=False, Icon="email", Placeholder="آدرس ایمیل را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="نام کاربری ایمیل", Name="EMailUserName", InputType="text", IsRequired=False, Icon="user", Placeholder="نام کاربری ایمیل را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="کلمه عبور ایمیل", Name="EMailPassWord", InputType="password", IsRequired=False, Icon="password", Placeholder="کلمه عبور ایمیل را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="سرور ایمیل", Name="EMailServer", InputType="text", IsRequired=False, Icon="server", Placeholder="آدرس سرور ایمیل را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="پورت ایمیل", Name="EMailPort", InputType="text", IsRequired=False, Icon="port", Placeholder="پورت ایمیل را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="کاربران دریافت کننده", Name="ReceivingUsers", InputType="multiselect", IsRequired=False, Icon="users", Placeholder="کاربران را انتخاب کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="نقش های دریافت کننده", Name="ReceivingRole", InputType="multiselect", IsRequired=False, Icon="roles", Placeholder="نقش ها را انتخاب کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="درج کننده کاربر", Name="InsertingUser", InputType="checkbox", IsRequired=False, Icon="user-add", Placeholder="", IsReadonly=False, Disabled=False),
            ValidationRule(Title="کوئری دریافت کنندگان", Name="ReceivingQuery", InputType="textarea", IsRequired=False, Icon="query", Placeholder="کوئری دریافت کنندگان را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="ارسال فایل پیوست", Name="SendAttachmentFile", InputType="checkbox", IsRequired=False, Icon="attachment", Placeholder="", IsReadonly=False, Disabled=False),
            ValidationRule(Title="استفاده از ایمیل عمومی", Name="UsePublicEmail", InputType="checkbox", IsRequired=False, Icon="email-public", Placeholder="", IsReadonly=False, Disabled=False),
            ValidationRule(Title="فعالسازی SSL", Name="EnableSsl", InputType="checkbox", IsRequired=False, Icon="security", Placeholder="", IsReadonly=False, Disabled=False),
            ValidationRule(Title="ارسال گزارش", Name="SendReport", InputType="multiselect", IsRequired=False, Icon="report", Placeholder="گزارش ها را انتخاب کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="عنوان", Name="Title", InputType="text", IsRequired=False, Icon="title", Placeholder="عنوان را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="کوئری عنوان", Name="TitleQuery", InputType="textarea", IsRequired=False, Icon="query", Placeholder="کوئری عنوان را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="متن پیام", Name="BodyMessage", InputType="textarea", IsRequired=False, Icon="message", Placeholder="متن پیام را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="کوئری متن پیام", Name="BodyMessageQuery", InputType="textarea", IsRequired=False, Icon="query", Placeholder="کوئری متن پیام را وارد کنید", IsReadonly=False, Disabled=False),
        ]
    )
