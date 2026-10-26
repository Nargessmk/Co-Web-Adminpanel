from pydantic import Field

from Schema.AppManagement.node_objects.base import DropdownOption, NodeObjectDTO, ValidationRule

class TableAttachmentDTO(NodeObjectDTO):
    FullName: str | None = None
    AllowedExtensions: list[str] | None = None
    AttachmentUploadType: int | None = None
    AttachmentUploadSize: int | None = None
    CoreObjectID: int | None = None
    MaxFileSize: int | None = None
    MinFileSize: int | None = None
    IsRequired: bool = False
    ShowDefault: bool = False
    SaveInDatabase: bool = False
    AutoFillQuery: str | None = None
    ColumnWidth: str | None = None

    ValidationRules: list[ValidationRule] = Field(
        default_factory=lambda: [
            ValidationRule(Title="نام پیوست", Name="FullName", InputType="text", IsRequired=True, Icon="attachment", Placeholder="نام پیوست را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="نوع بارگذاری ضمیمه", Name="AttachmentUploadType", InputType="selectbox", IsRequired=True, Icon="upload-type", Placeholder="نوع بارگذاری را انتخاب کنید", IsReadonly=False, Disabled=False, Options=[
                DropdownOption(Label="بارگذاری", Value=0),
                DropdownOption(Label="اسکن", Value=1),
                DropdownOption(Label="وبکم", Value=2),
            ]),
            ValidationRule(Title="اندازه ضمیمه", Name="AttachmentUploadSize", InputType="selectbox", IsRequired=True, Icon="upload-size", Placeholder="اندازه ضمیمه را انتخاب کنید", IsReadonly=False, Disabled=False, Options=[
                DropdownOption(Label="کوچک", Value=0),
                DropdownOption(Label="متوسط", Value=1),
                DropdownOption(Label="بزرگ", Value=2),
            ]),
            ValidationRule(Title="پسوندهای مجاز", Name="AllowedExtensions", InputType="multiselect", IsRequired=True, Icon="file-extensions", Placeholder="پسوندهای مجاز را انتخاب کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="حداکثر حجم فایل (KB)", Name="MaxFileSize", InputType="number", IsRequired=True, Icon="file-size-max", Placeholder="حداکثر حجم را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="حداقل حجم فایل (KB)", Name="MinFileSize", InputType="number", IsRequired=True, Icon="file-size-min", Placeholder="حداقل حجم را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="عرض ستون", Name="ColumnWidth", InputType="selectbox", IsRequired=True, Icon="column-width", Placeholder="عرض ستون را انتخاب کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="ضروری", Name="IsRequired", InputType="switch", IsRequired=False, Icon="required", Placeholder="", IsReadonly=False, Disabled=False),
            ValidationRule(Title="نمایش پیشفرض", Name="ShowDefault", InputType="switch", IsRequired=False, Icon="eye", Placeholder="", IsReadonly=False, Disabled=False),
            ValidationRule(Title="ذخیره در پایگاه داده", Name="SaveInDatabase", InputType="switch", IsRequired=False, Icon="database-save", Placeholder="", IsReadonly=False, Disabled=False),
            ValidationRule(Title="دستور پر کردن خودکار", Name="AutoFillQuery", InputType="textarea", IsRequired=False, Icon="auto-fill", Placeholder="دستور SQL را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="شناسه شیء اصلی", Name="CoreObjectID", InputType="number", IsRequired=True, Icon="object-id", Placeholder="", IsReadonly=True, Disabled=True),
        ]
    )
