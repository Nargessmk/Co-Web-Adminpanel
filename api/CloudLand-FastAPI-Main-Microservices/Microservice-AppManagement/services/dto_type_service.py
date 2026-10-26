from Schema.AppManagement import node_objects as dto_package
from Schema.AppManagement.node_objects.base import NodeObjectDTO
from core.exceptions import ValidationError


class UnknownNodeTypeError(ValidationError):
    pass


class UnsupportedDtoTypeError(ValidationError):
    pass


NODE_TYPE_MAPPINGS: dict[str, str] = {
    "application": "ApplicationDTO",
    "database": "DatabaseDTO",
    "table": "TableDTO",
    "general": "PublicSettingDTO",
    "search field": "SearchFieldDTO",
    "display field": "DisplayFieldDTO",
    "field": "FieldDTO",
    "dashboard subset": "SubDashboardDTO",
    "attachment": "TableAttachmentDTO",
    "dashboard integration": "DashboardIntegrationDTO",
    "show field event": "ShowFieldEventDTO",
    "event": "TableEventDTO",
    "application manager setting": "AdminSettingDTO",
    "grid row color": "GridRowColorDTO",
    "function": "TableFunctionDTO",
    "calculation field": "ComputationalFieldDTO",
    "button": "ButtonDTO",
    "folder": "FolderDTO",
    "form": "InformationEntryFormDTO",
    "dashboard": "DashboardDTO",
    "special phrase": "SpecialPhraseDTO",
    "new button form": "NewButtonFormDTO",
    "report": "ReportDTO",
    "web service": "WebServiceDTO",
}


class DtoTypeService:
    def __init__(self) -> None:
        self.dto_type_map: dict[str, type[NodeObjectDTO]] = {}
        for name, value in vars(dto_package).items():
            if isinstance(value, type) and issubclass(value, NodeObjectDTO) and value is not NodeObjectDTO:
                self.dto_type_map[name] = value

    def convert_to_dto_type_name(self, node_type: str) -> str:
        dto_type_name = NODE_TYPE_MAPPINGS.get(node_type.lower())
        if dto_type_name is None:
            raise UnknownNodeTypeError(f"No mapping found for node type: {node_type}")
        return dto_type_name

    def resolve_dto_type(self, node_type: str) -> type[NodeObjectDTO]:
        dto_type_name = self.convert_to_dto_type_name(node_type)
        dto_type = self.dto_type_map.get(dto_type_name)
        if dto_type is None:
            raise UnsupportedDtoTypeError(f"The object type '{node_type}' is not supported.")
        return dto_type


_service: DtoTypeService | None = None


def get_dto_type_service() -> DtoTypeService:
    global _service
    if _service is None:
        _service = DtoTypeService()
    return _service
