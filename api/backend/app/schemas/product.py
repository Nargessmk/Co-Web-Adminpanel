"""Product validation schemas and DTOs."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class ProductBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="Product title")
    slug: str = Field(..., min_length=1, max_length=255, description="URL-friendly slug")
    short_description: Optional[str] = Field(None, description="Brief summary")
    description: Optional[str] = Field(None, description="Full description or markdown")
    category_id: Optional[int] = Field(None, description="ID of category")
    is_featured: bool = Field(default=False)
    is_active: bool = Field(default=True)
    url: Optional[str] = None
    badge: Optional[str] = None
    metrics_json: Optional[Any] = None
    tags_json: Optional[Any] = None


class ProductCreateDTO(ProductBase):
    image_url: Optional[str] = None


class ProductUpdateDTO(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    slug: Optional[str] = Field(None, min_length=1, max_length=255)
    short_description: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[int] = None
    image_url: Optional[str] = None
    is_featured: Optional[bool] = None
    is_active: Optional[bool] = None
    url: Optional[str] = None
    badge: Optional[str] = None
    metrics_json: Optional[Any] = None
    tags_json: Optional[Any] = None


class ProductFilterDTO(BaseModel):
    category: Optional[str] = None
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=6, ge=1, le=100)


class ProductResponse(ProductBase):
    id: int
    image_url: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    category_name: Optional[str] = None
    category_slug: Optional[str] = None
