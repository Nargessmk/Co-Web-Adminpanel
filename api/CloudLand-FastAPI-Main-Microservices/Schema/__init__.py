"""
Schema package initialization.
Exports shared schemas located at root of Schema package,
as well as submodules for each microservice.
"""

from Schema.base import BaseDTO, dotnet_pascal
from Schema.paged_result import PagedResult
from Schema.result import ResultDTO

__all__ = [
    "BaseDTO",
    "dotnet_pascal",
    "PagedResult",
    "ResultDTO",
]