"""
AppManagement Schemas initialization module.
"""

from Schema.base import BaseDTO
from Schema.AppManagement.calendar import CalendarDTO
from Schema.AppManagement.constant import ConstantDTO
from Schema.AppManagement.constant_recursive import ConstantRecursiveDTO
from Schema.AppManagement.permission import UserConstantPermissionDTO
from Schema.AppManagement.module_permission import (
    ModulePermissionItemDTO,
    ModulePermissionDTO,
    UpdateModulePermissionsRequest,
    EffectivePermissionsResponse,
)
from Schema.AppManagement.reindex_result import ReindexResult
from Schema.paged_result import PagedResult

__all__ = [
    "BaseDTO",
    "CalendarDTO",
    "ConstantDTO",
    "ConstantRecursiveDTO",
    "UserConstantPermissionDTO",
    "ModulePermissionItemDTO",
    "ModulePermissionDTO",
    "UpdateModulePermissionsRequest",
    "EffectivePermissionsResponse",
    "ReindexResult",
    "PagedResult",
]
