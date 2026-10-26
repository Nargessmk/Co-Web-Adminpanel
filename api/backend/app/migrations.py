"""Automated database schema migrations for CloudLand.

Runs automatically on database pool startup so any new columns or tables
are added idempotently to existing databases without requiring manual SQL execution.
"""

from __future__ import annotations

import logging
import asyncpg

logger = logging.getLogger("cloudland.migrations")

MIGRATIONS_SQL = """
-- 1. home_settings extra columns for Hero & CTA images and form labels
ALTER TABLE home_settings ADD COLUMN IF NOT EXISTS hero_image_url TEXT;
ALTER TABLE home_settings ADD COLUMN IF NOT EXISTS cta_image_url TEXT;
ALTER TABLE home_settings ADD COLUMN IF NOT EXISTS cta_tab_hi_label VARCHAR(255);
ALTER TABLE home_settings ADD COLUMN IF NOT EXISTS cta_tab_quote_label VARCHAR(255);
ALTER TABLE home_settings ADD COLUMN IF NOT EXISTS cta_submit_label VARCHAR(255);

UPDATE home_settings SET
  cta_tab_hi_label = COALESCE(cta_tab_hi_label, 'ارسال پیام (Say Hi)'),
  cta_tab_quote_label = COALESCE(cta_tab_quote_label, 'درخواست پیش‌فاکتور (Get a Quote)'),
  cta_submit_label = COALESCE(cta_submit_label, 'ارسال پیام (Send Message)')
WHERE id = 1;

-- 2. home_features links
ALTER TABLE home_features ADD COLUMN IF NOT EXISTS link VARCHAR(500);
ALTER TABLE home_features ADD COLUMN IF NOT EXISTS link_label VARCHAR(255);

UPDATE home_features SET
  link = COALESCE(link, '/solutions'),
  link_label = COALESCE(link_label, 'بیشتر بدانید')
WHERE link IS NULL;

-- 3. about_settings CTA eyebrow
ALTER TABLE about_settings ADD COLUMN IF NOT EXISTS cta_eyebrow VARCHAR(255);
UPDATE about_settings SET
  cta_eyebrow = COALESCE(cta_eyebrow, 'همکاری با سرزمین ابری')
WHERE id = 1;

-- 4. about_cta_perks table
CREATE TABLE IF NOT EXISTS about_cta_perks (
  id SERIAL PRIMARY KEY,
  icon VARCHAR(100) NOT NULL DEFAULT 'verified',
  label VARCHAR(255) NOT NULL,
  sort_order INTEGER NOT NULL DEFAULT 0
);

INSERT INTO about_cta_perks (icon, label, sort_order)
SELECT v.icon, v.label, v.sort_order
FROM (VALUES
  ('verified', 'مشاوره تخصصی و تحلیل نیازمندی‌ها', 0),
  ('bolt', 'پاسخگویی سریع کمتر از ۲۴ ساعت', 1),
  ('cloud_done', 'توسعه راهکارهای ابری مقیاس‌پذیر', 2)
) AS v(icon, label, sort_order)
WHERE NOT EXISTS (SELECT 1 FROM about_cta_perks);

-- 5. contact_settings form fields
ALTER TABLE contact_settings ADD COLUMN IF NOT EXISTS form_title VARCHAR(255);
ALTER TABLE contact_settings ADD COLUMN IF NOT EXISTS form_subtitle TEXT;
ALTER TABLE contact_settings ADD COLUMN IF NOT EXISTS form_submit_label VARCHAR(255);

UPDATE contact_settings SET
  form_title = COALESCE(form_title, 'فرم درخواست'),
  form_subtitle = COALESCE(form_subtitle, 'لطفاً اطلاعات زیر را با دقت وارد کنید.'),
  form_submit_label = COALESCE(form_submit_label, 'ارسال درخواست')
WHERE id = 1;

-- 6. catalog_settings empty state & filter labels
ALTER TABLE catalog_settings ADD COLUMN IF NOT EXISTS all_category_label VARCHAR(255);
ALTER TABLE catalog_settings ADD COLUMN IF NOT EXISTS empty_title VARCHAR(255);
ALTER TABLE catalog_settings ADD COLUMN IF NOT EXISTS empty_text TEXT;

UPDATE catalog_settings SET
  all_category_label = COALESCE(all_category_label, 'همه'),
  empty_title = COALESCE(empty_title, 'محصولی یافت نشد'),
  empty_text = COALESCE(empty_text, 'در این دسته‌بندی هنوز محصولی ثبت نشده است.')
WHERE id = 1;

-- 7. solution_settings empty state
ALTER TABLE solution_settings ADD COLUMN IF NOT EXISTS empty_title VARCHAR(255);
ALTER TABLE solution_settings ADD COLUMN IF NOT EXISTS empty_text TEXT;

UPDATE solution_settings SET
  empty_title = COALESCE(empty_title, 'مقاله‌ای منتشر نشده است'),
  empty_text = COALESCE(empty_text, 'به‌زودی راهکارهای تیم CloudLand در این بخش قرار می‌گیرد.')
WHERE id = 1;

-- 8. about_settings rich content fields (statement, metrics, values, milestones)
ALTER TABLE about_settings ADD COLUMN IF NOT EXISTS statement_title VARCHAR(500);
ALTER TABLE about_settings ADD COLUMN IF NOT EXISTS statement_p1 TEXT;
ALTER TABLE about_settings ADD COLUMN IF NOT EXISTS statement_p2 TEXT;
ALTER TABLE about_settings ADD COLUMN IF NOT EXISTS metrics_json TEXT;
ALTER TABLE about_settings ADD COLUMN IF NOT EXISTS values_json TEXT;
ALTER TABLE about_settings ADD COLUMN IF NOT EXISTS milestones_json TEXT;

-- 9. contact_settings rich content fields (phones, address, hours, SLA, faqs)
ALTER TABLE contact_settings ADD COLUMN IF NOT EXISTS phone VARCHAR(255);
ALTER TABLE contact_settings ADD COLUMN IF NOT EXISTS email VARCHAR(255);
ALTER TABLE contact_settings ADD COLUMN IF NOT EXISTS address TEXT;
ALTER TABLE contact_settings ADD COLUMN IF NOT EXISTS working_hours VARCHAR(255);
ALTER TABLE contact_settings ADD COLUMN IF NOT EXISTS emergency_support VARCHAR(255);
ALTER TABLE contact_settings ADD COLUMN IF NOT EXISTS sla_response VARCHAR(255);
ALTER TABLE contact_settings ADD COLUMN IF NOT EXISTS faqs_json TEXT;

-- 10. home_features icon_src and features_json
ALTER TABLE home_features ADD COLUMN IF NOT EXISTS icon_src TEXT;
ALTER TABLE home_features ADD COLUMN IF NOT EXISTS features_json TEXT;

-- 11. home_works metrics_json and tags_json
ALTER TABLE home_works ADD COLUMN IF NOT EXISTS metrics_json TEXT;
ALTER TABLE home_works ADD COLUMN IF NOT EXISTS tags_json TEXT;

-- 12. solution_articles category, read_time, topic, tags
ALTER TABLE solution_articles ADD COLUMN IF NOT EXISTS category VARCHAR(255);
ALTER TABLE solution_articles ADD COLUMN IF NOT EXISTS read_time VARCHAR(100);
ALTER TABLE solution_articles ADD COLUMN IF NOT EXISTS topic VARCHAR(255);
ALTER TABLE solution_articles ADD COLUMN IF NOT EXISTS tags TEXT;

-- 13. products metrics_json, tags_json, badge
ALTER TABLE products ADD COLUMN IF NOT EXISTS metrics_json TEXT;
ALTER TABLE products ADD COLUMN IF NOT EXISTS tags_json TEXT;
ALTER TABLE products ADD COLUMN IF NOT EXISTS badge VARCHAR(255);

-- 14. media_files library table
CREATE TABLE IF NOT EXISTS media_files (
  id            SERIAL PRIMARY KEY,
  filename      VARCHAR(255) NOT NULL,
  original_name VARCHAR(255),
  file_url      TEXT NOT NULL UNIQUE,
  file_type     VARCHAR(50) NOT NULL DEFAULT 'image',
  mimetype      VARCHAR(100),
  file_size     BIGINT NOT NULL DEFAULT 0,
  folder        VARCHAR(100) DEFAULT 'general',
  created_at    TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_media_files_created ON media_files(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_media_files_type ON media_files(file_type);

-- 15. site_settings quick access widget fields & nav_items sync
ALTER TABLE site_settings ADD COLUMN IF NOT EXISTS quick_phone VARCHAR(255);
ALTER TABLE site_settings ADD COLUMN IF NOT EXISTS quick_phone_label VARCHAR(255);
ALTER TABLE site_settings ADD COLUMN IF NOT EXISTS quick_telegram VARCHAR(255);
ALTER TABLE site_settings ADD COLUMN IF NOT EXISTS quick_telegram_label VARCHAR(255);
ALTER TABLE site_settings ADD COLUMN IF NOT EXISTS quick_cta_link VARCHAR(255);
ALTER TABLE site_settings ADD COLUMN IF NOT EXISTS quick_cta_label VARCHAR(255);
ALTER TABLE site_settings ADD COLUMN IF NOT EXISTS quick_whatsapp VARCHAR(255);
ALTER TABLE site_settings ADD COLUMN IF NOT EXISTS quick_is_enabled VARCHAR(10);

UPDATE site_settings SET
  quick_phone = COALESCE(quick_phone, '02188901234'),
  quick_phone_label = COALESCE(quick_phone_label, 'تماس تلفنی مستقیم'),
  quick_telegram = COALESCE(quick_telegram, 'https://t.me'),
  quick_telegram_label = COALESCE(quick_telegram_label, 'پشتیبانی تلگرام'),
  quick_cta_link = COALESCE(quick_cta_link, '/contact'),
  quick_cta_label = COALESCE(quick_cta_label, 'درخواست مشاوره فوری'),
  quick_is_enabled = COALESCE(quick_is_enabled, 'true')
WHERE id = 1;

UPDATE site_nav_items SET label = 'خانه', path = '/', sort_order = 0 WHERE path IN ('/', '/home') OR label = 'صفحه اصلی';
UPDATE site_nav_items SET label = 'خدمات', path = '/services', sort_order = 1 WHERE path IN ('/services', '/solutions') OR label = 'خدمات';
UPDATE site_nav_items SET label = 'پروژه‌ها', path = '/projects', sort_order = 2 WHERE path IN ('/projects', '/products') OR label = 'پروژه‌ها';
UPDATE site_nav_items SET label = 'مقالات', path = '/articles', sort_order = 3 WHERE path IN ('/articles', '/blog', '/#sec-articles') OR label = 'مقالات';
UPDATE site_nav_items SET label = 'درباره ما', path = '/about', sort_order = 4 WHERE path = '/about' OR label = 'درباره ما';
UPDATE site_nav_items SET label = 'تماس با ما', path = '/contact', sort_order = 5 WHERE path = '/contact' OR label = 'تماس با ما';

-- 16. home_settings works_description and articles section settings
ALTER TABLE home_settings ADD COLUMN IF NOT EXISTS works_description TEXT;
ALTER TABLE home_settings ADD COLUMN IF NOT EXISTS articles_badge VARCHAR(255);
ALTER TABLE home_settings ADD COLUMN IF NOT EXISTS articles_title VARCHAR(500);
ALTER TABLE home_settings ADD COLUMN IF NOT EXISTS articles_description TEXT;
"""


async def run_migrations(pool: asyncpg.Pool) -> None:
    """Execute idempotent schema updates on startup."""
    try:
        async with pool.acquire() as connection:
            async with connection.transaction():
                await connection.execute(MIGRATIONS_SQL)
        logger.info("[migrations] Schema migrations applied successfully.")
    except Exception as e:
        logger.warning("[migrations] Migration check encountered an issue: %s", e)
