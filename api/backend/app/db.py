"""Database access layer with automatic PostgreSQL -> SQLite fallback.

Provides seamless local persistence when PostgreSQL is not running or unreachable,
while automatically using PostgreSQL when configured and available.
"""

from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
import json
import logging
from pathlib import Path
import re
import sqlite3
import threading
from typing import Any, Optional, Sequence

import asyncpg

from . import config

logger = logging.getLogger("cloudland.db")

_pool: Optional[asyncpg.Pool] = None
_sqlite_pool: Optional[SqlitePool] = None
_mode: str = "uninitialized"  # "postgres" | "sqlite"


class SqliteRecord(dict):
    """Drop-in mapping matching asyncpg.Record behavior."""

    def __init__(self, mapping: dict[str, Any], tuple_vals: tuple = ()):
        super().__init__(mapping)
        self._tuple = tuple_vals or tuple(mapping.values())

    def __getitem__(self, key: Any) -> Any:
        if isinstance(key, int):
            return self._tuple[key]
        return super().__getitem__(key)

    def get(self, key: str, default: Any = None) -> Any:
        return super().get(key, default)


def _translate_query(query: str, args: tuple[Any, ...]) -> tuple[str, list[Any]]:
    """Translate PostgreSQL parameter syntax ($1, $2) and idioms to SQLite."""
    q = query
    # $1, $2 -> ?1, ?2
    q = re.sub(r"\$(\d+)", r"?\1", q)
    # ILIKE -> LIKE
    q = re.sub(r"\bILIKE\b", "LIKE", q, flags=re.IGNORECASE)
    # NOW() -> CURRENT_TIMESTAMP
    q = re.sub(r"\bNOW\(\)", "CURRENT_TIMESTAMP", q, flags=re.IGNORECASE)

    processed_args = []
    for a in args:
        if isinstance(a, bool):
            processed_args.append(1 if a else 0)
        elif isinstance(a, (dict, list)):
            processed_args.append(json.dumps(a, ensure_ascii=False))
        else:
            processed_args.append(a)

    return q, processed_args


class SqliteTransaction:
    """Async context manager mirroring asyncpg's connection.transaction()."""

    def __init__(self, conn: sqlite3.Connection, lock: threading.Lock):
        self.conn = conn
        self.lock = lock

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        with self.lock:
            if exc_type is not None:
                self.conn.rollback()
            else:
                self.conn.commit()


class SqliteConnection:
    """Async connection wrapper for sqlite3 matching asyncpg.Connection."""

    def __init__(self, conn: sqlite3.Connection, lock: threading.Lock):
        self._conn = conn
        self._lock = lock

    def transaction(self) -> SqliteTransaction:
        return SqliteTransaction(self._conn, self._lock)

    async def fetch(self, query: str, *args: Any) -> list[SqliteRecord]:
        return await asyncio.to_thread(self._sync_fetch, query, args)

    async def fetchrow(self, query: str, *args: Any) -> Optional[SqliteRecord]:
        return await asyncio.to_thread(self._sync_fetchrow, query, args)

    async def fetchval(self, query: str, *args: Any) -> Any:
        return await asyncio.to_thread(self._sync_fetchval, query, args)

    async def execute(self, query: str, *args: Any) -> str:
        return await asyncio.to_thread(self._sync_execute, query, args)

    async def executemany(self, query: str, args: Sequence[Sequence[Any]]) -> None:
        return await asyncio.to_thread(self._sync_executemany, query, args)

    def _sync_fetch(self, query: str, args: tuple[Any, ...]) -> list[SqliteRecord]:
        with self._lock:
            q, p_args = _translate_query(query, args)
            cur = self._conn.cursor()
            cur.execute(q, p_args)
            rows = cur.fetchall()
            return [SqliteRecord(dict(r), tuple(r)) for r in rows]

    def _sync_fetchrow(self, query: str, args: tuple[Any, ...]) -> Optional[SqliteRecord]:
        with self._lock:
            q, p_args = _translate_query(query, args)
            cur = self._conn.cursor()
            cur.execute(q, p_args)
            row = cur.fetchone()
            if "RETURNING" in q.upper():
                self._conn.commit()
            if not row:
                return None
            return SqliteRecord(dict(row), tuple(row))

    def _sync_fetchval(self, query: str, args: tuple[Any, ...]) -> Any:
        with self._lock:
            q, p_args = _translate_query(query, args)
            cur = self._conn.cursor()
            cur.execute(q, p_args)
            row = cur.fetchone()
            if "RETURNING" in q.upper():
                self._conn.commit()
            if not row:
                return None
            return row[0]

    def _sync_execute(self, query: str, args: tuple[Any, ...]) -> str:
        with self._lock:
            q, p_args = _translate_query(query, args)
            cur = self._conn.cursor()
            cur.execute(q, p_args)
            self._conn.commit()
            return f"EXECUTE {cur.rowcount}"

    def _sync_executemany(self, query: str, args: Sequence[Sequence[Any]]) -> None:
        with self._lock:
            if not args:
                return
            q, _ = _translate_query(query, ())
            processed_list = []
            for row_args in args:
                processed_list.append([
                    1 if isinstance(a, bool) else (json.dumps(a, ensure_ascii=False) if isinstance(a, (dict, list)) else a)
                    for a in row_args
                ])
            cur = self._conn.cursor()
            cur.executemany(q, processed_list)
            self._conn.commit()


