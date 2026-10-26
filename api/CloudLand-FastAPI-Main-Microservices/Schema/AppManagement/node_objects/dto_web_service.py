from pydantic import Field

from Schema.AppManagement.node_objects.base import NodeObjectDTO, ValidationRule

class WebServiceDTO(NodeObjectDTO):
    Name: str | None = None
    URL: str | None = None
    ExportType: str | None = None

    ValidationRules: list[ValidationRule] = Field(
        default_factory=lambda: [
            ValidationRule(Title="نام وب سرویس", Name="Name", InputType="text", IsRequired=True, Icon="webservice", Placeholder="نام وب سرویس را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="آدرس وب سرویس", Name="URL", InputType="text", IsRequired=True, Icon="url", Placeholder="آدرس کامل وب سرویس را وارد کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="نوع خروجی", Name="ExportType", InputType="selectbox", IsRequired=True, Icon="data-type", Placeholder="نوع داده خروجی را انتخاب کنید", IsReadonly=False, Disabled=False),
        ]
    )
