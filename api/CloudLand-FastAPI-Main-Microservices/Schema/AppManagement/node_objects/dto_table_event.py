from pydantic import Field

from Schema.AppManagement.node_objects.base import NodeObjectDTO, ValidationRule

class TableEventDTO(NodeObjectDTO):
    TypeEventExecution: str | None = None
    EventType: str | None = None
    Condition: str | None = None
    Query: str | None = None
    RelatedTable: int | None = None
    RelatedWebService: int | None = None
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
    ReferralRecipientsUser: list[str] | None = None
    ReferralRecipientsRole: list[str] | None = None
    ReferralRecipientsQuery: str | None = None
    ReferralDeadlineResponse: int | None = None
    ReferralTitle: str | None = None
    ReferralTitleQuery: str | None = None

    ValidationRules: list[ValidationRule] = Field(
        default_factory=lambda: [
            ValidationRule(Title="نوع اجرای رویداد", Name="TypeEventExecution", InputType="text", IsRequired=True, Icon="event-execution", Placeholder="نوع اجرا را انتخاب کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="نوع رویداد", Name="EventType", InputType="text", IsRequired=True, Icon="event-type", Placeholder="نوع رویداد را انتخاب کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="جدول مرتبط", Name="RelatedTable", InputType="text", IsRequired=True, Icon="table-link", Placeholder="جدول مرتبط را انتخاب کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="وب سرویس مرتبط", Name="RelatedWebService", InputType="selectbox", IsRequired=True, Icon="webservice", Placeholder="وب سرویس را انتخاب کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="شرط اجرای کوئری", Name="Condition", InputType="textarea", IsRequired=False, Icon="condition", Placeholder="شرط SQL را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="کوئری", Name="Query", InputType="textarea", IsRequired=False, Icon="query", Placeholder="کوئری SQL را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="استفاده از ایمیل پیشفرض", Name="UsePublicEmail", InputType="switch", IsRequired=False, Icon="email-default", Placeholder="", IsReadonly=False, Disabled=False),
            ValidationRule(Title="ایمیل", Name="EMail", InputType="text", IsRequired=False, Icon="email", Placeholder="آدرس ایمیل را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="نام کاربری", Name="EMailUserName", InputType="text", IsRequired=False, Icon="username", Placeholder="نام کاربری ایمیل را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="کلمه عبور", Name="EMailPassWord", InputType="password", IsRequired=False, Icon="password", Placeholder="رمز عبور ایمیل را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="سرور", Name="EMailServer", InputType="text", IsRequired=False, Icon="server", Placeholder="آدرس سرور ایمیل را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="پورت", Name="EMailPort", InputType="text", IsRequired=False, Icon="port", Placeholder="پورت ایمیل را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="فعال کردن SSL", Name="EnableSsl", InputType="switch", IsRequired=False, Icon="ssl", Placeholder="", IsReadonly=False, Disabled=False),
            ValidationRule(Title="کاربران دریافت کننده", Name="ReceivingUsers", InputType="multiselect", IsRequired=False, Icon="users", Placeholder="کاربران را انتخاب کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="نقش کاربر دریافت کننده", Name="ReceivingRole", InputType="multiselect", IsRequired=False, Icon="roles", Placeholder="نقش ها را انتخاب کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="کاربر درج کننده", Name="InsertingUser", InputType="switch", IsRequired=False, Icon="user-add", Placeholder="", IsReadonly=False, Disabled=False),
            ValidationRule(Title="کوئری دریافت کنندگان", Name="ReceivingQuery", InputType="textarea", IsRequired=False, Icon="query-users", Placeholder="کوئری دریافت کنندگان را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="ارسال پیوست", Name="SendAttachmentFile", InputType="switch", IsRequired=False, Icon="attachment", Placeholder="", IsReadonly=False, Disabled=False),
            ValidationRule(Title="ارسال گزارش", Name="SendReport", InputType="multiselect", IsRequired=False, Icon="report", Placeholder="گزارش ها را انتخاب کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="عنوان", Name="Title", InputType="text", IsRequired=False, Icon="title", Placeholder="عنوان ایمیل را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="کوئری عنوان", Name="TitleQuery", InputType="textarea", IsRequired=False, Icon="query-title", Placeholder="کوئری عنوان را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="متن", Name="BodyMessage", InputType="textarea", IsRequired=False, Icon="message", Placeholder="متن ایمیل را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="کوئری متن", Name="BodyMessageQuery", InputType="textarea", IsRequired=False, Icon="query-message", Placeholder="کوئری متن را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="مهلت پاسخگویی (روز)", Name="ReferralDeadlineResponse", InputType="number", IsRequired=False, Icon="deadline", Placeholder="تعداد روز را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="کاربران دریافت کننده", Name="ReferralRecipientsUser", InputType="multiselect", IsRequired=False, Icon="users", Placeholder="کاربران را انتخاب کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="نقش کاربر دریافت کننده", Name="ReferralRecipientsRole", InputType="multiselect", IsRequired=False, Icon="roles", Placeholder="نقش ها را انتخاب کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="کوئری دریافت کنندگان", Name="ReferralRecipientsQuery", InputType="textarea", IsRequired=False, Icon="query-users", Placeholder="کوئری دریافت کنندگان را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="دستور ارجاع", Name="ReferralTitle", InputType="textarea", IsRequired=False, Icon="referral", Placeholder="دستور ارجاع را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="کوئری دستور ارجاع", Name="ReferralTitleQuery", InputType="textarea", IsRequired=False, Icon="query-referral", Placeholder="کوئری دستور ارجاع را وارد کنید", IsReadonly=False, Disabled=False),
        ]
    )
