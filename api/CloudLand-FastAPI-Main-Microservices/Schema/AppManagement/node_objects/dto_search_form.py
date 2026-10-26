from pydantic import Field

from Schema.AppManagement.node_objects.base import NodeObjectDTO, ValidationRule

class SearchFormDTO(NodeObjectDTO):
    RelatedTable: int | None = None
    FullName: str | None = None
    Query: str | None = None
    GroupByQuery: str | None = None
    ConditionQuery: str | None = None
    CommonConditionQuery: str | None = None
    SelectedColumns: str | None = None
    Icon: str | None = None
    ShowIcon: bool = False
    ShowText: bool = False
    ClearGridAfterSearch: bool = False
    SearchConditionQuery: str | None = None
    SearchAlarmQuery: str | None = None

    ValidationRules: list[ValidationRule] = Field(
        default_factory=lambda: [
            ValidationRule(Title="نام فرم جستجو", Name="FullName", InputType="text", IsRequired=True, Icon="search-form", Placeholder="نام فرم جستجو را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="جدول مرتبط", Name="RelatedTable", InputType="selectbox", IsRequired=True, Icon="table-link", Placeholder="جدول مرتبط را انتخاب کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="آیکن", Name="Icon", InputType="text", IsRequired=True, Icon="image", Placeholder="نام آیکن را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="نمایش آیکن", Name="ShowIcon", InputType="switch", IsRequired=True, Icon="eye", Placeholder="", IsReadonly=False, Disabled=False),
            ValidationRule(Title="نمایش نام", Name="ShowText", InputType="switch", IsRequired=True, Icon="text", Placeholder="", IsReadonly=False, Disabled=False),
            ValidationRule(Title="خالی کردن جدول بعد از جستجو", Name="ClearGridAfterSearch", InputType="switch", IsRequired=True, Icon="grid-clear", Placeholder="", IsReadonly=False, Disabled=False),
            ValidationRule(Title="کوئری اصلی", Name="Query", InputType="textarea", IsRequired=False, Icon="query", Placeholder="کوئری SQL را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="شرط", Name="ConditionQuery", InputType="textarea", IsRequired=False, Icon="condition", Placeholder="شرط SQL را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="شرط مشترک", Name="CommonConditionQuery", InputType="textarea", IsRequired=False, Icon="common-condition", Placeholder="شرط مشترک SQL را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="کوئری گروهبندی", Name="GroupByQuery", InputType="textarea", IsRequired=False, Icon="group-by", Placeholder="کوئری GROUP BY را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="ستون های انتخابی", Name="SelectedColumns", InputType="textarea", IsRequired=False, Icon="columns", Placeholder="ستون ها را با کاما جدا کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="شرط جستجو", Name="SearchConditionQuery", InputType="textarea", IsRequired=False, Icon="search-condition", Placeholder="شرط جستجو SQL را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="هشدار جستجو", Name="SearchAlarmQuery", InputType="textarea", IsRequired=False, Icon="alarm", Placeholder="کوئری هشدار جستجو را وارد کنید", IsReadonly=False, Disabled=False),
        ]
    )
