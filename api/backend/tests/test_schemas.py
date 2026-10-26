"""Unit tests for Pydantic DTO models and validations."""

import unittest
from pydantic import ValidationError

from app.schemas.category import CategoryCreateDTO, CategoryUpdateDTO
from app.schemas.product import ProductCreateDTO, ProductUpdateDTO


class TestPydanticSchemas(unittest.TestCase):
    """Verify DTO validation behavior and constraints."""

    def test_category_create_valid(self):
        dto = CategoryCreateDTO(
            name="ابری و زیرساخت",
            slug="cloud-infra",
            description="خدمات سرورهای ابری",
        )
        self.assertEqual(dto.name, "ابری و زیرساخت")
        self.assertEqual(dto.slug, "cloud-infra")
        self.assertEqual(dto.description, "خدمات سرورهای ابری")

    def test_category_create_requires_name_and_slug(self):
        with self.assertRaises(ValidationError):
            CategoryCreateDTO(name="", slug="valid-slug")  # empty name fails min_length=1

        with self.assertRaises(ValidationError):
            CategoryCreateDTO(name="Valid Name", slug="")  # empty slug fails min_length=1

    def test_category_update_optional_fields(self):
        dto = CategoryUpdateDTO(name="نام جدید")
        self.assertEqual(dto.name, "نام جدید")
        self.assertIsNone(dto.slug)
        self.assertIsNone(dto.description)

    def test_product_create_valid_and_defaults(self):
        dto = ProductCreateDTO(
            title="سامانه مانیتورینگ ابری",
            slug="cloud-monitoring",
            category_id=1,
        )
        self.assertEqual(dto.title, "سامانه مانیتورینگ ابری")
        self.assertEqual(dto.slug, "cloud-monitoring")
        self.assertEqual(dto.category_id, 1)
        self.assertFalse(dto.is_featured)  # Default
        self.assertTrue(dto.is_active)  # Default

    def test_product_create_requires_title_and_slug(self):
        with self.assertRaises(ValidationError):
            ProductCreateDTO(title="", slug="slug")

        with self.assertRaises(ValidationError):
            ProductCreateDTO(title="Title", slug="")


if __name__ == "__main__":
    unittest.main()
