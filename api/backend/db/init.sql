-- ============================================
-- CloudLand Backend — PostgreSQL schema
-- Mounted into /docker-entrypoint-initdb.d/
-- (runs automatically on FIRST init of the postgres volume)
-- ============================================

CREATE TABLE IF NOT EXISTS product_categories (
  id          SERIAL PRIMARY KEY,
  name        VARCHAR(255) NOT NULL,
  slug        VARCHAR(255) NOT NULL UNIQUE,
  description TEXT,
  sort_order  INTEGER,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at  TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Categories are reordered by the admin from the products-page filter row
-- (existing rows keep their current id order).
ALTER TABLE product_categories ADD COLUMN IF NOT EXISTS sort_order INTEGER;
UPDATE product_categories SET sort_order = id WHERE sort_order IS NULL;
CREATE INDEX IF NOT EXISTS product_categories_sort_order_idx ON product_categories (sort_order);

CREATE TABLE IF NOT EXISTS products (
  id                SERIAL PRIMARY KEY,
  title             VARCHAR(255) NOT NULL,
  slug              VARCHAR(255) NOT NULL UNIQUE,
  short_description TEXT,
  description       TEXT,
  image_url         TEXT,
  url               TEXT,
  category_id       INTEGER REFERENCES product_categories(id) ON DELETE SET NULL,
  is_featured       BOOLEAN NOT NULL DEFAULT FALSE,
  is_active         BOOLEAN NOT NULL DEFAULT TRUE,
  created_at        TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at        TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS product_catalogs (
  id         SERIAL PRIMARY KEY,
  product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
  title      VARCHAR(255) NOT NULL,
  file_url   TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS product_images (
  id         SERIAL PRIMARY KEY,
  product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
  image_url  TEXT NOT NULL,
  sort_order INTEGER NOT NULL DEFAULT 0,
  created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Product videos (gallery) — was previously only created by a JS migration.
CREATE TABLE IF NOT EXISTS product_videos (
  id            SERIAL PRIMARY KEY,
  product_id    INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
  video_url     TEXT NOT NULL,
  thumbnail_url TEXT,
  sort_order    INTEGER NOT NULL DEFAULT 0,
  title         TEXT,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE product_videos ADD COLUMN IF NOT EXISTS thumbnail_url TEXT;


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

CREATE INDEX IF NOT EXISTS idx_products_category_id  ON products(category_id);
CREATE INDEX IF NOT EXISTS idx_products_is_active    ON products(is_active);
CREATE INDEX IF NOT EXISTS idx_catalogs_product_id   ON product_catalogs(product_id);
CREATE INDEX IF NOT EXISTS idx_product_images_product_id ON product_images(product_id);
CREATE INDEX IF NOT EXISTS idx_product_videos_product_id ON product_videos(product_id);
CREATE INDEX IF NOT EXISTS idx_consultations_status  ON consultations(status);

CREATE TABLE IF NOT EXISTS team_members (
  id           SERIAL PRIMARY KEY,
  full_name    VARCHAR(255) NOT NULL,
  full_name_en VARCHAR(255),
  role         VARCHAR(255) NOT NULL,
  role_en      VARCHAR(255),
  linkedin_url TEXT,
  github_url   TEXT,
  website_url  TEXT,
  resume_en    TEXT,
  resume_fa    TEXT,
  image_url    TEXT,
  sort_order   INTEGER NOT NULL DEFAULT 0,
  is_active    BOOLEAN NOT NULL DEFAULT TRUE,
  created_at   TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at   TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_team_members_sort ON team_members(sort_order);
CREATE INDEX IF NOT EXISTS idx_team_members_active ON team_members(is_active);



-- Résumé layout template. 'classic' is the GitHub-style single column
-- (summary / experience / education / skills) used by every existing member.
ALTER TABLE team_members
  ADD COLUMN IF NOT EXISTS resume_template VARCHAR(32) NOT NULL DEFAULT 'classic';

-- Latin spelling of the name, shown on the English résumé and its PDF while the
-- Persian one keeps `full_name`. Nullable because rows created before this
-- existed have no Latin name yet; the form requires it for new and edited
-- members, and the PDF falls back to `full_name` when it is still empty.
ALTER TABLE team_members
  ADD COLUMN IF NOT EXISTS full_name_en VARCHAR(255);

-- English job title, used by the English résumé in place of `role`. Nullable for
-- the same reason as `full_name_en`; the English PDF falls back to `role` until
-- an English title is filled in.
ALTER TABLE team_members
  ADD COLUMN IF NOT EXISTS role_en VARCHAR(255);

-- Icon shown in the About page whenever the member has no photo (`image_url`).
-- Stores a Material Icons ligature name, e.g. 'code' or 'palette', which the
-- admin picks from the same IconSelect control the other sections use. Nullable:
-- rows created before this column existed have no choice, and the page then
-- falls back to the icon it assigned positionally before, so those members
-- keep looking exactly as they did.
ALTER TABLE team_members
  ADD COLUMN IF NOT EXISTS avatar_icon VARCHAR(64);

-- ============================================
-- Seed data
-- ============================================
INSERT INTO product_categories (name, slug, description) VALUES
  ('Software Development', 'software-development', 'Custom software solutions'),
  ('Cloud Services', 'cloud-services', 'Cloud infrastructure and deployment'),
  ('AI & Machine Learning', 'ai-machine-learning', 'Intelligent automation solutions'),
  ('IT Consulting', 'it-consulting', 'Expert technology consulting')
ON CONFLICT (slug) DO NOTHING;

INSERT INTO products (title, slug, short_description, description, category_id, is_featured, is_active) VALUES
  ('CloudLand ERP Platform', 'cloudland-erp', 'Enterprise resource planning solution for modern businesses', 'A comprehensive ERP system built with cutting-edge technology to streamline your business operations.', 1, true, true),
  ('Smart Analytics Dashboard', 'smart-analytics', 'Real-time business intelligence and reporting', 'Powerful analytics platform that transforms raw data into actionable insights with beautiful visualizations.', 3, true, true),
  ('Cloud Migration Toolkit', 'cloud-migration-toolkit', 'Seamless migration to cloud infrastructure', 'Automated tools and expert guidance for migrating your on-premise infrastructure to the cloud.', 2, true, true),
  ('DevOps Pipeline Manager', 'devops-pipeline', 'Automated CI/CD pipeline management', 'Streamline your development workflow with automated testing, building, and deployment pipelines.', 1, false, true),
  ('AI Customer Support Bot', 'ai-support-bot', 'Intelligent customer service automation', 'Deploy an AI-powered chatbot that handles customer inquiries 24/7 with natural language understanding.', 3, false, true),
  ('Enterprise Security Suite', 'enterprise-security', 'Comprehensive cybersecurity protection', 'End-to-end security solution including threat detection, vulnerability scanning, and compliance reporting.', 4, true, true)
ON CONFLICT (slug) DO NOTHING;

-- ============================================
-- About page content (admin editable)
-- ============================================
CREATE TABLE IF NOT EXISTS about_settings (
  id                  INTEGER PRIMARY KEY,
  hero_badge          VARCHAR(255),
  hero_title          VARCHAR(500),
  hero_title_accent   VARCHAR(100),
  hero_description    TEXT,
  timeline_title      VARCHAR(255),
  team_title          VARCHAR(255),
  team_subtitle       VARCHAR(500),
  cta_icon            VARCHAR(100) DEFAULT 'support_agent',
  cta_title           VARCHAR(255),
  cta_description     TEXT,
  cta_primary_icon    VARCHAR(100) DEFAULT 'mail',
  cta_primary_label   VARCHAR(255),
  cta_primary_link    VARCHAR(500),
  cta_secondary_icon  VARCHAR(100) DEFAULT 'inventory_2',
  cta_secondary_label VARCHAR(255),
  cta_secondary_link  VARCHAR(500),
  updated_at          TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS about_stats (
  id         SERIAL PRIMARY KEY,
  value      VARCHAR(50) NOT NULL,
  label      VARCHAR(255) NOT NULL,
  icon       VARCHAR(100) DEFAULT 'star',
  sort_order INTEGER NOT NULL DEFAULT 0,
  created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS about_mission_cards (
  id           SERIAL PRIMARY KEY,
  title        VARCHAR(255) NOT NULL,
  description  TEXT,
  icon         VARCHAR(100) DEFAULT 'star',
  is_highlight BOOLEAN NOT NULL DEFAULT FALSE,
  sort_order   INTEGER NOT NULL DEFAULT 0,
  created_at   TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at   TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS about_timeline (
  id          SERIAL PRIMARY KEY,
  year        VARCHAR(50) NOT NULL,
  title       VARCHAR(255) NOT NULL,
  description TEXT,
  icon        VARCHAR(100) DEFAULT 'star',
  sort_order  INTEGER NOT NULL DEFAULT 0,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at  TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_about_stats_sort ON about_stats(sort_order);
CREATE INDEX IF NOT EXISTS idx_about_mission_cards_sort ON about_mission_cards(sort_order);
CREATE INDEX IF NOT EXISTS idx_about_timeline_sort ON about_timeline(sort_order);

INSERT INTO about_settings (
  id, hero_badge, hero_title, hero_title_accent, hero_description,
  timeline_title, team_title, team_subtitle,
  cta_icon, cta_title, cta_description,
  cta_primary_icon, cta_primary_label, cta_primary_link,
  cta_secondary_icon, cta_secondary_label, cta_secondary_link
)
SELECT
  1,
  'درباره CloudLand',
  'ما زیرساخت آینده را می‌سازیم',
  'آینده',
  'CloudLand با هدف ارائه راهکارهای نرم‌افزاری پیشرفته و زیرساخت‌های ابری مقیاس‌پذیر تأسیس شده است. ما به کسب‌وکارها کمک می‌کنیم تا با بهره‌گیری از فناوری‌های نوین، عملکرد خود را بهبود بخشند و در بازار رقابتی امروز پیشرو باشند.',
  'مسیر پیشرفت ما',
  'تیم ما',
  'متخصصانی که آینده را می‌سازند',
  'support_agent',
  'آماده همکاری هستید؟',
  'با ما در ارتباط باشید تا بهترین راهکار را برای کسب‌وکار شما پیشنهاد دهیم.',
  'mail',
  'تماس با ما',
  '/contact',
  'inventory_2',
  'مشاهده محصولات',
  '/products'
WHERE NOT EXISTS (SELECT 1 FROM about_settings);

INSERT INTO about_stats (value, label, icon, sort_order)
SELECT * FROM (VALUES
  ('۸۷+', 'پروژه موفق', 'task_alt', 0),
  ('۳۰+', 'مشتری', 'groups', 1),
  ('۱۰+', 'سال تجربه', 'workspace_premium', 2),
  ('۲۴/۷', 'پشتیبانی', 'headset_mic', 3)
) AS seed(value, label, icon, sort_order)
WHERE NOT EXISTS (SELECT 1 FROM about_stats);

INSERT INTO about_mission_cards (title, description, icon, is_highlight, sort_order)
SELECT * FROM (VALUES
  ('مأموریت ما', 'ارائه راهکارهای نرم‌افزاری هوشمند و مقیاس‌پذیر که به کسب‌وکارها امکان رشد سریع، کاهش هزینه‌ها و افزایش بهره‌وری را می‌دهد.', 'emoji_objects', FALSE, 0),
  ('چشم‌انداز ما', 'تبدیل شدن به برترین ارائه‌دهنده زیرساخت‌های ابری و راهکارهای هوش مصنوعی در خاورمیانه تا سال ۱۴۱۰.', 'visibility', TRUE, 1),
  ('ارزش‌های ما', 'نوآوری، کیفیت، شفافیت و تعهد به موفقیت مشتریان. ما باور داریم موفقیت مشتریان، موفقیت ماست.', 'favorite', FALSE, 2)
) AS seed(title, description, icon, is_highlight, sort_order)
WHERE NOT EXISTS (SELECT 1 FROM about_mission_cards);

INSERT INTO about_timeline (year, title, description, icon, sort_order)
SELECT * FROM (VALUES
  ('۱۳۹۶', 'تأسیس شرکت', 'شروع فعالیت با تیمی کوچک از متخصصان نرم‌افزار و شبکه.', 'groups', 0),
  ('۱۳۹۹', 'اولین محصول ابری', 'عرضه اولین سرویس ذخیره‌سازی ابری مقیاس‌پذیر.', 'cloud_upload', 1),
  ('۱۴۰۰', 'گسترش تیم', 'افزایش تیم به ۱۵ نفر و ورود به حوزه هوش مصنوعی.', 'diversity_3', 2),
  ('۱۴۰۱', 'صفحه اول گوگل', 'شناخته شدن به عنوان برترین ارائه‌دهنده راهکارهای ابری.', 'trending_up', 3),
  ('۱۴۰۲', 'بین‌المللی شدن', 'شروع همکاری با شرکت‌های منطقه‌ای و بین‌المللی.', 'public', 4),
  ('۱۴۰۳', 'هوش مصنوعی', 'راه‌اندازی پلتفرم هوش مصنوعی برای خودکارسازی فرآیندها.', 'smart_toy', 5)
) AS seed(year, title, description, icon, sort_order)
WHERE NOT EXISTS (SELECT 1 FROM about_timeline);

-- ============================================
-- Contact page content (admin editable)
-- The request form itself is static and posts to /api/consultations.
-- ============================================
CREATE TABLE IF NOT EXISTS contact_settings (
  id INTEGER PRIMARY KEY,
  hero_badge VARCHAR(255),
  hero_title VARCHAR(500),
  hero_title_accent VARCHAR(100),
  hero_description TEXT,
  aside_title VARCHAR(255),
  aside_description TEXT,
  aside_icon VARCHAR(100) DEFAULT 'support_agent',
  updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS contact_info_cards (
  id SERIAL PRIMARY KEY,
  label VARCHAR(255) NOT NULL,
  value TEXT NOT NULL,
  icon VARCHAR(100) DEFAULT 'info',
  sort_order INTEGER DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS contact_info_cards_sort_order_idx ON contact_info_cards (sort_order);

INSERT INTO contact_settings (
  id, hero_badge, hero_title, hero_title_accent, hero_description,
  aside_title, aside_description, aside_icon
)
SELECT
  1,
  'ارتباط با CloudLand',
  'درخواست مشاوره و دمو',
  'مشاوره و دمو',
  'اطلاعات خود را وارد کنید تا کارشناسان CloudLand در اولین فرصت با شما تماس بگیرند.',
  'در کنار شما هستیم',
  'اگر برای انتخاب محصول، پیاده‌سازی یا توسعه یک راهکار نرم‌افزاری نیاز به مشاوره دارید، با ما در ارتباط باشید.',
  'support_agent'
WHERE NOT EXISTS (SELECT 1 FROM contact_settings);

INSERT INTO contact_info_cards (label, value, icon, sort_order)
SELECT * FROM (VALUES
  ('شماره تماس', 'مهرنیا:09163085306 | سیلاوی:09382990760', 'phone', 0),
  ('ایمیل', 'silawimahdi2002@gmail.com | qermezkon@gmail.com', 'email', 1),
  ('موقعیت', 'ایران، اهواز', 'location_on', 2)
) AS seed(label, value, icon, sort_order)
WHERE NOT EXISTS (SELECT 1 FROM contact_info_cards);

-- ============================================
-- Products page header (admin editable)
-- ============================================
CREATE TABLE IF NOT EXISTS catalog_settings (
  id INTEGER PRIMARY KEY,
  page_badge VARCHAR(255),
  page_title VARCHAR(500),
  page_description TEXT,
  detail_catalogs_title VARCHAR(255),
  detail_videos_title VARCHAR(255),
  detail_gallery_title VARCHAR(255),
  detail_description_title VARCHAR(255),
  detail_related_title VARCHAR(255),
  detail_site_label VARCHAR(255),
  detail_consult_label VARCHAR(255),
  detail_products_label VARCHAR(255),
  updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO catalog_settings (id, page_title, page_description)
SELECT 1, 'کاتالوگ محصولات', 'تمامی نرم‌افزارهای CloudLand را در یک نگاه مشاهده کنید.'
WHERE NOT EXISTS (SELECT 1 FROM catalog_settings);

-- The products page badge and the headings/labels of a product's detail page
-- live in this same row (the detail page has no header of its own), so a
-- database created before them still gets the columns — and the texts the
-- page hard-coded until now, so the admin dialog opens with real values.
ALTER TABLE catalog_settings ADD COLUMN IF NOT EXISTS page_badge VARCHAR(255);
ALTER TABLE catalog_settings ADD COLUMN IF NOT EXISTS detail_catalogs_title VARCHAR(255);
ALTER TABLE catalog_settings ADD COLUMN IF NOT EXISTS detail_videos_title VARCHAR(255);
ALTER TABLE catalog_settings ADD COLUMN IF NOT EXISTS detail_gallery_title VARCHAR(255);
ALTER TABLE catalog_settings ADD COLUMN IF NOT EXISTS detail_description_title VARCHAR(255);
ALTER TABLE catalog_settings ADD COLUMN IF NOT EXISTS detail_related_title VARCHAR(255);
ALTER TABLE catalog_settings ADD COLUMN IF NOT EXISTS detail_site_label VARCHAR(255);
ALTER TABLE catalog_settings ADD COLUMN IF NOT EXISTS detail_consult_label VARCHAR(255);
ALTER TABLE catalog_settings ADD COLUMN IF NOT EXISTS detail_products_label VARCHAR(255);
UPDATE catalog_settings SET
  page_badge            = COALESCE(page_badge, 'محصولات و سامانه‌های ابری'),
  detail_catalogs_title = COALESCE(detail_catalogs_title, 'کاتالوگ‌ها و فایل‌ها'),
  detail_videos_title   = COALESCE(detail_videos_title, 'ویدیوهای محصول'),
  detail_gallery_title  = COALESCE(detail_gallery_title, 'گالری تصاویر'),
  detail_description_title = COALESCE(detail_description_title, 'توضیحات محصول'),
  detail_related_title  = COALESCE(detail_related_title, 'محصولات مرتبط'),
  detail_site_label     = COALESCE(detail_site_label, 'مشاهده سایت'),
  detail_consult_label  = COALESCE(detail_consult_label, 'درخواست مشاوره'),
  detail_products_label = COALESCE(detail_products_label, 'سایر محصولات')
WHERE id = 1;

-- Category seeds above are inserted without sort_order; give them the id order.
UPDATE product_categories SET sort_order = id WHERE sort_order IS NULL;

-- ============================================
-- "راهکارها" — articles written from the admin panel
-- ============================================
CREATE TABLE IF NOT EXISTS solution_articles (
  id                 SERIAL PRIMARY KEY,
  title              VARCHAR(255) NOT NULL,
  slug               VARCHAR(255) NOT NULL UNIQUE,
  summary            TEXT,
  content            TEXT,
  image_url          TEXT,
  source_title       VARCHAR(500),
  source_url         TEXT,
  related_product_id INTEGER REFERENCES products(id) ON DELETE SET NULL,
  author_id          INTEGER REFERENCES team_members(id) ON DELETE SET NULL,
  sort_order         INTEGER NOT NULL DEFAULT 0,
  is_active          BOOLEAN NOT NULL DEFAULT TRUE,
  created_at         TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at         TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_solution_articles_active ON solution_articles(is_active);
CREATE INDEX IF NOT EXISTS idx_solution_articles_sort ON solution_articles(sort_order);
CREATE INDEX IF NOT EXISTS idx_solution_articles_product ON solution_articles(related_product_id);
CREATE INDEX IF NOT EXISTS idx_solution_articles_author ON solution_articles(author_id);

-- ============================================
-- "راهکارها" page header (admin editable)
-- ============================================
CREATE TABLE IF NOT EXISTS solution_settings (
  id               INTEGER PRIMARY KEY,
  page_badge       VARCHAR(255),
  page_title       VARCHAR(500),
  page_description TEXT,
  updated_at       TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO solution_settings (id, page_badge, page_title, page_description)
SELECT
  1,
  'راهکارها',
  'راهکارهای CloudLand',
  'یادداشت‌ها، تحلیل‌ها و راهنمای تخصصی تیم CloudLand درباره نرم‌افزار، زیرساخت ابری و هوش مصنوعی.'
WHERE NOT EXISTS (SELECT 1 FROM solution_settings);

-- An article's detail page has no header of its own: its eyebrow, the labels
-- of its source/related-product/author blocks and its two action buttons are
-- edited in this same row, so an older database still gets the columns (and
-- the texts the detail page hard-coded until now).
ALTER TABLE solution_settings ADD COLUMN IF NOT EXISTS detail_eyebrow VARCHAR(255);
ALTER TABLE solution_settings ADD COLUMN IF NOT EXISTS detail_source_label VARCHAR(255);
ALTER TABLE solution_settings ADD COLUMN IF NOT EXISTS detail_related_label VARCHAR(255);
ALTER TABLE solution_settings ADD COLUMN IF NOT EXISTS detail_author_label VARCHAR(255);
ALTER TABLE solution_settings ADD COLUMN IF NOT EXISTS detail_author_link_label VARCHAR(255);
ALTER TABLE solution_settings ADD COLUMN IF NOT EXISTS detail_others_label VARCHAR(255);
ALTER TABLE solution_settings ADD COLUMN IF NOT EXISTS detail_consult_label VARCHAR(255);
UPDATE solution_settings SET
  detail_eyebrow            = COALESCE(detail_eyebrow, 'راهکارها و مقالات تخصصی'),
  detail_source_label       = COALESCE(detail_source_label, 'منبع'),
  detail_related_label      = COALESCE(detail_related_label, 'محصول مرتبط'),
  detail_author_label       = COALESCE(detail_author_label, 'نویسنده'),
  detail_author_link_label  = COALESCE(detail_author_link_label, 'مشاهده در افراد تیم'),
  detail_others_label       = COALESCE(detail_others_label, 'سایر راهکارها'),
  detail_consult_label      = COALESCE(detail_consult_label, 'درخواست مشاوره')
WHERE id = 1;

-- ============================================
-- Site header + footer (admin editable)
-- ============================================
CREATE TABLE IF NOT EXISTS site_settings (
  id                        INTEGER PRIMARY KEY,
  logo_url                  TEXT,
  site_name                 VARCHAR(255),
  header_login_label        VARCHAR(255),
  header_login_link         VARCHAR(500),
  header_cta_label          VARCHAR(255),
  header_cta_link           VARCHAR(500),
  header_buttons_order      VARCHAR(32),
  footer_description        TEXT,
  footer_products_title     VARCHAR(255),
  footer_all_products_label VARCHAR(255),
  footer_company_title      VARCHAR(255),
  footer_contact_title      VARCHAR(255),
  footer_contact_address    VARCHAR(500),
  footer_contact_phone      VARCHAR(255),
  footer_contact_email      VARCHAR(500),
  footer_cta_label          VARCHAR(255),
  footer_cta_link           VARCHAR(500),
  footer_copyright          VARCHAR(500),
  footer_privacy_label      VARCHAR(255),
  footer_privacy_url        VARCHAR(500),
  footer_terms_label        VARCHAR(255),
  footer_terms_url          VARCHAR(500),
  updated_at                TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- The admin can drag the two header buttons past each other; the order travels
-- as a short 'login,cta' / 'cta,login' list. Existing rows keep the order they
-- are rendered in today.
ALTER TABLE site_settings ADD COLUMN IF NOT EXISTS header_buttons_order VARCHAR(32);
UPDATE site_settings SET header_buttons_order = 'login,cta' WHERE header_buttons_order IS NULL;

INSERT INTO site_settings (
  id, logo_url, site_name,
  header_login_label, header_login_link, header_cta_label, header_cta_link,
  header_buttons_order,
  footer_description, footer_products_title, footer_all_products_label,
  footer_company_title, footer_contact_title, footer_contact_address,
  footer_contact_phone, footer_contact_email, footer_cta_label, footer_cta_link,
  footer_copyright, footer_privacy_label, footer_privacy_url,
  footer_terms_label, footer_terms_url
)
SELECT
  1,
  '/images/cloudland-logo.png',
  'CloudLand',
  'ورود', '/admin/login',
  'درخواست دمو', '/contact',
  'login,cta',
  'راهکارهای نرم‌افزاری هوشمند برای کسب‌وکارهای مدرن. ما به شما کمک می‌کنیم سریع‌تر، هوشمندتر و مطمئن‌تر رشد کنید.',
  'محصولات', 'همه محصولات',
  'شرکت',
  'تماس با ما', 'ایران، اهواز', '۰۶۱۳-۳۳۶۲۷۷۲', 'inform@gmail.com',
  'درخواست مشاوره', '/contact',
  'تمامی حقوق محفوظ است.',
  'حریم خصوصی', '#',
  'شرایط استفاده', '#'
WHERE NOT EXISTS (SELECT 1 FROM site_settings);

CREATE TABLE IF NOT EXISTS site_nav_items (
  id         SERIAL PRIMARY KEY,
  label      VARCHAR(255) NOT NULL,
  path       VARCHAR(500) NOT NULL,
  sort_order INTEGER NOT NULL DEFAULT 0,
  is_active  BOOLEAN NOT NULL DEFAULT TRUE
);

INSERT INTO site_nav_items (label, path, sort_order)
SELECT v.label, v.path, v.sort_order
FROM (VALUES
  ('خانه', '/', 0),
  ('محصولات', '/products', 1),
  ('راهکارها', '/solutions', 2),
  ('درباره ما', '/about', 3),
  ('تماس با ما', '/contact', 4)
) AS v(label, path, sort_order)
WHERE NOT EXISTS (SELECT 1 FROM site_nav_items);

CREATE TABLE IF NOT EXISTS site_footer_links (
  id         SERIAL PRIMARY KEY,
  label      VARCHAR(255) NOT NULL,
  url        VARCHAR(500) NOT NULL,
  sort_order INTEGER NOT NULL DEFAULT 0,
  is_active  BOOLEAN NOT NULL DEFAULT TRUE
);

INSERT INTO site_footer_links (label, url, sort_order)
SELECT v.label, v.url, v.sort_order
FROM (VALUES
  ('خانه', '/', 0),
  ('راهکارها', '/solutions', 1),
  ('درباره ما', '/about', 2),
  ('تماس با ما', '/contact', 3),
  ('وبلاگ', '#', 4)
) AS v(label, url, sort_order)
WHERE NOT EXISTS (SELECT 1 FROM site_footer_links);

CREATE TABLE IF NOT EXISTS site_social_links (
  id         SERIAL PRIMARY KEY,
  label      VARCHAR(255) NOT NULL,
  url        VARCHAR(500) NOT NULL,
  icon       VARCHAR(100) NOT NULL DEFAULT 'link',
  sort_order INTEGER NOT NULL DEFAULT 0,
  is_active  BOOLEAN NOT NULL DEFAULT TRUE
);

INSERT INTO site_social_links (label, url, icon, sort_order)
SELECT v.label, v.url, v.icon, v.sort_order
FROM (VALUES
  ('LinkedIn', '#', 'business', 0),
  ('Instagram', '#', 'photo_camera', 1),
  ('Telegram', '#', 'send', 2)
) AS v(label, url, icon, sort_order)
WHERE NOT EXISTS (SELECT 1 FROM site_social_links);

-- ============================================
-- HOME PAGE (admin editable)
-- ============================================

CREATE TABLE IF NOT EXISTS home_settings (
  id                      INTEGER PRIMARY KEY,
  hero_badge              VARCHAR(255),
  hero_title              VARCHAR(500),
  hero_title_color        VARCHAR(20),
  hero_title_accent       VARCHAR(255),
  hero_description        TEXT,
  hero_primary_label      VARCHAR(255),
  hero_primary_link       VARCHAR(500),
  hero_secondary_label    VARCHAR(255),
  hero_secondary_link     VARCHAR(500),
  hero_scroll_label       VARCHAR(255),
  orbit_caption           VARCHAR(255),
  products_badge          VARCHAR(255),
  products_title          VARCHAR(500),
  products_description    TEXT,
  products_all_label      VARCHAR(255),
  products_empty_title    VARCHAR(255),
  products_empty_text     TEXT,
  why_badge               VARCHAR(255),
  why_title               VARCHAR(500),
  why_title_accent        VARCHAR(255),
  why_description         TEXT,
  customers_badge         VARCHAR(255),
  customers_title         VARCHAR(500),
  customers_title_accent  VARCHAR(255),
  customers_description   TEXT,
  trust_title             VARCHAR(500),
  trust_description       TEXT,
  cta_icon                VARCHAR(100),
  cta_title               VARCHAR(500),
  cta_title_accent        VARCHAR(255),
  cta_description         TEXT,
  cta_primary_label       VARCHAR(255),
  cta_primary_link        VARCHAR(500),
  cta_secondary_label     VARCHAR(255),
  cta_secondary_link      VARCHAR(500),
  works_eyebrow           VARCHAR(255),
  works_title             VARCHAR(500),
  works_all_label         VARCHAR(255),
  works_details_label     VARCHAR(255),
  works_tech_label        VARCHAR(255),
  works_team_label        VARCHAR(255),
  works_cta_label         VARCHAR(255),
  works_category_label    VARCHAR(255),
  works_duration_label    VARCHAR(255),
  reviews_eyebrow         VARCHAR(255),
  reviews_title           VARCHAR(500),
  updated_at              TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO home_settings (
  id,
  hero_badge, hero_title, hero_title_accent, hero_description,
  hero_primary_label, hero_primary_link,
  hero_secondary_label, hero_secondary_link,
  hero_scroll_label,
  orbit_caption,
  products_badge, products_title, products_description,
  products_all_label, products_empty_title, products_empty_text,
  why_badge, why_title, why_title_accent, why_description,
  customers_badge, customers_title, customers_title_accent, customers_description,
  trust_title, trust_description,
  cta_icon, cta_title, cta_title_accent, cta_description,
  cta_primary_label, cta_primary_link,
  cta_secondary_label, cta_secondary_link
)
SELECT
  1,
  'سرزمین ابری',
  'راهکارهای نرم‌افزاری', 'برای کسب‌وکارهای هوشمند',
  'ما در CloudLand با ارائه محصولات نرم‌افزاری پیشرفته، به کسب‌وکارها کمک می‌کنیم تا سریع‌تر رشد کنند، هوشمندتر تصمیم بگیرند و فرآیندهای خود را ساده‌تر مدیریت کنند.',
  'مشاهده محصولات', '/products',
  'درخواست مشاوره', '/contact',
  'مشاهده محصولات',
  'سرزمین ابری',
  'محصولات CloudLand', 'جدیدترین سامانه‌های ما',
  'راهکارهای نرم‌افزاری هوشمند برای ساده‌تر، سریع‌تر و بهتر کردن فرآیندهای کسب‌وکار',
  'مشاهده همه محصولات', 'هنوز محصولی ثبت نشده است',
  'محصولات CloudLand به‌زودی در این بخش نمایش داده می‌شوند.',
  'چرا CloudLand؟', 'زیرساختی مطمئن برای', 'کسب‌وکار شما',
  'با تکیه بر فناوری‌های مدرن، امنیت بالا و معماری مقیاس‌پذیر، راهکارهایی می‌سازیم که همراه رشد کسب‌وکار شما باشند.',
  'اعتماد شما، سرمایه ماست', 'مورد اعتماد', 'کسب‌وکارهای بزرگ',
  'مجموعه‌ای از سازمان‌ها و کسب‌وکارها به راهکارهای نرم‌افزاری CloudLand اعتماد کرده‌اند.',
  'همراه شما در مسیر رشد',
  'ما به ایجاد همکاری‌های بلندمدت و ارائه راهکارهای قابل اعتماد برای کسب‌وکارها متعهد هستیم.',
  'rocket_launch', 'آماده‌اید کسب‌وکارتان را', 'متحول کنید؟',
  'با راهکارهای نرم‌افزاری CloudLand، مسیر تحول دیجیتال کسب‌وکارتان را شروع کنید.',
  'درخواست دمو', '/contact',
  'تماس با ما', '/contact'
WHERE NOT EXISTS (SELECT 1 FROM home_settings);

-- The hero title is a single value again: one box in the admin dialog, with a
-- colour picked from four. hero_title_color is the only addition, so a database
-- created before it still gets the column (and the hero's own navy).
ALTER TABLE home_settings ADD COLUMN IF NOT EXISTS hero_title_color VARCHAR(20);
UPDATE home_settings SET hero_title_color = '#0d1b5e' WHERE hero_title_color IS NULL;

-- The "OUR WORKS" and "نظرات مشتریان" sections are two more editable blocks of
-- the homepage: their headers live in this row, their cards in home_works /
-- home_reviews below. A database created before them still gets the columns
-- (and the texts the sections hard-coded until now).
ALTER TABLE home_settings ADD COLUMN IF NOT EXISTS works_eyebrow VARCHAR(255);
ALTER TABLE home_settings ADD COLUMN IF NOT EXISTS works_title VARCHAR(500);
ALTER TABLE home_settings ADD COLUMN IF NOT EXISTS works_all_label VARCHAR(255);
ALTER TABLE home_settings ADD COLUMN IF NOT EXISTS works_details_label VARCHAR(255);
ALTER TABLE home_settings ADD COLUMN IF NOT EXISTS works_tech_label VARCHAR(255);
ALTER TABLE home_settings ADD COLUMN IF NOT EXISTS works_team_label VARCHAR(255);
ALTER TABLE home_settings ADD COLUMN IF NOT EXISTS works_cta_label VARCHAR(255);
ALTER TABLE home_settings ADD COLUMN IF NOT EXISTS works_category_label VARCHAR(255);
ALTER TABLE home_settings ADD COLUMN IF NOT EXISTS works_duration_label VARCHAR(255);
ALTER TABLE home_settings ADD COLUMN IF NOT EXISTS reviews_eyebrow VARCHAR(255);
ALTER TABLE home_settings ADD COLUMN IF NOT EXISTS reviews_title VARCHAR(500);
UPDATE home_settings SET
  works_eyebrow        = COALESCE(works_eyebrow, 'پروژه‌ها و نمونه‌کارها'),
  works_title          = COALESCE(works_title, 'OUR WORKS'),
  works_all_label      = COALESCE(works_all_label, 'مشاهده همه پروژه‌ها'),
  works_details_label  = COALESCE(works_details_label, 'جزئیات پروژه'),
  works_tech_label     = COALESCE(works_tech_label, 'TECHNOLOGIES USED'),
  works_team_label     = COALESCE(works_team_label, 'TEAM MEMBERS'),
  works_cta_label      = COALESCE(works_cta_label, 'رزرو جلسه و دمو'),
  works_category_label = COALESCE(works_category_label, 'دسته‌بندی'),
  works_duration_label = COALESCE(works_duration_label, 'مدت زمان اجرا'),
  reviews_eyebrow      = COALESCE(reviews_eyebrow, 'نظرات مشتریان و همکاران'),
  reviews_title        = COALESCE(reviews_title, 'تجربه همکاری با سرزمین ابری')
WHERE id = 1;

-- The hero buttons are a list, so the admin can add, remove, reorder them and
-- choose the filled or the outlined look. The hero_*_label columns above are
-- the values this table was seeded from and are kept only for old databases.
CREATE TABLE IF NOT EXISTS home_buttons (
  id         SERIAL PRIMARY KEY,
  label      VARCHAR(255) NOT NULL,
  link       VARCHAR(500),
  variant    VARCHAR(20) NOT NULL DEFAULT 'primary',
  sort_order INTEGER NOT NULL DEFAULT 0
);

INSERT INTO home_buttons (label, link, variant, sort_order)
SELECT part.label, part.link, part.variant, part.sort_order
FROM home_settings s
CROSS JOIN LATERAL (VALUES
  (COALESCE(NULLIF(s.hero_primary_label, ''), 'مشاهده محصولات'), s.hero_primary_link, 'primary', 0),
  (COALESCE(NULLIF(s.hero_secondary_label, ''), 'درخواست مشاوره'), s.hero_secondary_link, 'secondary', 1)
) AS part(label, link, variant, sort_order)
WHERE s.id = 1 AND NOT EXISTS (SELECT 1 FROM home_buttons);

CREATE TABLE IF NOT EXISTS home_orbit_items (
  id         SERIAL PRIMARY KEY,
  ring       VARCHAR(10) NOT NULL DEFAULT 'inner',
  label      VARCHAR(255) NOT NULL,
  icon       VARCHAR(100) NOT NULL,
  color      VARCHAR(20) NOT NULL DEFAULT '#1A2472',
  sort_order INTEGER NOT NULL DEFAULT 0
);

INSERT INTO home_orbit_items (ring, label, icon, color, sort_order)
SELECT v.ring, v.label, v.icon, v.color, v.sort_order
FROM (VALUES
  ('inner', 'امنیت', 'shield', '#1A2472', 0),
  ('inner', 'داده', 'storage', '#f5a300', 1),
  ('inner', 'ابر', 'cloud', '#1A2472', 2),
  ('inner', 'هوش مصنوعی', 'psychology', '#f5a300', 3),
  ('outer', 'کد', 'code', '#f5a300', 0),
  ('outer', 'تحلیل', 'analytics', '#1A2472', 1),
  ('outer', 'سرور', 'dns', '#f5a300', 2),
  ('outer', 'اتوماسیون', 'auto_awesome', '#1A2472', 3)
) AS v(ring, label, icon, color, sort_order)
WHERE NOT EXISTS (SELECT 1 FROM home_orbit_items);

CREATE TABLE IF NOT EXISTS home_features (
  id          SERIAL PRIMARY KEY,
  title       VARCHAR(255) NOT NULL,
  description TEXT,
  icon        VARCHAR(100) NOT NULL,
  color       VARCHAR(20) NOT NULL DEFAULT 'navy',
  sort_order  INTEGER NOT NULL DEFAULT 0
);

INSERT INTO home_features (title, description, icon, color, sort_order)
SELECT v.title, v.description, v.icon, v.color, v.sort_order
FROM (VALUES
  ('امنیت بالا',
   'حفاظت از اطلاعات و زیرساخت‌های شما با استانداردهای امنیتی مدرن.',
   'shield', 'navy', 0),
  ('قابلیت اطمینان',
   'زیرساخت پایدار و قابل اعتماد برای سرویس‌هایی که همیشه در دسترس هستند.',
   'verified', 'orange', 1),
  ('پشتیبانی حرفه‌ای',
   'تیم متخصص CloudLand همیشه در کنار شماست تا سریع و دقیق پاسخگو باشد.',
   'support_agent', 'navy', 2),
  ('توسعه‌پذیری',
   'معماری انعطاف‌پذیر برای رشد و توسعه راهکارها متناسب با نیاز شما.',
   'trending_up', 'orange', 3)
) AS v(title, description, icon, color, sort_order)
WHERE NOT EXISTS (SELECT 1 FROM home_features);

CREATE TABLE IF NOT EXISTS home_customers (
  id         SERIAL PRIMARY KEY,
  name       VARCHAR(255) NOT NULL,
  logo       VARCHAR(255) NOT NULL,
  logo_url   TEXT,
  sort_order INTEGER NOT NULL DEFAULT 0
);

INSERT INTO home_customers (name, logo, sort_order)
SELECT v.name, v.logo, v.sort_order
FROM (VALUES
  ('دیجی‌کالا', 'DIGIKALA', 0),
  ('همراه اول', 'MCI', 1),
  ('اسنپ', 'SNAPP', 2),
  ('تپسی', 'TAPSI', 3),
  ('بیمه ایران', 'IRAN', 4),
  ('پارک علم و فناوری', 'STP', 5)
) AS v(name, logo, sort_order)
WHERE NOT EXISTS (SELECT 1 FROM home_customers);

-- Each statistic travels with the number it belongs to (see 012_home_stats)
CREATE TABLE IF NOT EXISTS home_stats (
  id         SERIAL PRIMARY KEY,
  scope      VARCHAR(10)  NOT NULL,
  key        VARCHAR(20)  NOT NULL,
  label      VARCHAR(255) NOT NULL,
  sort_order INTEGER      NOT NULL DEFAULT 0
);

INSERT INTO home_stats (scope, key, label, sort_order)
SELECT v.scope, v.key, v.label, v.sort_order
FROM (VALUES
  ('hero', 'products', 'محصول فعال', 0),
  ('hero', 'customers', 'مشتری فعال', 1),
  ('hero', 'uptime', 'آپتایم', 2),
  ('why', 'products', 'محصول فعال', 0),
  ('why', 'customers', 'مشتری فعال', 1),
  ('why', 'uptime', 'آپتایم', 2),
  ('why', 'support', 'پشتیبانی', 3)
) AS v(scope, key, label, sort_order)
WHERE NOT EXISTS (SELECT 1 FROM home_stats);

-- ============================================
-- Homepage "OUR WORKS" showcase cards (admin editable)
--
-- The visual on the right of a card is one of the two built-in mockups
-- (`mockup` = phones / browser) unless the admin uploads a screenshot
-- (`image_url`), which is what the card then shows.
-- ============================================
CREATE TABLE IF NOT EXISTS home_works (
  id            SERIAL PRIMARY KEY,
  badge         VARCHAR(255) NOT NULL,
  badge_icon    VARCHAR(100) NOT NULL DEFAULT 'star',
  details_link  VARCHAR(500),
  meta_category VARCHAR(255),
  meta_duration VARCHAR(255),
  description   TEXT,
  tech          TEXT,
  team          VARCHAR(500),
  team_more     VARCHAR(50),
  cta_label     VARCHAR(255),
  cta_link      VARCHAR(500),
  image_url     TEXT,
  mockup        VARCHAR(20) NOT NULL DEFAULT 'phones',
  sort_order    INTEGER NOT NULL DEFAULT 0
);

INSERT INTO home_works (
  badge, badge_icon, details_link, meta_category, meta_duration,
  description, tech, team, team_more, cta_label, cta_link, mockup, sort_order
)
SELECT v.badge, v.badge_icon, v.details_link, v.meta_category, v.meta_duration,
       v.description, v.tech, v.team, v.team_more, v.cta_label, v.cta_link,
       v.mockup, v.sort_order
FROM (VALUES
  ('FITNESS APP', 'star', '/products/cloudland-bi',
   'توسعه اپلیکیشن موبایل', '۴ ماه',
   'سامانه جامع و هوشمند سلامت و پایش تناسب اندام با برنامه‌ریزی خودکار تمرینات ورزشی، رژیم غذایی هوش مصنوعی و پردازش بلادرنگ شاخص‌های زیستی کاربران.',
   'React Native, Firebase, Redux, REST API, PostgreSQL',
   'SA,MR,EM,FK', '+۳',
   'رزرو جلسه و دمو', '/contact', 'phones', 0),
  ('E-COMMERCE ENTERPRISE', 'storefront', '/products/cloudland-bpms',
   'پلتفرم ابری سازمانی', '۵ ماه',
   'سامانه چندفروشندگی و تجارت الکترونیک B2B با موتور پردازش سریع فاکتور، یکپارچه‌ساز انبارداری توزیع‌شده، گیت‌وی پرداخت بانکی مقیاس‌پذیر و داشبورد تحلیل رفتار مشتریان.',
   'Vue 3, FastAPI, Docker & K8s, Redis Cache, PostgreSQL',
   'AS,ND,KH,BM', '+۴',
   'درخواست دمو آنلاین', '/contact', 'browser', 1)
) AS v(badge, badge_icon, details_link, meta_category, meta_duration,
       description, tech, team, team_more, cta_label, cta_link, mockup, sort_order)
WHERE NOT EXISTS (SELECT 1 FROM home_works);

-- ============================================
-- Homepage client/partner testimonials (admin editable)
-- ============================================
CREATE TABLE IF NOT EXISTS home_reviews (
  id         SERIAL PRIMARY KEY,
  name       VARCHAR(255) NOT NULL,
  role       VARCHAR(255),
  initials   VARCHAR(10),
  text       TEXT NOT NULL,
  sort_order INTEGER NOT NULL DEFAULT 0
);

INSERT INTO home_reviews (name, role, initials, text, sort_order)
SELECT v.name, v.role, v.initials, v.text, v.sort_order
FROM (VALUES
  ('مهندس آرش شریفی', 'مدیر ارشد فناوری (CTO) در نکست‌ژن', 'آش',
   'همکاری با تیم کلودلند یکی از بهترین تجربیات مهندسی سازمان ما بود. آن‌ها با درک دقیق دغدغه‌های پرتراکنش ما، معماری ابری قدرتمند و پایداری را پیاده کردند که فراتر از استانداردهای معمول بود.', 0),
  ('دکتر علیرضا باقری', 'مدیرعامل هلدینگ رادمان تکنولوژی', 'عب',
   'تعهد کاری، سرعت اجرای بالا و طراحی رابط کاربری بسیار لوکس و مدرن باعث شد پلتفرم جدید ما تحسین همه سرمایه‌گذاران و مشتریان را برانگیزد. پشتیبانی ۲۴ ساعته آن‌ها واقعاً قوت قلب ماست.', 1),
  ('سارا مهدی‌پور', 'مدیر محصول ارشد سامانه‌های مالی', 'سم',
   'دقت در جزییات UI/UX و هماهنگی فوق‌العاده با تیم بک‌اند، فرآیند اجرای پروژه را بدون کمترین تأخیر پیش برد. به هر شرکتی که به دنبال کار درجه‌یک سازمانی است توصیه می‌کنم.', 2),
  ('کامران یزدانی', 'معمار نرم‌افزار و زیرساخت', 'کی',
   'امنیت داده و رعایت استانداردهای Zero-Trust در راهکارهای ابری کلودلند در بالاترین سطح ممکن قرار دارد. تجربه‌ای کاملاً متمایز نسبت به سایر پیمانکاران.', 3)
) AS v(name, role, initials, text, sort_order)
WHERE NOT EXISTS (SELECT 1 FROM home_reviews);

-- ============================================================
-- 014 — store the object key, not the full URL
--
-- Uploaded files used to be written to the database as the complete public
-- URL (https://s3.ailand.ai/cloudland/products/abc.png). That froze the host
-- into every row: moving the bucket to another domain would have broken every
-- image on the site. The database now keeps only the part after the bucket
-- (products/abc.png) and the API builds the URL from S3_PUBLIC_BASE on the way
-- out, so a new host is a one-line change in the environment.
--
-- The rewrite is idempotent: it only touches values that still start with a
-- scheme, so running it again does nothing. Only URLs whose path really has a
-- host, the bucket and an object are rewritten, which leaves the logo that
-- lives in the frontend (/images/cloudland-logo.png) and any link an admin
-- typed by hand exactly as it is.
-- ============================================================

UPDATE products          SET image_url      = substring(image_url  FROM '^https?://[^/]+/[^/]+/(.+)$') WHERE image_url  ~ '^https?://[^/]+/[^/]+/.+$';
UPDATE product_images    SET image_url      = substring(image_url  FROM '^https?://[^/]+/[^/]+/(.+)$') WHERE image_url  ~ '^https?://[^/]+/[^/]+/.+$';
UPDATE product_videos    SET video_url      = substring(video_url  FROM '^https?://[^/]+/[^/]+/(.+)$') WHERE video_url  ~ '^https?://[^/]+/[^/]+/.+$';
UPDATE product_catalogs  SET file_url       = substring(file_url   FROM '^https?://[^/]+/[^/]+/(.+)$') WHERE file_url   ~ '^https?://[^/]+/[^/]+/.+$';
UPDATE team_members      SET image_url      = substring(image_url  FROM '^https?://[^/]+/[^/]+/(.+)$') WHERE image_url  ~ '^https?://[^/]+/[^/]+/.+$';
UPDATE solution_articles SET image_url      = substring(image_url  FROM '^https?://[^/]+/[^/]+/(.+)$') WHERE image_url  ~ '^https?://[^/]+/[^/]+/.+$';
UPDATE site_settings     SET logo_url       = substring(logo_url   FROM '^https?://[^/]+/[^/]+/(.+)$') WHERE logo_url   ~ '^https?://[^/]+/[^/]+/.+$';

-- ============================================================
-- 015 — 100% Admin CMS coverage for all sections
-- ============================================================
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

ALTER TABLE home_features ADD COLUMN IF NOT EXISTS link VARCHAR(500);
ALTER TABLE home_features ADD COLUMN IF NOT EXISTS link_label VARCHAR(255);
UPDATE home_features SET
  link = COALESCE(link, '/solutions'),
  link_label = COALESCE(link_label, 'بیشتر بدانید')
WHERE link IS NULL;

ALTER TABLE about_settings ADD COLUMN IF NOT EXISTS cta_eyebrow VARCHAR(255);
UPDATE about_settings SET
  cta_eyebrow = COALESCE(cta_eyebrow, 'همکاری با سرزمین ابری')
WHERE id = 1;

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

ALTER TABLE contact_settings ADD COLUMN IF NOT EXISTS form_title VARCHAR(255);
ALTER TABLE contact_settings ADD COLUMN IF NOT EXISTS form_subtitle TEXT;
ALTER TABLE contact_settings ADD COLUMN IF NOT EXISTS form_submit_label VARCHAR(255);
UPDATE contact_settings SET
  form_title = COALESCE(form_title, 'فرم درخواست'),
  form_subtitle = COALESCE(form_subtitle, 'لطفاً اطلاعات زیر را با دقت وارد کنید.'),
  form_submit_label = COALESCE(form_submit_label, 'ارسال درخواست')
WHERE id = 1;

ALTER TABLE catalog_settings ADD COLUMN IF NOT EXISTS all_category_label VARCHAR(255);
ALTER TABLE catalog_settings ADD COLUMN IF NOT EXISTS empty_title VARCHAR(255);
ALTER TABLE catalog_settings ADD COLUMN IF NOT EXISTS empty_text TEXT;
UPDATE catalog_settings SET
  all_category_label = COALESCE(all_category_label, 'همه'),
  empty_title = COALESCE(empty_title, 'محصولی یافت نشد'),
  empty_text = COALESCE(empty_text, 'در این دسته‌بندی هنوز محصولی ثبت نشده است.')
WHERE id = 1;

ALTER TABLE solution_settings ADD COLUMN IF NOT EXISTS empty_title VARCHAR(255);
ALTER TABLE solution_settings ADD COLUMN IF NOT EXISTS empty_text TEXT;
UPDATE solution_settings SET
  empty_title = COALESCE(empty_title, 'مقاله‌ای منتشر نشده است'),
  empty_text = COALESCE(empty_text, 'به‌زودی راهکارهای تیم CloudLand در این بخش قرار می‌گیرد.')
WHERE id = 1;

