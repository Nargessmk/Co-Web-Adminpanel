from pydantic import Field

from Schema.AppManagement.node_objects.base import NodeObjectDTO, ValidationRule

class PublicSettingDTO(NodeObjectDTO):
    CompanyName: str | None = None
    AppPersianName: str | None = None
    AppEnglishName: str | None = None
    WebSite: str | None = None
    PhoneNumber: str | None = None
    E_Maile: str | None = None
    EMaileUserName: str | None = None
    EMailePassWord: str | None = None
    EMaileServer: str | None = None
    EMailePort: str | None = None
    EnableSsl: bool = False
    BrandSlogan: str | None = None
    AppLogo: str | None = None
    MainColor: str | None = None
    IconColor: str | None = None
    TitleColor: str | None = None
    IntroduceOthers: str | None = None
    Laws: str | None = None
    UserPrivacy: str | None = None
    FileSavingPath: str | None = None
    SaveFileValueInDataBase: bool = False
    LoginBackgroundImage: str | None = None
    HeaderLoginBackgroundImage: str | None = None
    HomeBackgroundImage: str | None = None
    GeneralMessage: str | None = None
    CSS: str | None = None
    JS: str | None = None
    RelatedWebService: int | None = None
    ChangePasswordDays: int | None = None
    SupportLink: str | None = None
    DataRecoveryMinutes: int | None = None

    ValidationRules: list[ValidationRule] = Field(
        default_factory=lambda: [
            ValidationRule(Title="نام شرکت", Name="CompanyName", InputType="text", IsRequired=True, Icon="company", Placeholder="نام شرکت را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="نام فارسی اپلیکیشن", Name="AppPersianName", InputType="text", IsRequired=True, Icon="app", Placeholder="نام فارسی برنامه را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="نام انگلیسی اپلیکیشن", Name="AppEnglishName", InputType="text", IsRequired=True, Icon="app", Placeholder="نام انگلیسی برنامه را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="شعار برند", Name="BrandSlogan", InputType="text", IsRequired=True, Icon="slogan", Placeholder="شعار برند را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="وبسایت", Name="WebSite", InputType="url", IsRequired=False, Icon="website", Placeholder="آدرس وبسایت را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="شماره تماس", Name="PhoneNumber", InputType="tel", IsRequired=False, Icon="phone", Placeholder="شماره تماس را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="ایمیل", Name="E_Maile", InputType="email", IsRequired=False, Icon="email", Placeholder="آدرس ایمیل را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="لینک پشتیبان", Name="SupportLink", InputType="url", IsRequired=False, Icon="support", Placeholder="لینک پشتیبانی را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="رنگ پس زمینه", Name="MainColor", InputType="color", IsRequired=True, Icon="background", Placeholder="رنگ اصلی را انتخاب کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="رنگ آیکن", Name="IconColor", InputType="color", IsRequired=True, Icon="icon", Placeholder="رنگ آیکن ها را انتخاب کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="رنگ حروف", Name="TitleColor", InputType="color", IsRequired=True, Icon="text", Placeholder="رنگ متن ها را انتخاب کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="لوگوی شرکت", Name="AppLogo", InputType="image", IsRequired=True, Icon="logo", Placeholder="لوگو را آپلود کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="تصویر زمینه ورودی", Name="LoginBackgroundImage", InputType="image", IsRequired=True, Icon="login-bg", Placeholder="تصویر زمینه صفحه ورود را آپلود کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="تصویر زمینه خانه", Name="HomeBackgroundImage", InputType="image", IsRequired=True, Icon="home-bg", Placeholder="تصویر زمینه صفحه اصلی را آپلود کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="معرفی به دیگران", Name="IntroduceOthers", InputType="text", IsRequired=True, Icon="share", Placeholder="متن معرفی را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="پیغام عمومی", Name="GeneralMessage", InputType="text", IsRequired=True, Icon="message", Placeholder="پیغام عمومی را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="قوانین", Name="Laws", InputType="textarea", IsRequired=True, Icon="law", Placeholder="قوانین را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="حریم خصوصی", Name="UserPrivacy", InputType="textarea", IsRequired=True, Icon="privacy", Placeholder="متن حریم خصوصی را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="مسیر ذخیره ی ضمائم", Name="FileSavingPath", InputType="text", IsRequired=True, Icon="folder", Placeholder="مسیر ذخیره فایل ها را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="CSS", Name="CSS", InputType="textarea", IsRequired=True, Icon="css", Placeholder="کدهای CSS را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="JS", Name="JS", InputType="textarea", IsRequired=True, Icon="javascript", Placeholder="کدهای JavaScript را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="نام کاربری ایمیل", Name="EMaileUserName", InputType="text", IsRequired=False, Icon="user", Placeholder="نام کاربری ایمیل را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="کلمه عبور ایمیل", Name="EMailePassWord", InputType="password", IsRequired=False, Icon="password", Placeholder="کلمه عبور ایمیل را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="سرور ایمیل", Name="EMaileServer", InputType="text", IsRequired=False, Icon="server", Placeholder="آدرس سرور ایمیل را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="پورت ایمیل", Name="EMailePort", InputType="text", IsRequired=False, Icon="port", Placeholder="پورت ایمیل را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="فعال کردن SSL", Name="EnableSsl", InputType="checkbox", IsRequired=False, Icon="security", Placeholder="", IsReadonly=False, Disabled=False),
            ValidationRule(Title="وب سرویس مرتبط", Name="RelatedWebService", InputType="dropdown", IsRequired=False, Icon="web-service", Placeholder="وب سرویس پیامک را انتخاب کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="تعداد روزهای تغییر کلمه عبور", Name="ChangePasswordDays", InputType="number", IsRequired=False, Icon="password-change", Placeholder="تعداد روزهای تغییر رمز را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="زمان بازیابی داده ها(دقیقه)", Name="DataRecoveryMinutes", InputType="number", IsRequired=False, Icon="recovery", Placeholder="زمان بازیابی داده را وارد کنید", IsReadonly=False, Disabled=False),
        ]
    )