class SqlitePool:
    """Async pool wrapper matching asyncpg.Pool."""

    def __init__(self, db_path: Path):
        self._db_path = db_path
        self._lock = threading.Lock()
        self._conn = sqlite3.connect(str(db_path), check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        # Enable WAL mode and foreign keys for performance and integrity
        self._conn.execute("PRAGMA journal_mode=WAL;")
        self._conn.execute("PRAGMA foreign_keys=ON;")
        self._connection = SqliteConnection(self._conn, self._lock)

    @asynccontextmanager
    async def acquire(self):
        yield self._connection

    async def fetch(self, query: str, *args: Any) -> list[SqliteRecord]:
        return await self._connection.fetch(query, *args)

    async def fetchrow(self, query: str, *args: Any) -> Optional[SqliteRecord]:
        return await self._connection.fetchrow(query, *args)

    async def fetchval(self, query: str, *args: Any) -> Any:
        return await self._connection.fetchval(query, *args)

    async def execute(self, query: str, *args: Any) -> str:
        return await self._connection.execute(query, *args)

    async def executemany(self, query: str, args: Sequence[Sequence[Any]]) -> None:
        return await self._connection.executemany(query, args)

    def close(self):
        with self._lock:
            self._conn.close()


SQLITE_SCHEMA = """
CREATE TABLE IF NOT EXISTS product_categories (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  name        TEXT NOT NULL,
  slug        TEXT NOT NULL UNIQUE,
  description TEXT,
  sort_order  INTEGER,
  created_at  TEXT DEFAULT CURRENT_TIMESTAMP,
  updated_at  TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS products (
  id                INTEGER PRIMARY KEY AUTOINCREMENT,
  title             TEXT NOT NULL,
  slug              TEXT NOT NULL UNIQUE,
  short_description TEXT,
  description       TEXT,
  image_url         TEXT,
  url               TEXT,
  category_id       INTEGER REFERENCES product_categories(id) ON DELETE SET NULL,
  badge             TEXT,
  metrics_json      TEXT,
  tags_json         TEXT,
  is_featured       INTEGER NOT NULL DEFAULT 0,
  is_active         INTEGER NOT NULL DEFAULT 1,
  created_at        TEXT DEFAULT CURRENT_TIMESTAMP,
  updated_at        TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS product_catalogs (
  id         INTEGER PRIMARY KEY AUTOINCREMENT,
  product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
  title      TEXT NOT NULL,
  file_url   TEXT,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS product_images (
  id         INTEGER PRIMARY KEY AUTOINCREMENT,
  product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
  image_url  TEXT NOT NULL,
  sort_order INTEGER NOT NULL DEFAULT 0,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS product_videos (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  product_id    INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
  video_url     TEXT NOT NULL,
  thumbnail_url TEXT,
  sort_order    INTEGER NOT NULL DEFAULT 0,
  title         TEXT,
  created_at    TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS consultations (
  id           INTEGER PRIMARY KEY AUTOINCREMENT,
  full_name    TEXT NOT NULL,
  phone        TEXT NOT NULL,
  email        TEXT,
  company_name TEXT,
  subject      TEXT NOT NULL,
  message      TEXT,
  status       TEXT NOT NULL DEFAULT 'new',
  created_at   TEXT DEFAULT CURRENT_TIMESTAMP,
  updated_at   TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS team_members (
  id           INTEGER PRIMARY KEY AUTOINCREMENT,
  full_name    TEXT NOT NULL,
  full_name_en TEXT,
  role         TEXT NOT NULL,
  role_en      TEXT,
  linkedin_url TEXT,
  github_url   TEXT,
  website_url  TEXT,
  resume_en    TEXT,
  resume_fa    TEXT,
  image_url    TEXT,
  sort_order   INTEGER NOT NULL DEFAULT 0,
  is_active    INTEGER NOT NULL DEFAULT 1,
  resume_template TEXT DEFAULT 'classic',
  avatar_icon  TEXT,
  created_at   TEXT DEFAULT CURRENT_TIMESTAMP,
  updated_at   TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS solution_articles (
  id           INTEGER PRIMARY KEY AUTOINCREMENT,
  title        TEXT NOT NULL,
  slug         TEXT NOT NULL UNIQUE,
  summary      TEXT,
  content      TEXT,
  image_url    TEXT,
  author_id    INTEGER REFERENCES team_members(id) ON DELETE SET NULL,
  related_product_id INTEGER REFERENCES products(id) ON DELETE SET NULL,
  product_id   INTEGER REFERENCES products(id) ON DELETE SET NULL,
  sort_order   INTEGER NOT NULL DEFAULT 0,
  source_title TEXT,
  source_url   TEXT,
  category     TEXT,
  read_time    TEXT,
  topic        TEXT,
  tags         TEXT,
  is_active    INTEGER NOT NULL DEFAULT 1,
  created_at   TEXT DEFAULT CURRENT_TIMESTAMP,
  updated_at   TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS site_settings (
  id           INTEGER PRIMARY KEY,
  site_name    TEXT DEFAULT 'کهکشان هوشمند',
  tagline      TEXT,
  logo_url     TEXT,
  favicon_url  TEXT,
  footer_text  TEXT,
  meta_title   TEXT,
  meta_description TEXT,
  meta_keywords TEXT,
  updated_at   TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS home_settings (
  id           INTEGER PRIMARY KEY,
  hero_badge   TEXT,
  hero_title   TEXT,
  hero_description TEXT,
  hero_title_color TEXT,
  hero_image_url TEXT,
  cta_title    TEXT,
  cta_description TEXT,
  cta_image_url TEXT,
  cta_tab_hi_label TEXT,
  cta_tab_quote_label TEXT,
  cta_submit_label TEXT,
  updated_at   TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS home_features (
  id           INTEGER PRIMARY KEY AUTOINCREMENT,
  title        TEXT,
  description  TEXT,
  icon         TEXT,
  icon_src     TEXT,
  color        TEXT,
  link         TEXT,
  link_label   TEXT,
  features_json TEXT,
  sort_order   INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS home_works (
  id           INTEGER PRIMARY KEY AUTOINCREMENT,
  title        TEXT,
  category     TEXT,
  description  TEXT,
  metrics_json TEXT,
  tags_json    TEXT,
  mockup       TEXT,
  badge_icon   TEXT,
  image_url    TEXT,
  sort_order   INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS home_buttons (
  id           INTEGER PRIMARY KEY AUTOINCREMENT,
  label        TEXT,
  link         TEXT,
  variant      TEXT,
  sort_order   INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS home_orbit_items (
  id           INTEGER PRIMARY KEY AUTOINCREMENT,
  ring         TEXT,
  label        TEXT,
  icon         TEXT,
  color        TEXT,
  sort_order   INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS home_customers (
  id           INTEGER PRIMARY KEY AUTOINCREMENT,
  name         TEXT,
  logo_url     TEXT,
  sort_order   INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS home_stats (
  id           INTEGER PRIMARY KEY AUTOINCREMENT,
  scope        TEXT,
  key          TEXT,
  label        TEXT,
  sort_order   INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS home_reviews (
  id           INTEGER PRIMARY KEY AUTOINCREMENT,
  author       TEXT,
  role         TEXT,
  company      TEXT,
  quote        TEXT,
  avatar_url   TEXT,
  rating       INTEGER,
  sort_order   INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS about_settings (
  id           INTEGER PRIMARY KEY,
  hero_badge   TEXT,
  hero_title   TEXT,
  hero_description TEXT,
  statement_title TEXT,
  statement_p1 TEXT,
  statement_p2 TEXT,
  metrics_json TEXT,
  values_json  TEXT,
  milestones_json TEXT,
  cta_title    TEXT,
  cta_description TEXT,
  cta_eyebrow  TEXT,
  updated_at   TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS about_stats (
  id           INTEGER PRIMARY KEY AUTOINCREMENT,
  number       TEXT,
  label        TEXT,
  icon         TEXT,
  sort_order   INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS about_mission_cards (
  id           INTEGER PRIMARY KEY AUTOINCREMENT,
  title        TEXT,
  description  TEXT,
  icon         TEXT,
  is_highlight INTEGER DEFAULT 0,
  sort_order   INTEGER DEFAULT 0,
  updated_at   TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS about_timeline (
  id           INTEGER PRIMARY KEY AUTOINCREMENT,
  year         TEXT,
  title        TEXT,
  description  TEXT,
  sort_order   INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS about_cta_perks (
  id           INTEGER PRIMARY KEY AUTOINCREMENT,
  icon         TEXT NOT NULL DEFAULT 'verified',
  label        TEXT NOT NULL,
  sort_order   INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS contact_settings (
  id           INTEGER PRIMARY KEY,
  hero_badge   TEXT,
  hero_title   TEXT,
  hero_description TEXT,
  phone        TEXT,
  email        TEXT,
  address      TEXT,
  working_hours TEXT,
  emergency_support TEXT,
  sla_response TEXT,
  faqs_json    TEXT,
  form_title   TEXT,
  form_subtitle TEXT,
  form_submit_label TEXT,
  updated_at   TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS contact_info_cards (
  id           INTEGER PRIMARY KEY AUTOINCREMENT,
  type         TEXT,
  title        TEXT,
  value        TEXT,
  icon         TEXT,
  link         TEXT,
  sort_order   INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS catalog_settings (
  id           INTEGER PRIMARY KEY,
  page_badge   TEXT,
  page_title   TEXT,
  page_description TEXT,
  all_category_label TEXT,
  empty_title  TEXT,
  empty_text   TEXT,
  detail_catalogs_title TEXT,
  detail_videos_title TEXT,
  detail_gallery_title TEXT,
  detail_description_title TEXT,
  detail_related_title TEXT,
  detail_site_label TEXT,
  detail_consult_label TEXT,
  detail_products_label TEXT,
  updated_at   TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS solution_settings (
  id           INTEGER PRIMARY KEY,
  page_badge   TEXT,
  page_title   TEXT,
  page_description TEXT,
  empty_title  TEXT,
  empty_text   TEXT,
  detail_eyebrow TEXT,
  detail_source_label TEXT,
  detail_related_label TEXT,
  detail_author_label TEXT,
  detail_author_link_label TEXT,
  detail_others_label TEXT,
  detail_consult_label TEXT,
  updated_at   TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS site_nav_items (
  id           INTEGER PRIMARY KEY AUTOINCREMENT,
  label        TEXT,
  link         TEXT,
  sort_order   INTEGER DEFAULT 0,
  is_active    INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS site_footer_links (
  id           INTEGER PRIMARY KEY AUTOINCREMENT,
  section      TEXT,
  label        TEXT,
  link         TEXT,
  sort_order   INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS site_social_links (
  id           INTEGER PRIMARY KEY AUTOINCREMENT,
  platform     TEXT,
  url          TEXT,
  icon         TEXT,
  sort_order   INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS media_files (
  id           INTEGER PRIMARY KEY AUTOINCREMENT,
  filename     TEXT NOT NULL,
  original_name TEXT,
  file_url     TEXT NOT NULL UNIQUE,
  file_type    TEXT NOT NULL DEFAULT 'image',
  mimetype     TEXT,
  file_size    INTEGER NOT NULL DEFAULT 0,
  folder       TEXT DEFAULT 'general',
  created_at   TEXT DEFAULT CURRENT_TIMESTAMP
);
"""


def _seed_sqlite(pool: SqlitePool) -> None:
    """Populate default initial rows if tables are empty."""
    with pool._lock:
        cur = pool._conn.cursor()
        # Ensure column exists if table was previously created
        for col_stmt in [
            "ALTER TABLE solution_articles ADD COLUMN related_product_id INTEGER REFERENCES products(id) ON DELETE SET NULL;",
            "ALTER TABLE solution_articles ADD COLUMN sort_order INTEGER NOT NULL DEFAULT 0;",
            "ALTER TABLE solution_articles ADD COLUMN category TEXT;",
            "ALTER TABLE solution_articles ADD COLUMN read_time TEXT;",
            "ALTER TABLE solution_articles ADD COLUMN topic TEXT;",
            "ALTER TABLE solution_articles ADD COLUMN tags TEXT;",
            "ALTER TABLE products ADD COLUMN badge TEXT;",
            "ALTER TABLE products ADD COLUMN metrics_json TEXT;",
            "ALTER TABLE products ADD COLUMN tags_json TEXT;",
        ]:
            try:
                cur.execute(col_stmt)
            except Exception:
                pass

        # Categories
        cur.execute("SELECT COUNT(*) FROM product_categories")
        if cur.fetchone()[0] == 0:
            cur.executemany(
                "INSERT INTO product_categories (id, name, slug, description, sort_order) VALUES (?, ?, ?, ?, ?)",
                [
                    (1, "توسعه نرم‌افزار و سامانه‌ها", "software-development", "طراحی و توسعه سیستم‌های توزیع‌شده و اپلیکیشن‌های مقیاس‌پذیر", 1),
                    (2, "زیرساخت ابری و DevOps", "cloud-services", "مدیریت کلاسترها، کوبرنتیز و خطوط استقرار مداوم CI/CD", 2),
                    (3, "هوش مصنوعی و کلان‌داده", "ai-machine-learning", "مدل‌های یادگیری ماشین، پردازش زبان طبیعی و خطوط انتقال داده بلادرنگ", 3),
                    (4, "امنیت سازمانی و شبکه", "security-network", "ایزولاسیون Zero-Trust، آزمون‌های نفوذ و معماری امنیت دفاع در عمق", 4),
                ],
            )

        # Products
        cur.execute("SELECT COUNT(*) FROM products")
        if cur.fetchone()[0] == 0:
            cur.executemany(
                "INSERT INTO products (id, title, slug, short_description, description, category_id, is_featured, is_active) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                [
                    (1, "سامانه یکپارچه ERP سازمانی کهکشان هوشمند", "cloudland-erp", "پلتفرم مدیریت منابع سازمانی با مقیاس‌پذیری بالا و پردازش داده‌های بلادرنگ.", "<p>سامانه جامع سازمانی با معماری ماژولار، یکپارچگی پایگاه‌های داده و گزارش‌گیری تحلیلی.</p>", 1, 1, 1),
                    (2, "داشبورد هوش تجاری و تحلیل کلان‌داده", "smart-analytics", "مانیتورینگ و مصورسازی هوشمند داده‌های بلادرنگ در لبه شبکه با هوش مصنوعی.", "<p>داشبورد تعاملی مانیتورینگ عملکرد، پیش‌بینی رفتار کاربران و تحلیل بلادرنگ شاخص‌ها.</p>", 3, 1, 1),
                    (3, "درگاه امنیتی توزیع‌شده Zero-Trust Edge Gateway", "edge-gateway", "سرویس مش پرسرعت با محافظت چندسطحی، رمزنگاری mTLS و لتنسی زیر ۱۵ میلی‌ثانیه.", "<p>زیرساخت لبه با قابلیت فایروال لایه ۷، توزیع بار هوشمند و ایزولاسیون پردازش.</p>", 2, 1, 1),
                ],
            )

        # Team Members
        cur.execute("SELECT COUNT(*) FROM team_members")
        if cur.fetchone()[0] == 0:
            cur.executemany(
                "INSERT INTO team_members (id, full_name, full_name_en, role, role_en, sort_order, is_active, resume_template, avatar_icon) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                [
                    (1, "مهندس سینا مرادی", "Sina Moradi", "معمار ارشد سیستم و راهبر فنی", "Chief System Architect", 1, 1, "classic", "memory"),
                    (2, "مهندس پویان سرمدی", "Pouyan Sarmadi", "مدیر ارشد زیرساخت ابری و دوآپس", "Head of Cloud Infrastructure", 2, 1, "classic", "dns"),
                    (3, "دکتر سارا یزدانی", "Dr. Sara Yazdani", "سرپرست تیم هوش مصنوعی و داده", "Head of AI & Data", 3, 1, "classic", "psychology"),
                    (4, "مهندس مهرداد کیا", "Mehrdad Kia", "مدیر ارشد طراحی محصول و تجربه کاربری", "Head of Product Design", 4, 1, "classic", "palette"),
                ],
            )

        # Solution Articles
        cur.execute("SELECT COUNT(*) FROM solution_articles")
        if cur.fetchone()[0] == 0:
            cur.executemany(
                "INSERT INTO solution_articles (id, title, slug, summary, content, category, read_time, topic, is_active) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                [
                    (
                        1,
                        "معماری میکروسرویس‌های مقیاس‌پذیر در ابعاد ملی",
                        "distributed-microservices-architecture",
                        "بررسی استراتژی‌های تجزیه سیستم‌های یکپارچه و پیاده‌سازی الگوهای Event-Driven",
                        "<p>طراحی سیستم‌های توزیع‌شده با پایداری ۹۹.۹۹۹٪ مستلزم رعایت دقیق ایزولاسیون خطا و تفکیک دیتابیس‌هاست.</p>",
                        "معماری نرم‌افزار",
                        "۷ دقیقه",
                        "سیستم‌های توزیع‌شده",
                        1,
                    ),
                    (
                        2,
                        "استقرار معماری امنیت Zero-Trust در زیرساخت‌های ابری",
                        "zero-trust-cloud-security",
                        "اصول احراز هویت مستمر، کنترل دسترسی جزئی‌نگر و رمزنگاری سراسری mTLS",
                        "<p>در معماری Zero-Trust، هیچ درخواستی صرف قرارگیری در شبکه داخلی مورد اعتماد قرار نمی‌گیرد.</p>",
                        "امنیت ابری",
                        "۵ دقیقه",
                        "امنیت شبکه",
                        1,
                    ),
                ],
            )

        # Consultations
        cur.execute("SELECT COUNT(*) FROM consultations")
        if cur.fetchone()[0] == 0:
            cur.executemany(
                "INSERT INTO consultations (id, full_name, phone, email, company_name, subject, message, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                [
                    (1, "مهندس علیرضا رضایی", "09121112233", "rezaei@company.ir", "شرکت داده‌پردازان", "مشاوره زیرساخت ابری", "درخواست بررسی و بهینه‌سازی کلاستر کوبرنتیز سازمانی", "new"),
                    (2, "مریم حسینی", "09351234567", "hosseini@startup.io", "استارتاپ هوش‌یار", "طراحی خطوط انتقال داده", "مشاوره در زمینه پردازش داده‌های کلان و مدل‌های یادگیری عمیق", "contacted"),
                ],
            )

        # Singleton settings
        cur.execute("INSERT OR IGNORE INTO site_settings (id, site_name, tagline, footer_text) VALUES (1, 'کهکشان هوشمند', 'مهندسی سیستم‌های مدرن و زیرساخت‌های ابری', 'کلیه حقوق محفوظ است © کهکشان هوشمند')")
        cur.execute("INSERT OR IGNORE INTO home_settings (id, hero_badge, hero_title, hero_description, hero_title_color, hero_image_url) VALUES (1, 'سامانه مهندسی نرم‌افزار و رایانش ابری', 'معماری سیستم‌های مدرن، رایانش ابری و هوش مصنوعی سازمانی', 'ارائه راهکارهای مقیاس‌پذیر سازمانی با پایداری ۹۹.۹۹۹٪ و لتنسی میلی‌ثانیه‌ای.', '#1A2472', '/images/herosection-video.mp4')")
        cur.execute("INSERT OR IGNORE INTO about_settings (id, hero_badge, hero_title, hero_description, statement_title) VALUES (1, 'درباره کهکشان هوشمند', 'اصالت مهندسی، انضباط سازمانی', 'ما یک استودیوی پیشرو در معماری نرم‌افزارهای تجاری و زیرساخت‌های ابری هستیم.', 'پیشگام در مهندسی سیستم‌های توزیع‌شده با قابلیت اتکای سازمانی')")
        cur.execute("INSERT OR IGNORE INTO contact_settings (id, hero_badge, hero_title, hero_description, phone, email, address, working_hours, emergency_support, sla_response) VALUES (1, 'ارتباط با ما', 'گفت‌وگو درباره پروژه بعدی شما', 'تیم مشاوره و مهندسی کهکشان هوشمند آماده پاسخگویی به پرسش‌های فنی و سازمانی شماست.', '۰۲۱-۸۸۸۸۹۹۹۹', 'info@cloudland.ir', 'تهران، پارک فناوری پردیس، مجتمع کهکشان هوشمند', 'شنبه تا چهارشنبه ۸:۰۰ الی ۱۷:۰۰', 'پشتیبانی اضطراری ۲۴/۷ برای پروژه‌های سازمانی', 'پاسخگویی سریع کمتر از ۲ ساعت کاری')")
        # Alter table migrations for catalog_settings and solution_settings
        for col in ["page_badge", "page_title", "page_description", "all_category_label", "empty_title", "empty_text", "detail_catalogs_title", "detail_videos_title", "detail_gallery_title", "detail_description_title", "detail_related_title", "detail_site_label", "detail_consult_label", "detail_products_label"]:
            try:
                cur.execute(f"ALTER TABLE catalog_settings ADD COLUMN {col} TEXT;")
            except Exception:
                pass

        for col in ["page_badge", "page_title", "page_description", "empty_title", "empty_text", "detail_eyebrow", "detail_source_label", "detail_related_label", "detail_author_label", "detail_author_link_label", "detail_others_label", "detail_consult_label"]:
            try:
                cur.execute(f"ALTER TABLE solution_settings ADD COLUMN {col} TEXT;")
            except Exception:
                pass

        for col in ["works_description", "articles_badge", "articles_title", "articles_description"]:
            try:
                cur.execute(f"ALTER TABLE home_settings ADD COLUMN {col} TEXT;")
            except Exception:
                pass

        cur.execute("INSERT OR IGNORE INTO catalog_settings (id, page_badge, page_title, page_description) VALUES (1, 'سبد محصولات و پروژه‌ها', 'پروژه‌های شاخص و پلتفرم‌های ابری', 'بررسی معماری سیستم‌های ملی و تجاری با پایداری ۹۹.۹۹۹٪.')")
        cur.execute("INSERT OR IGNORE INTO solution_settings (id, page_badge, page_title, page_description) VALUES (1, 'راهکارها و خدمات تخصصی', 'معماری سیستم‌های مدرن و هوش مصنوعی سازمانی', 'ارائه خدمات مهندسی نرم‌افزار و زیرساخت‌های توزیع‌شده.')")

        pool._conn.commit()


