from pydantic import Field

from Schema.AppManagement.node_objects.base import DropdownOption, NodeObjectDTO, ValidationRule

class FieldDTO(NodeObjectDTO):
    FieldName: str | None = None
    DisplayName: str | None = None
    FieldNature: str | None = None
    FieldType: int | None = None
    FieldDisplayType: int | None = None
    IsEditAble: bool = False
    IsDefaultView: bool = False
    IsRequired: bool = False
    RelatedTable: int | None = None
    ViewCommand: str | None = None
    SpecialValue: str | None = None
    DefaultValue: str | None = None
    IsDefaultViewRadioBox: bool = False
    IsLeftWrite: bool = False
    IsIdentity: bool = False
    IsVirtual: bool = False
    IsTableAttachment: bool = False
    IsWide: bool = False
    ActiveOnKeyDown: bool = False
    IsExclusive: bool = False
    ShowInForm: bool = False
    Folder: str | None = None
    DigitsAfterDecimal: int | None = None
    RelatedFieldCommand: int | None = None
    Class: str | None = None
    ClearAfterChange: bool = False
    FieldComment: str | None = None
    MinValue: float | None = None
    MaxValue: float | None = None
    AutoFillQuery: str | None = None
    TextColor: str | None = None
    SearchAutoCompleteCount: int | None = None
    GridTextColor: str | None = None
    RelatedLink: str | None = None
    ColumnWidth: str | None = None
    AnalystDescription: str | None = None

    ValidationRules: list[ValidationRule] = Field(
        default_factory=lambda: [
            ValidationRule(Title="نام فیلد", Name="FieldName", InputType="text", IsRequired=True, Icon="field", Placeholder="نام فیلد را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="نام نمایشی", Name="DisplayName", InputType="text", IsRequired=False, Icon="text-field", Placeholder="نام نمایشی فیلد را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="نوع فیلد", Name="FieldType", InputType="selectbox", IsRequired=True, Icon="type", Placeholder="نوع فیلد را انتخاب کنید", IsReadonly=False, Disabled=False, Options=[
                DropdownOption(Label="ShortText", Value=0),
                DropdownOption(Label="LongText", Value=1),
                DropdownOption(Label="Number", Value=2),
                DropdownOption(Label="TwoValues", Value=3),
                DropdownOption(Label="SingleSelectList", Value=4),
                DropdownOption(Label="RelatedTable", Value=5),
                DropdownOption(Label="Image", Value=6),
                DropdownOption(Label="Map", Value=7),
                DropdownOption(Label="Password", Value=8),
                DropdownOption(Label="Phone", Value=9),
                DropdownOption(Label="PersianDateTime", Value=10),
                DropdownOption(Label="MiladyDateTime", Value=11),
                DropdownOption(Label="Clock", Value=12),
                DropdownOption(Label="Money", Value=13),
                DropdownOption(Label="UserRole", Value=14),
                DropdownOption(Label="Plaque", Value=15),
                DropdownOption(Label="Icon", Value=16),
                DropdownOption(Label="ExternalField", Value=17),
                DropdownOption(Label="ActionType", Value=18),
                DropdownOption(Label="ComboBox", Value=19),
                DropdownOption(Label="NationalCode", Value=20),
                DropdownOption(Label="CoreRelatedTable", Value=21),
                DropdownOption(Label="NotificationType", Value=22),
                DropdownOption(Label="RecordType", Value=23),
                DropdownOption(Label="Editor", Value=24),
                DropdownOption(Label="AttachmentUploadType", Value=25),
                DropdownOption(Label="Sparkline", Value=26),
                DropdownOption(Label="Color", Value=27),
                DropdownOption(Label="MultiSelect", Value=29),
                DropdownOption(Label="BPMSModel", Value=30),
                DropdownOption(Label="xml", Value=31),
                DropdownOption(Label="Binery", Value=32),
                DropdownOption(Label="Query", Value=33),
                DropdownOption(Label="Attachment", Value=34),
                DropdownOption(Label="FillTextAutoComplete", Value=35),
                DropdownOption(Label="RelatedTableTree", Value=36),
                DropdownOption(Label="Upload", Value=37),
                DropdownOption(Label="ViewerForm", Value=38),
                DropdownOption(Label="Rating", Value=39),
                DropdownOption(Label="CoreRelatedTableCheckbox", Value=40),
                DropdownOption(Label="MultiSelectFromRelatedTable", Value=41),
                DropdownOption(Label="MultiSelectFromComboBox", Value=42),
            ]),
            ValidationRule(Title="نوع نمایش فیلد", Name="FieldDisplayType", InputType="selectbox", IsRequired=False, Icon="display", Placeholder="نوع نمایش را انتخاب کنید", IsReadonly=False, Disabled=False, Options=[
                DropdownOption(Label="عمودی", Value=0),
                DropdownOption(Label="افقی", Value=1),
            ]),
            ValidationRule(Title="توضیحات فیلد", Name="FieldComment", InputType="text", IsRequired=False, Icon="comment", Placeholder="توضیحات فیلد را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="قابل ویرایش", Name="IsEditAble", InputType="checkbox", IsRequired=False, Icon="edit", Placeholder="", IsReadonly=False, Disabled=False),
            ValidationRule(Title="مشاهده پیشفرض", Name="IsDefaultView", InputType="checkbox", IsRequired=False, Icon="eye", Placeholder="", IsReadonly=False, Disabled=False),
            ValidationRule(Title="ضروری", Name="IsRequired", InputType="checkbox", IsRequired=False, Icon="required", Placeholder="", IsReadonly=False, Disabled=False),
            ValidationRule(Title="چپ چین", Name="IsLeftWrite", InputType="checkbox", IsRequired=False, Icon="align-left", Placeholder="", IsReadonly=False, Disabled=False),
            ValidationRule(Title="منحصر به فرد", Name="IsExclusive", InputType="checkbox", IsRequired=False, Icon="unique", Placeholder="", IsReadonly=False, Disabled=False),
            ValidationRule(Title="نمایش در فرم", Name="ShowInForm", InputType="checkbox", IsRequired=False, Icon="form", Placeholder="", IsReadonly=False, Disabled=False),
            ValidationRule(Title="فعال کردن KeyDown", Name="ActiveOnKeyDown", InputType="checkbox", IsRequired=False, Icon="keyboard", Placeholder="", IsReadonly=False, Disabled=False),
            ValidationRule(Title="پاک کردن فرم بعد از تغییر", Name="ClearAfterChange", InputType="checkbox", IsRequired=False, Icon="clear", Placeholder="", IsReadonly=False, Disabled=False),
            ValidationRule(Title="جدول مرتبط", Name="RelatedTable", InputType="dropdown", IsRequired=False, Icon="table", Placeholder="جدول مرتبط را انتخاب کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="فیلد مرتبط", Name="RelatedField", InputType="dropdown", IsRequired=False, Icon="field-link", Placeholder="فیلد مرتبط را انتخاب کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="شرط فیلد مرتبط", Name="RelatedFieldCommand", InputType="dropdown", IsRequired=False, Icon="field-condition", Placeholder="شرط فیلد مرتبط را انتخاب کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="مقدار پیشفرض", Name="DefaultValue", InputType="text", IsRequired=False, Icon="default", Placeholder="مقدار پیشفرض را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="مقدار ویژه", Name="SpecialValue", InputType="textarea", IsRequired=False, Icon="special", Placeholder="مقدار ویژه را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="تعداد رقم بعد اعشار", Name="DigitsAfterDecimal", InputType="number", IsRequired=False, Icon="decimal", Placeholder="تعداد ارقام اعشار را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="بیشترین مقدار", Name="MaxValue", InputType="number", IsRequired=False, Icon="max", Placeholder="حداکثر مقدار را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="کمترین مقدار", Name="MinValue", InputType="number", IsRequired=False, Icon="min", Placeholder="حداقل مقدار را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="عرض فیلد", Name="ColumnWidth", InputType="dropdown", IsRequired=False, Icon="width", Placeholder="عرض فیلد را انتخاب کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="رنگ متن", Name="TextColor", InputType="color", IsRequired=False, Icon="text-color", Placeholder="رنگ متن را انتخاب کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="رنگ متن گرید", Name="GridTextColor", InputType="dropdown", IsRequired=False, Icon="grid-color", Placeholder="رنگ متن گرید را انتخاب کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="لینک مرتبط", Name="RelatedLink", InputType="url", IsRequired=False, Icon="link", Placeholder="لینک مرتبط را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="کلاس", Name="Class", InputType="text", IsRequired=False, Icon="css", Placeholder="کلاس CSS را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="دستور نمایشی", Name="ViewCommand", InputType="textarea", IsRequired=False, Icon="code", Placeholder="دستور نمایشی را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="دستور پر کردن خودکار", Name="AutoFillQuery", InputType="textarea", IsRequired=False, Icon="auto-fill", Placeholder="دستور پر کردن خودکار را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="تعداد کارکتر جهت جستجو", Name="SearchAutoCompleteCount", InputType="number", IsRequired=False, Icon="search", Placeholder="تعداد کاراکتر برای جستجو را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="توضیحات برنامه نویس/تحلیلگر", Name="AnalystDescription", InputType="textarea", IsRequired=False, Icon="developer", Placeholder="توضیحات فنی را وارد کنید", IsReadonly=False, Disabled=False),
        ]
    )
