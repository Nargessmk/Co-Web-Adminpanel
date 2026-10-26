"""Initial baseline schema migration for CloudLand

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-10-26 18:30:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Product Categories
    op.execute("""
    CREATE TABLE IF NOT EXISTS product_categories (
      id          SERIAL PRIMARY KEY,
      name        VARCHAR(255) NOT NULL,
      slug        VARCHAR(255) NOT NULL UNIQUE,
      description TEXT,
      sort_order  INTEGER,
      created_at  TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
      updated_at  TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
    CREATE INDEX IF NOT EXISTS product_categories_sort_order_idx ON product_categories (sort_order);
    """)

    # 2. Products
    op.execute("""
    CREATE TABLE IF NOT EXISTS products (
      id                SERIAL PRIMARY KEY,
      title             VARCHAR(255) NOT NULL,
      slug              VARCHAR(255) NOT NULL UNIQUE,
      short_description TEXT,
      description       TEXT,
      image_url         TEXT,
      url               TEXT,
      badge             VARCHAR(100),
      metrics_json      TEXT,
      tags_json         TEXT,
      category_id       INTEGER REFERENCES product_categories(id) ON DELETE SET NULL,
      is_featured       BOOLEAN NOT NULL DEFAULT FALSE,
      is_active         BOOLEAN NOT NULL DEFAULT TRUE,
      created_at        TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
      updated_at        TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
    CREATE INDEX IF NOT EXISTS idx_products_category_id ON products(category_id);
    CREATE INDEX IF NOT EXISTS idx_products_is_active ON products(is_active);
    """)

    # 3. Product Catalogs, Images, Videos
    op.execute("""
    CREATE TABLE IF NOT EXISTS product_catalogs (
      id         SERIAL PRIMARY KEY,
      product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
      title      VARCHAR(255) NOT NULL,
      file_url   TEXT,
      created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
    CREATE INDEX IF NOT EXISTS idx_catalogs_product_id ON product_catalogs(product_id);

    CREATE TABLE IF NOT EXISTS product_images (
      id         SERIAL PRIMARY KEY,
      product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
      image_url  TEXT NOT NULL,
      sort_order INTEGER NOT NULL DEFAULT 0,
      created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
    CREATE INDEX IF NOT EXISTS idx_product_images_product_id ON product_images(product_id);

    CREATE TABLE IF NOT EXISTS product_videos (
      id            SERIAL PRIMARY KEY,
      product_id    INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
      video_url     TEXT NOT NULL,
      thumbnail_url TEXT,
      sort_order    INTEGER NOT NULL DEFAULT 0,
      title         TEXT,
      created_at    TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
    CREATE INDEX IF NOT EXISTS idx_product_videos_product_id ON product_videos(product_id);
    """)

    # 4. Consultations
    op.execute("""
    CREATE TABLE IF NOT EXISTS consultations (
      id           SERIAL PRIMARY KEY,
      full_name    VARCHAR(255) NOT NULL,
      phone        VARCHAR(50) NOT NULL,
      email        VARCHAR(255),
      company_name VARCHAR(255),
      subject      VARCHAR(255) NOT NULL,
      message      TEXT,
      status       VARCHAR(50) NOT NULL DEFAULT 'new',
      created_at   TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
      updated_at   TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
    CREATE INDEX IF NOT EXISTS idx_consultations_status ON consultations(status);
    """)


def downgrade() -> None:
    op.execute("""
    DROP TABLE IF EXISTS consultations CASCADE;
    DROP TABLE IF EXISTS product_videos CASCADE;
    DROP TABLE IF EXISTS product_images CASCADE;
    DROP TABLE IF EXISTS product_catalogs CASCADE;
    DROP TABLE IF EXISTS products CASCADE;
    DROP TABLE IF EXISTS product_categories CASCADE;
    """)