async def init_pool() -> Any:
    """Create the connection pool. Connects to PostgreSQL if reachable, or activates local SQLite fallback."""
    global _pool, _sqlite_pool, _mode

    # 1. Try PostgreSQL if configured
    try:
        _pool = await asyncpg.create_pool(
            host=config.DB_HOST,
            port=config.DB_PORT,
            database=config.DB_NAME,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            min_size=config.DB_POOL_MIN_SIZE,
            max_size=config.DB_POOL_MAX_SIZE,
            command_timeout=5,
        )
        await _pool.fetchval("SELECT 1")
        from .migrations import run_migrations
        await run_migrations(_pool)
        _mode = "postgres"
        logger.info("Connected to PostgreSQL successfully.")
        return _pool
    except Exception as exc:
        _pool = None
        logger.warning("PostgreSQL unavailable (%s). Activating local SQLite database fallback.", exc)

    # 2. Activate SQLite fallback
    db_file = config.BASE_DIR / "cloudland_local.db"
    _sqlite_pool = SqlitePool(db_file)
    with _sqlite_pool._lock:
        _sqlite_pool._conn.executescript(SQLITE_SCHEMA)
    _seed_sqlite(_sqlite_pool)
    _mode = "sqlite"
    logger.info("Local SQLite database initialized at %s", db_file)
    return _sqlite_pool


