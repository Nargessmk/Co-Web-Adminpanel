from pydantic import Field

from Schema.AppManagement.node_objects.base import DropdownOption, NodeObjectDTO, ValidationRule

class ComputationalFieldDTO(NodeObjectDTO):
    Query: str | None = None
    ShowInForm: bool = False
    IsDefaultView: bool = False
    IsWide: bool = False
    FieldType: int | None = None
    DigitsAfterDecimal: int | None = None
    MaxValue: float | None = None
    MinValue: float | None = None
    DisplayName: str | None = None
    FieldComment: str | None = None

    ValidationRules: list[ValidationRule] = Field(
        default_factory=lambda: [
            ValidationRule(Title="کوئری محاسباتی", Name="Query", InputType="textarea", IsRequired=True, Icon="code", Placeholder="کوئری محاسباتی را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="نام نمایشی", Name="DisplayName", InputType="text", IsRequired=True, Icon="text-field", Placeholder="نام نمایشی فیلد را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="توضیحات فیلد", Name="FieldComment", InputType="textarea", IsRequired=False, Icon="comment", Placeholder="توضیحات فیلد را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="نمایش در فرم", Name="ShowInForm", InputType="checkbox", IsRequired=False, Icon="form", Placeholder="", IsReadonly=False, Disabled=False),
            ValidationRule(Title="نمایش پیش فرض", Name="IsDefaultView", InputType="checkbox", IsRequired=False, Icon="eye", Placeholder="", IsReadonly=False, Disabled=False),
            ValidationRule(Title="نمایش عریض", Name="IsWide", InputType="checkbox", IsRequired=False, Icon="width", Placeholder="", IsReadonly=False, Disabled=False),
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
            ValidationRule(Title="اعداد بعد از اعشار", Name="DigitsAfterDecimal", InputType="number", IsRequired=False, Icon="decimal", Placeholder="تعداد ارقام اعشار را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="حداقل مقدار", Name="MinValue", InputType="number", IsRequired=False, Icon="min", Placeholder="حداقل مقدار مجاز را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="حداکثر مقدار", Name="MaxValue", InputType="number", IsRequired=False, Icon="max", Placeholder="حداکثر مقدار مجاز را وارد کنید", IsReadonly=False, Disabled=False),
        ]
    )
