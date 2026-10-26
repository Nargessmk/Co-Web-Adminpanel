from pydantic import Field

from Schema.AppManagement.node_objects.base import DropdownOption, NodeObjectDTO, ValidationRule

class DatabaseDTO(NodeObjectDTO):
    Source: str | None = None
    DataBase: str | None = None
    DBPassword: str | None = None
    DBUser: str | None = None
    versions: int | None = None

    ValidationRules: list[ValidationRule] = Field(
        default_factory=lambda: [
            ValidationRule(Title="منبع داده", Name="Source", InputType="text", IsRequired=False, Icon="database", Placeholder="آدرس سرور یا منبع داده را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="نام پایگاه داده", Name="DataBase", InputType="text", IsRequired=True, Icon="database", Placeholder="نام پایگاه داده را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="رمز عبور", Name="DBPassword", InputType="password", IsRequired=False, Icon="lock", Placeholder="رمز عبور پایگاه داده را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="نام کاربری", Name="DBUser", InputType="text", IsRequired=True, Icon="user", Placeholder="نام کاربری پایگاه داده را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="نسخه SQL", Name="versions", InputType="dropdown", IsRequired=False, Icon="version", Placeholder="نسخه SQL Server را انتخاب کنید", IsReadonly=False, Disabled=False, Options=[
                DropdownOption(Label="SQL2000", Value=0),
                DropdownOption(Label="SQL2008", Value=1),
                DropdownOption(Label="SQL2019", Value=2),
                DropdownOption(Label="SQL2022", Value=3),
            ]),
        ]
    )
