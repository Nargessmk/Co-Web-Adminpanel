from dataclasses import dataclass
from uuid import UUID

FOLDER_NODE_TYPE_ID = UUID("ec640c73-0bda-42ee-b7f7-f946ea3354dd")
TABLE_NODE_TYPE_ID = UUID("47dbacd7-4f0d-4022-a044-7c7d1beff42f")


@dataclass(frozen=True)
class FolderItemDTO:
    parent_title: str
    parent_node_type_id: UUID
    folder_title: str
    folder_icon: str


FOLDER_LIST: list[FolderItemDTO] = [
    FolderItemDTO("جدول", TABLE_NODE_TYPE_ID, "فیلد", "table-rows"),
    FolderItemDTO("جدول", TABLE_NODE_TYPE_ID, "رویداد", "code"),
    FolderItemDTO("جدول", TABLE_NODE_TYPE_ID, "ضمیمه", "file-invoice"),
]
