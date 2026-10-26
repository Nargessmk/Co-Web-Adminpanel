from pydantic import Field

from Schema.AppManagement.node_objects.base import DropdownOption, NodeObjectDTO, ValidationRule

class DataSourceInfoDTO(NodeObjectDTO):
    UserName: str | None = None
    Password: str | None = None
    DataBase: str | None = None
    ServerName: str | None = None
    FilePath: str | None = None
    DataSourceType: int | None = None

    ValidationRules: list[ValidationRule] = Field(
        default_factory=lambda: [
            ValidationRule(Title="نوع منبع داده", Name="DataSourceType", InputType="selectbox", IsRequired=True, Icon="database-type", Placeholder="نوع منبع داده را انتخاب کنید", IsReadonly=False, Disabled=False, Options=[
                DropdownOption(Label="SQLSERVER", Value=0),
                DropdownOption(Label="EXCEL", Value=1),
                DropdownOption(Label="ACCESS", Value=2),
                DropdownOption(Label="MySql", Value=3),
            ]),
            ValidationRule(Title="نام سرور", Name="ServerName", InputType="text", IsRequired=False, Icon="server", Placeholder="نام یا آدرس سرور را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="نام پایگاه داده", Name="DataBase", InputType="text", IsRequired=False, Icon="database", Placeholder="نام پایگاه داده را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="نام کاربری", Name="UserName", InputType="text", IsRequired=False, Icon="user", Placeholder="نام کاربری را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="کلمه عبور", Name="Password", InputType="password", IsRequired=False, Icon="password", Placeholder="کلمه عبور را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="مسیر فایل", Name="FilePath", InputType="file-path", IsRequired=False, Icon="folder", Placeholder="مسیر فایل داده را وارد کنید", IsReadonly=False, Disabled=False),
        ]
    )