async def close_pool() -> None:
    global _pool, _sqlite_pool, _mode
    if _pool is not None:
        await _pool.close()
        _pool = None
    if _sqlite_pool is not None:
        _sqlite_pool.close()
        _sqlite_pool = None
    _mode = "uninitialized"


def pool() -> Any:
    """Return the active database pool (PostgreSQL or SQLite adapter)."""
    global _sqlite_pool, _mode
    if _mode == "postgres" and _pool is not None:
        return _pool
    if _mode == "sqlite" and _sqlite_pool is not None:
        return _sqlite_pool
    # If uninitialized, initialize SQLite on demand
    db_file = config.BASE_DIR / "cloudland_local.db"
    _sqlite_pool = SqlitePool(db_file)
    with _sqlite_pool._lock:
        _sqlite_pool._conn.executescript(SQLITE_SCHEMA)
    _seed_sqlite(_sqlite_pool)
    _mode = "sqlite"
    return _sqlite_pool


async def fetch(query: str, *args: Any) -> list[Any]:
    return await pool().fetch(query, *args)


async def fetchrow(query: str, *args: Any) -> Optional[Any]:
    return await pool().fetchrow(query, *args)


async def fetchval(query: str, *args: Any) -> Any:
    return await pool().fetchval(query, *args)


async def execute(query: str, *args: Any) -> str:
    return await pool().execute(query, *args)


async def executemany(query: str, args: Sequence[Sequence[Any]]) -> None:
    await pool().executemany(query, args)


__all__ = [
    "init_pool",
    "close_pool",
    "pool",
    "fetch",
    "fetchrow",
    "fetchval",
    "execute",
    "executemany",
]
