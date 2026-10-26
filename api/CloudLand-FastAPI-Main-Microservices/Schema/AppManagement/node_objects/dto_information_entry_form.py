from pydantic import Field

from Schema.AppManagement.node_objects.base import DropdownOption, NodeObjectDTO, ValidationRule

class InformationEntryFormDTO(NodeObjectDTO):
    InformationEntryFormName: str | None = None
    Query: str | None = None
    ConditionQuery: str | None = None
    OrderQuery: str | None = None
    RelatedTable: int | None = None
    ExternalField: int | None = None
    ParentID: int | None = None
    ShowRecordCountDefault: int | None = None
    IsDefault: bool = False
    IsShowID: bool = False
    ShowSelectedColumn: bool = False
    SearchWithOnKeyDown: bool = False
    SearchWithOnKeyDownCoreId: int | None = None
    Icon: str | None = None
    BadgeTitle: str | None = None
    BadgeQuery: str | None = None
    BadgeColor: str | None = None
    BadgeTextColor: str | None = None
    CSS: str | None = None
    ShowAttachment: bool = False
    ShowDetailAttachment: bool = False
    ShowInParentForm: bool = False
    ShowInMenuTreeList: bool = False
    Groupable: bool = False
    Pageable: bool = False
    AggregateUsable: bool = False
    ShowAttachmentColumn: bool = False
    AttachmentColumnName: int | None = None
    TitleSaveButton: str | None = None
    HeightAttachment: int | None = None
    GridEditMode: int | None = None
    ShowChartInformationEntryForm: bool = False
    IsCloseFormAfterSave: bool = False
    ChartID: str | None = None
    ChartName: str | None = None
    ChartTitle: str | None = None
    ChartGroup: str | None = None
    ChartAvatar: str | None = None
    ChartParentID: str | None = None
    RowColorColumnName: int | None = None
    RowColorOperator: str | None = None
    RowColorColumnValue: str | None = None
    RowColorSelectedColor: str | None = None
    ShowLineNumber: bool = False
    ShowClearFormWithOutFixItemButton: bool = False
    FixItemClearForm: str | None = None
    ClearFormWithOutFixItemButtonName: str | None = None
    RowCountInPage: int | None = None
    SaveParentSubjectSaveChild: bool = False
    FormComment: str | None = None
    ShowAttachmentButton: bool = False
    CheckValidChildGrid: bool = False
    ShowNewButton: bool = False
    Height: int | None = None
    DefaultColumnShowInGrid: str | None = None
    EditorFormJson: str | None = None
    GroupableField: int | None = None
    NewPageUrl: str | None = None
    UpdatePageUrl: str | None = None
    NewButtonVisibleConditionQuery: str | None = None
    GroupByQuery: str | None = None
    SaveAtOnce: bool = False
    CheckFieldDuplicateRecords: str | None = None
    ColumnWidth: str | None = None
    AttachmentColumnWidth: str | None = None
    AnalystDescription: str | None = None
    ShowNewButtonInToolbar: bool = False
    ShowUpdateButtonInToolbar: bool = False
    ShowDeleteButtonInToolbar: bool = False
    ShowAttachmentButtonInToolbar: bool = False
    ShowViewButtonInToolbar: bool = False
    OpenFormType: int | None = None

    ValidationRules: list[ValidationRule] = Field(
        default_factory=lambda: [
            ValidationRule(Title="نام فرم", Name="InformationEntryFormName", InputType="text", IsRequired=True, Icon="form", Placeholder="نام فرم را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="نوع نمایش فرم", Name="OpenFormType", InputType="selectbox", IsRequired=True, Icon="display-type", Placeholder="نوع نمایش فرم را انتخاب کنید", IsReadonly=False, Disabled=False, Options=[
                DropdownOption(Label="Grid", Value=0),
                DropdownOption(Label="NewForm", Value=1),
            ]),
            ValidationRule(Title="نوع درج", Name="GridEditMode", InputType="selectbox", IsRequired=True, Icon="edit-mode", Placeholder="نوع درج را انتخاب کنید", IsReadonly=False, Disabled=False, Options=[
                DropdownOption(Label="InLine", Value=0),
                DropdownOption(Label="PopUp", Value=1),
                DropdownOption(Label="InCell", Value=2),
            ]),
            ValidationRule(Title="جدول مرتبط", Name="RelatedTable", InputType="dropdown", IsRequired=True, Icon="table", Placeholder="جدول مرتبط را انتخاب کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="فیلد مرتبط", Name="ExternalField", InputType="dropdown", IsRequired=True, Icon="field-link", Placeholder="فیلد مرتبط را انتخاب کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="فیلد گروهبندی", Name="GroupableField", InputType="dropdown", IsRequired=True, Icon="group", Placeholder="فیلد گروهبندی را انتخاب کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="تعداد نمایش رکورد", Name="ShowRecordCountDefault", InputType="number", IsRequired=False, Icon="row-count", Placeholder="تعداد رکوردهای پیشفرض را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="طول فرم", Name="Height", InputType="number", IsRequired=False, Icon="height", Placeholder="طول فرم را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="عرض فرم", Name="ColumnWidth", InputType="dropdown", IsRequired=False, Icon="width", Placeholder="عرض فرم را انتخاب کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="توضیحات فرم", Name="FormComment", InputType="text", IsRequired=False, Icon="comment", Placeholder="توضیحات فرم را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="عنوان دکمه ذخیره", Name="TitleSaveButton", InputType="text", IsRequired=False, Icon="save", Placeholder="عنوان دکمه ذخیره را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="آیکن", Name="Icon", InputType="icon-picker", IsRequired=False, Icon="image", Placeholder="آیکن را انتخاب کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="نمایش شناسه", Name="IsShowID", InputType="checkbox", IsRequired=False, Icon="id", Placeholder="", IsReadonly=False, Disabled=False),
            ValidationRule(Title="ذخیره بصورت یکجا", Name="SaveAtOnce", InputType="checkbox", IsRequired=False, Icon="save-all", Placeholder="", IsReadonly=False, Disabled=False),
            ValidationRule(Title="ذخیره والد مشروط ذخیره فرزند", Name="SaveParentSubjectSaveChild", InputType="checkbox", IsRequired=False, Icon="parent-child", Placeholder="", IsReadonly=False, Disabled=False),
            ValidationRule(Title="بررسی فرزند قبل از ذخیره", Name="CheckValidChildGrid", InputType="checkbox", IsRequired=False, Icon="validation", Placeholder="", IsReadonly=False, Disabled=False),
            ValidationRule(Title="نمایش در فرم والد", Name="ShowInParentForm", InputType="checkbox", IsRequired=False, Icon="parent-form", Placeholder="", IsReadonly=False, Disabled=False),
            ValidationRule(Title="نمایش در لیست منو", Name="ShowInMenuTreeList", InputType="checkbox", IsRequired=False, Icon="menu", Placeholder="", IsReadonly=False, Disabled=False),
            ValidationRule(Title="قابلیت صفحه بندی", Name="Pageable", InputType="checkbox", IsRequired=False, Icon="pagination", Placeholder="", IsReadonly=False, Disabled=False),
            ValidationRule(Title="تعداد ردیف در هر صفحه", Name="RowCountInPage", InputType="number", IsRequired=False, Icon="rows", Placeholder="تعداد ردیف در هر صفحه را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="قابلیت گروهبندی", Name="Groupable", InputType="checkbox", IsRequired=False, Icon="grouping", Placeholder="", IsReadonly=False, Disabled=False),
            ValidationRule(Title="نمایش زیر صفحه", Name="AggregateUsable", InputType="checkbox", IsRequired=False, Icon="aggregate", Placeholder="", IsReadonly=False, Disabled=False),
            ValidationRule(Title="نمایش ستون انتخاب", Name="ShowSelectedColumn", InputType="checkbox", IsRequired=False, Icon="select-column", Placeholder="", IsReadonly=False, Disabled=False),
            ValidationRule(Title="جستجو با onKeyDown", Name="SearchWithOnKeyDown", InputType="checkbox", IsRequired=False, Icon="search-key", Placeholder="", IsReadonly=False, Disabled=False),
            ValidationRule(Title="فرم جستجو مرتبط", Name="SearchWithOnKeyDown", InputType="dropdown", IsRequired=False, Icon="search-form", Placeholder="فرم جستجو را انتخاب کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="نمایش ستون ردیف", Name="ShowLineNumber", InputType="checkbox", IsRequired=False, Icon="row-number", Placeholder="", IsReadonly=False, Disabled=False),
            ValidationRule(Title="بستن فرم بعد از ذخیره", Name="IsCloseFormAfterSave", InputType="checkbox", IsRequired=False, Icon="close", Placeholder="", IsReadonly=False, Disabled=False),
            ValidationRule(Title="نمایش دکمه جدید در فرم", Name="ShowNewButton", InputType="checkbox", IsRequired=False, Icon="new", Placeholder="", IsReadonly=False, Disabled=False),
            ValidationRule(Title="نمایش دکمه پاک کردن فرم به استثناء", Name="ShowClearFormWithOutFixItemButton", InputType="checkbox", IsRequired=False, Icon="clear", Placeholder="", IsReadonly=False, Disabled=False),
            ValidationRule(Title="عنوان دکمه پاک کردن فرم به استثناء", Name="ClearFormWithOutFixItemButtonName", InputType="text", IsRequired=False, Icon="button-text", Placeholder="عنوان دکمه را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="فیلد های استثناء پاک کردن", Name="FixItemClearForm", InputType="text", IsRequired=False, Icon="exclude", Placeholder="فیلدهای استثناء را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="ستون پیشفرض نمایش گرید", Name="DefaultColumnShowInGrid", InputType="text", IsRequired=False, Icon="column-default", Placeholder="ستون های پیشفرض را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="فیلد های عدم تکرار در ایجاد ردیف", Name="CheckFieldDuplicateRecords", InputType="text", IsRequired=False, Icon="unique", Placeholder="فیلدهای منحصر بفرد را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="صفحه دکمه جدید", Name="NewPageUrl", InputType="url", IsRequired=False, Icon="new-page", Placeholder="آدرس صفحه جدید را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="صفحه دکمه ویرایش", Name="UpdatePageUrl", InputType="url", IsRequired=False, Icon="edit-page", Placeholder="آدرس صفحه ویرایش را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="فرم طراحی شده", Name="EditorFormJson", InputType="form-designer", IsRequired=False, Icon="design", Placeholder="", IsReadonly=False, Disabled=False),
            ValidationRule(Title="کوئری نمایش دکمه جدید", Name="NewButtonVisibleConditionQuery", InputType="textarea", IsRequired=False, Icon="query", Placeholder="کوئری نمایش دکمه جدید را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="کوئری", Name="Query", InputType="textarea", IsRequired=False, Icon="query", Placeholder="کوئری اصلی را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="شرط کوئری", Name="ConditionQuery", InputType="textarea", IsRequired=False, Icon="condition", Placeholder="شرط کوئری را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="گروهبندی کوئری", Name="GroupByQuery", InputType="textarea", IsRequired=False, Icon="group-query", Placeholder="کوئری گروهبندی را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="ترتیب کوئری", Name="OrderQuery", InputType="textarea", IsRequired=False, Icon="sort", Placeholder="کوئری مرتب سازی را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="CSS", Name="CSS", InputType="textarea", IsRequired=False, Icon="css", Placeholder="کد CSS را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="توضیحات برنامه نویس/تحلیلگر", Name="AnalystDescription", InputType="textarea", IsRequired=False, Icon="developer", Placeholder="توضیحات فنی را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="نمایش ضمیمه در فرم", Name="ShowAttachment", InputType="checkbox", IsRequired=False, Icon="attachment", Placeholder="", IsReadonly=False, Disabled=False),
            ValidationRule(Title="طول ضمیمه", Name="HeightAttachment", InputType="number", IsRequired=False, Icon="height", Placeholder="طول بخش ضمیمه را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="عرض ضمیمه", Name="AttachmentColumnWidth", InputType="dropdown", IsRequired=False, Icon="width", Placeholder="عرض ستون ضمیمه را انتخاب کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="نمایش دکمه ضمیمه", Name="ShowAttachmentButton", InputType="checkbox", IsRequired=False, Icon="attachment-button", Placeholder="", IsReadonly=False, Disabled=False),
            ValidationRule(Title="نمایش جزئیات ضمیمه در فرم", Name="ShowDetailAttachment", InputType="checkbox", IsRequired=False, Icon="attachment-detail", Placeholder="", IsReadonly=False, Disabled=False),
            ValidationRule(Title="نمایش ستون ضمیمه", Name="ShowAttachmentColumn", InputType="checkbox", IsRequired=False, Icon="attachment-column", Placeholder="", IsReadonly=False, Disabled=False),
            ValidationRule(Title="ستون ضمیمه", Name="AttachmentColumnName", InputType="dropdown", IsRequired=False, Icon="attachment-field", Placeholder="ستون ضمیمه را انتخاب کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="نمایش بصورت چارت", Name="ShowChartInformationEntryForm", InputType="checkbox", IsRequired=False, Icon="chart", Placeholder="", IsReadonly=False, Disabled=False),
            ValidationRule(Title="ستون شناسه", Name="ChartID", InputType="text", IsRequired=False, Icon="chart-id", Placeholder="ستون شناسه چارت را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="ستون نام", Name="ChartName", InputType="text", IsRequired=False, Icon="chart-name", Placeholder="ستون نام چارت را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="ستون عنوان", Name="ChartTitle", InputType="text", IsRequired=False, Icon="chart-title", Placeholder="ستون عنوان چارت را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="ستون والد", Name="ChartParentID", InputType="text", IsRequired=False, Icon="chart-parent", Placeholder="ستون والد چارت را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="ستون گروه", Name="ChartGroup", InputType="text", IsRequired=False, Icon="chart-group", Placeholder="ستون گروه چارت را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="ستون تصویر", Name="ChartAvatar", InputType="text", IsRequired=False, Icon="chart-image", Placeholder="ستون تصویر چارت را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="عنوان", Name="BadgeTitle", InputType="text", IsRequired=False, Icon="badge", Placeholder="عنوان برچسب را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="رنگ زمینه", Name="BadgeColor", InputType="color", IsRequired=False, Icon="background", Placeholder="رنگ زمینه برچسب را انتخاب کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="رنگ متن", Name="BadgeTextColor", InputType="color", IsRequired=False, Icon="text-color", Placeholder="رنگ متن برچسب را انتخاب کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="کوئری", Name="BadgeQuery", InputType="textarea", IsRequired=False, Icon="query", Placeholder="کوئری برچسب را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="نام ستون", Name="RowColorColumnName", InputType="dropdown", IsRequired=False, Icon="column", Placeholder="ستون رنگ سطر را انتخاب کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="نوع عملگر", Name="RowColorOperator", InputType="dropdown", IsRequired=False, Icon="operator", Placeholder="عملگر را انتخاب کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="مقدار ستون", Name="RowColorColumnValue", InputType="text", IsRequired=False, Icon="value", Placeholder="مقدار مقایسه را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="رنگ سطر", Name="RowColorSelectedColor", InputType="dropdown", IsRequired=False, Icon="color", Placeholder="رنگ سطر را انتخاب کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="دکمه جدید", Name="ShowNewButtonInToolbar", InputType="checkbox", IsRequired=False, Icon="new", Placeholder="", IsReadonly=False, Disabled=False),
            ValidationRule(Title="دکمه ضمیمه", Name="ShowAttachmentButtonInToolbar", InputType="checkbox", IsRequired=False, Icon="attachment", Placeholder="", IsReadonly=False, Disabled=False),
            ValidationRule(Title="دکمه ویرایش", Name="ShowUpdateButtonInToolbar", InputType="checkbox", IsRequired=False, Icon="edit", Placeholder="", IsReadonly=False, Disabled=False),
            ValidationRule(Title="دکمه حذف", Name="ShowDeleteButtonInToolbar", InputType="checkbox", IsRequired=False, Icon="delete", Placeholder="", IsReadonly=False, Disabled=False),
            ValidationRule(Title="دکمه مشاهده", Name="ShowViewButtonInToolbar", InputType="checkbox", IsRequired=False, Icon="view", Placeholder="", IsReadonly=False, Disabled=False),
        ]
    )
