from pydantic import Field

from Schema.AppManagement.node_objects.base import NodeObjectDTO, ValidationRule
from typing import ClassVar

class AdminSettingDTO(NodeObjectDTO):
    ShowUserRegistryInLoginForm: bool = False
    ShowDataSourceListInSettingForm: bool = False
    ShowSpecialPhraseListInSettingForm: bool = False
    ShowInformationEntryFormListInSettingForm: bool = False
    ShowProcessListInSettingForm: bool = False
    ShowReportListInSettingForm: bool = False
    ShowDashboardListInSettingForm: bool = False
    ShowPublicFileListInSettingForm: bool = False
    ShowConnectWebsiteListInSettingForm: bool = False
    ShowSMSSettingInSettingForm: bool = False
    ShowEmailSettingInSettingForm: bool = False
    ShowPaymentSettingInSettingForm: bool = False
    ShowPublicSettingInSettingForm: bool = False
    ShowUserCalendar: bool = False
    ShowInfoInLogin: bool = False
    ShowAllRights: bool = False
    ShowEditingRestrictions: bool = False
    ShowCanUpdateOnlyUserRegistry: bool = False
    ShowCanUpdateOneDey: bool = False
    ShowCanUpdateThreeDey: bool = False
    ShowCanUpdateOneWeek: bool = False
    PermissionShowImportExportInForm: bool = False
    ShowImportExportInAllForm: bool = False
    AllowFormShowImportExport: list[str] | None = None
    PermissionShowCommentInForm: bool = False
    ShowCommentInAllForm: bool = False
    AllowFormShowComment: list[str] | None = None
    PermissionShowEmailInForm: bool = False
    ShowEmailInAllForm: bool = False
    AllowFormShowEmail: list[str] | None = None

    REQUIRED_FIELDS: ClassVar[tuple[str, ...]] = ("ShowUserRegistryInLoginForm", "ShowDataSourceListInSettingForm", "ShowSpecialPhraseListInSettingForm")

    ValidationRules: list[ValidationRule] = Field(
        default_factory=lambda: [
            ValidationRule(Title="نمایش ثبت نام در فرم ورود", Name="ShowUserRegistryInLoginForm", InputType="checkbox", IsRequired=False, Icon="general", Placeholder="", IsReadonly=False, Disabled=False),
            ValidationRule(Title="نمایش تقویم برنامه ریزی", Name="ShowUserCalendar", InputType="checkbox", Icon="general", Placeholder="", IsReadonly=False, Disabled=False, IsRequired=False),
            ValidationRule(Title="نمایش اطلاعات در فرم ورود", Name="ShowInfoInLogin", InputType="checkbox", Icon="general", Placeholder="", IsReadonly=False, Disabled=False, IsRequired=False),
            ValidationRule(Title="نمایش کلیه حقوق", Name="ShowAllRights", InputType="checkbox", Icon="general", Placeholder="", IsReadonly=False, Disabled=False, IsRequired=False),
            ValidationRule(Title="نمایش پایگاه داده", Name="ShowDataSourceListInSettingForm", InputType="checkbox", Icon="system", Placeholder="", IsReadonly=False, Disabled=False, IsRequired=False),
            ValidationRule(Title="نمایش عبارت ویژه", Name="ShowSpecialPhraseListInSettingForm", InputType="checkbox", Icon="system", Placeholder="", IsReadonly=False, Disabled=False, IsRequired=False),
            ValidationRule(Title="نمایش فرم ساز", Name="ShowInformationEntryFormListInSettingForm", InputType="checkbox", Icon="system", Placeholder="", IsReadonly=False, Disabled=False, IsRequired=False),
            ValidationRule(Title="نمایش فرآیند ساز", Name="ShowProcessListInSettingForm", InputType="checkbox", Icon="system", Placeholder="", IsReadonly=False, Disabled=False, IsRequired=False),
            ValidationRule(Title="نمایش گزارش ساز", Name="ShowReportListInSettingForm", InputType="checkbox", Icon="system", Placeholder="", IsReadonly=False, Disabled=False, IsRequired=False),
            ValidationRule(Title="نمایش داشبورد ساز", Name="ShowDashboardListInSettingForm", InputType="checkbox", Icon="system", Placeholder="", IsReadonly=False, Disabled=False, IsRequired=False),
            ValidationRule(Title="نمایش فایل های عمومی", Name="ShowPublicFileListInSettingForm", InputType="checkbox", Icon="system", Placeholder="", IsReadonly=False, Disabled=False, IsRequired=False),
            ValidationRule(Title="نمایش ارتباط با وب سایت", Name="ShowConnectWebsiteListInSettingForm", InputType="checkbox", Icon="system", Placeholder="", IsReadonly=False, Disabled=False, IsRequired=False),
            ValidationRule(Title="نمایش ارتباط با پیامک", Name="ShowSMSSettingInSettingForm", InputType="checkbox", Icon="system", Placeholder="", IsReadonly=False, Disabled=False, IsRequired=False),
            ValidationRule(Title="نمایش ارتباط با ایمیل", Name="ShowEmailSettingInSettingForm", InputType="checkbox", Icon="system", Placeholder="", IsReadonly=False, Disabled=False, IsRequired=False),
            ValidationRule(Title="نمایش ارتباط با درگاه پرداخت", Name="ShowPaymentSettingInSettingForm", InputType="checkbox", Icon="system", Placeholder="", IsReadonly=False, Disabled=False, IsRequired=False),
            ValidationRule(Title="نمایش تنظیمات عمومی", Name="ShowPublicSettingInSettingForm", InputType="checkbox", Icon="system", Placeholder="", IsReadonly=False, Disabled=False, IsRequired=False),
            ValidationRule(Title="نمایش محدودیت های ویرایش", Name="ShowEditingRestrictions", InputType="checkbox", Icon="edit", Placeholder="", IsReadonly=False, Disabled=False, IsRequired=False),
            ValidationRule(Title="ویرایش محدود به کاربر درج کننده", Name="ShowCanUpdateOnlyUserRegistry", InputType="checkbox", Icon="edit", Placeholder="", IsReadonly=False, Disabled=False, IsRequired=False),
            ValidationRule(Title="ویرایش به مدت یک روز", Name="ShowCanUpdateOneDey", InputType="checkbox", Icon="edit", Placeholder="", IsReadonly=False, Disabled=False, IsRequired=False),
            ValidationRule(Title="ویرایش به مدت سه روز", Name="ShowCanUpdateThreeDey", InputType="checkbox", Icon="edit", Placeholder="", IsReadonly=False, Disabled=False, IsRequired=False),
            ValidationRule(Title="ویرایش به مدت یک هفته", Name="ShowCanUpdateOneWeek", InputType="checkbox", Icon="edit", Placeholder="", IsReadonly=False, Disabled=False, IsRequired=False),
            ValidationRule(Title="دسترسی نمایش import در فرم", Name="PermissionShowImportExportInForm", InputType="checkbox", Icon="import-export", Placeholder="", IsReadonly=False, Disabled=False, IsRequired=False),
            ValidationRule(Title="نمایش import در تمام فرم ها", Name="ShowImportExportInAllForm", InputType="checkbox", Icon="import-export", Placeholder="", IsReadonly=False, Disabled=False, IsRequired=False),
            ValidationRule(Title="نمایش import", Name="AllowFormShowImportExport", InputType="CoreRelatedTableCheckbox", IsRequired=False, Icon="import-export", Placeholder="", IsReadonly=False, Disabled=False),
            ValidationRule(Title="دسترسی نمایش یادداشت در فرم", Name="PermissionShowCommentInForm", InputType="checkbox", Icon="note", Placeholder="", IsReadonly=False, Disabled=False, IsRequired=False),
            ValidationRule(Title="نمایش یادداشت در تمام فرم ها", Name="ShowCommentInAllForm", InputType="checkbox", Icon="note", Placeholder="", IsReadonly=False, Disabled=False, IsRequired=False),
            ValidationRule(Title="نمایش یادداشت", Name="AllowFormShowComment", InputType="CoreRelatedTableCheckbox", IsRequired=False, Icon="note", Placeholder="", IsReadonly=False, Disabled=False),
            ValidationRule(Title="دسترسی نمایش ایمیل در فرم", Name="PermissionShowEmailInForm", InputType="checkbox", Icon="email", Placeholder="", IsReadonly=False, Disabled=False, IsRequired=False),
            ValidationRule(Title="نمایش ایمیل در تمام فرم ها", Name="ShowEmailInAllForm", InputType="checkbox", Icon="email", Placeholder="", IsReadonly=False, Disabled=False, IsRequired=False),
            ValidationRule(Title="نمایش ایمیل", Name="AllowFormShowEmail", InputType="CoreRelatedTableCheckbox", IsRequired=False, Icon="email", Placeholder="", IsReadonly=False, Disabled=False),
        ]
    )
