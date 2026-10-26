from pydantic import Field

from Schema.AppManagement.node_objects.base import NodeObjectDTO, ValidationRule

class TableDTO(NodeObjectDTO):
    FullName: str | None = None
    DisplayName: str | None = None
    Comment: str | None = None
    TABLESCHEMA: str | None = None
    ShowRecordCountDefault: int | None = None
    AnalystDescription: str | None = None

    ValidationRules: list[ValidationRule] = Field(
        default_factory=lambda: [
            ValidationRule(Title="نام کامل جدول", Name="FullName", InputType="text", IsRequired=True, Icon="table", Placeholder="نام کامل جدول را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="نام نمایشی", Name="DisplayName", InputType="text", IsRequired=False, Icon="display-name", Placeholder="نام نمایشی جدول را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="پیغام نمایشی", Name="Comment", InputType="text", IsRequired=False, Icon="comment", Placeholder="پیغام نمایشی را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="نام کاربر امنیتی جدول", Name="TABLESCHEMA", InputType="text", IsRequired=False, Icon="schema", Placeholder="نام schema را وارد کنید (مثلاً dbo)", IsReadonly=False, Disabled=False),
            ValidationRule(Title="تعداد نمایش رکورد پیش‌فرض", Name="ShowRecordCountDefault", InputType="number", IsRequired=False, Icon="record-count", Placeholder="تعداد رکوردهای نمایش داده شده را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="توضیحات تحلیلگر", Name="AnalystDescription", InputType="textarea", IsRequired=False, Icon="analysis", Placeholder="توضیحات تحلیل و برنامه‌نویسی را وارد کنید", IsReadonly=False, Disabled=False),
        ]
    )
