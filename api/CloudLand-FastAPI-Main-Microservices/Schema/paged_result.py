from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, model_validator

from Schema.base import dotnet_pascal

T = TypeVar("T")


class PagedResult(BaseModel, Generic[T]):
    model_config = ConfigDict(populate_by_name=True, alias_generator=dotnet_pascal)

    items: list[T]
    total_count: int
    page_index: int
    page_size: int
    total_pages: int = 0

    @model_validator(mode="after")
    def _compute_total_pages(self) -> "PagedResult[T]":
        if self.page_size > 0:
            self.total_pages = (self.total_count + self.page_size - 1) // self.page_size
        return self
