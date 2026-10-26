from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ResultDTO(BaseModel, Generic[T]):
    is_success: bool
    data: T | None = None
    message: str = ""
    errors: list[str] = []

    total_count: int | None = None
    page_number: int | None = None
    page_size: int | None = None
    total_pages: int | None = None

    @classmethod
    def success(cls, data: T, message: str = "عملیات موفقیت آمیز") -> "ResultDTO[T]":
        return cls(is_success=True, data=data, message=message)

    @classmethod
    def success_paged(
        cls,
        data: T,
        total_count: int,
        page_number: int,
        page_size: int,
        message: str = "Operation successful",
    ) -> "ResultDTO[T]":
        total_pages = (total_count + page_size - 1) // page_size if page_size > 0 else 0
        return cls(
            is_success=True,
            data=data,
            message=message,
            total_count=total_count,
            page_number=page_number,
            page_size=page_size,
            total_pages=total_pages,
        )

    @classmethod
    def failure(cls, message: str, errors: list[str] | None = None) -> "ResultDTO[T]":
        return cls(is_success=False, message=message, errors=errors or [])

    @classmethod
    def failure_with_data(cls, message: str, data: T) -> "ResultDTO[T]":
        return cls(is_success=False, message=message, data=data)
