from pydantic import Field

from Schema.AppManagement.node_objects.base import NodeObjectDTO, ValidationRule

class SpecialPhraseDTO(NodeObjectDTO):
    Query: str | None = None
    DataSourceID: int | None = None

    ValidationRules: list[ValidationRule] = Field(
        default_factory=lambda: [
            ValidationRule(Title="پایگاه داده مرتبط", Name="DataSourceID", InputType="selectbox", IsRequired=False, Icon="database-link", Placeholder="پایگاه داده را انتخاب کنید", IsReadonly=False, Disabled=False),
            ValidationRule(Title="کوئری", Name="Query", InputType="textarea", IsRequired=False, Icon="sql-query", Placeholder="کوئری SQL را وارد کنید", IsReadonly=False, Disabled=False),
        ]
    )
