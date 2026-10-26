"""Category validation schemas and DTOs."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Category display name")
    slug: str = Field(..., min_length=1, max_length=255, description="Category URL-friendly slug")
    description: Optional[str] = Field(None, description="Optional description")


class CategoryCreateDTO(CategoryBase):
    pass


class CategoryUpdateDTO(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    slug: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None


class CategorySortOrderDTO(BaseModel):
    id: int
    sort_order: int


class CategoryResponse(CategoryBase):
    id: int
    sort_order: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
