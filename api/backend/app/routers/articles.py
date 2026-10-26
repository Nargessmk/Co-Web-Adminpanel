"""Articles API: public list/detail + admin CRUD and sync.

Connects to `solution_articles` and supports articles filtering, search,
slug resolution, and Master Editor sync.
"""

from __future__ import annotations

import json
import logging
import re
import time
import unicodedata
from typing import Any, Optional

from fastapi import APIRouter, Depends, Request

from .. import config, db, storage
from ..errors import ApiError
from ..helpers import (
    extract_file,
    page_limit,
    pagination,
    read_body,
    text,
)
from ..responses import failure, success
from ..security import AdminContext, require_admin

logger = logging.getLogger("cloudland.articles")

router = APIRouter(prefix="/api/articles", tags=["Articles"])

DEFAULT_ARTICLES_DATA = [
    {
        "id": 1,
        "title": "چرا پردازش در لبه شبکه (Edge Computing) آینده پلتفرم‌های پرسرعت است؟",
        "slug": "edge-computing-future",
        "excerpt": "تحلیل دقیق معماری توزیع درخواست‌ها در نزدیک‌ترین فاصله جغرافیایی به کاربر و کاهش ۹۰ درصدی تاخیر بارگذاری.",
        "content": """### لزوم حرکت به سمت پردازش در لبه
در دنیای مدرن وب، میلی‌ثانیه‌ها ارزش تجاری تعیین‌کننده‌ای دارند. تاخیر شبکه (Network Latency) نه فقط ناشی از توان سرور، بلکه حاصل فاصله فیزیکی تا دیتاسنتر و مراحل عبور بسته‌ها از گره‌های متعدد مسیریابی است.

#### مزایای اساسی معماری Edge:
۱. **کاهش لتنسی تا زیر ۱۵ میلی‌ثانیه**: انتقال کدهای محاسباتی به گره‌های Anycast در نزدیکی کاربر نهایی.
۲. **کاهش بار سرورهای هسته**: مدیریت ترافیک‌های بازرسی و کش هوشمند لایه‌ای.
۳. **امنیت در لبه**: جلوگیری از حملات DDoS پیش از رسیدن به هسته سامانه.

با بهره‌گیری از پلتفرم لبه کهکشان هوشمند، تمامی فرآیندهای SSR و اعتبارسنجی توکن‌ها در لبه شبکه انجام می‌پذیرد.""",
        "category": "رایانش ابری",
        "read_time": "۵ دقیقه مطالعه",
        "topic": "معماری سیستم",
        "image": "/assets/articles/edge-computing.jpg",
        "date": "۱۵ شهریور ۱۴۰۵",
        "author": {
            "name": "نیما سهرابی",
            "role": "سرپرست زیرساخت ابری",
            "avatar": "/images/home/contact-datacenter.jpg",
        },
        "tags": ["Edge Network", "Anycast", "Latency Optimization"],
        "product_title": "زیرساخت توزیع‌شده CloudLand Edge",
        "product_slug": "cloudland-edge",
        "product_short_description": "پلتفرم ابری لبه شبکه برای اجرای توزیع‌شده سرویس‌ها و کش هوشمند با تضمین تاخیر کمتر از ۱۵ میلی‌ثانیه.",
        "product_image_url": "/Modern 3D Tech Dashboard Illustration(1).png",
    },
    {
        "id": 2,
        "title": "الگوهای ضدپایداری در مهاجرت به میکروسرویس‌ها و روش‌های پیشگیری از آن",
        "slug": "microservices-anti-patterns",
        "excerpt": "بررسی چالش‌های رایج ارتباطات بین سرویسی، شکست متوالی (Cascading Failures) و پیاده‌سازی Circuit Breaker در عمل.",
        "content": """### دام‌های پنهان معماری میکروسرویس
میکروسرویس‌ها مقیاس‌پذیری تیم‌ها را آزاد می‌کنند، اما بدون نظم مهندسی می‌توانند شبکه را به یک کلاف سردرگم از درخواست‌های شکست‌خورده تبدیل نمایند.

#### کلیدی‌ترین الگوهای ضدپایداری:
- **شکست‌های زنجیره‌ای (Cascading Failures)**: زمانی که کندی یک سرویس وابسته، کل صف ارتباطی سرویس‌های بالادست را قفل می‌کند.
- **ارتباطات همزمان بیش‌ازحد (Chatty HTTP Calls)**: جایگزین کردن آن‌ها با رویدادمحوری (Event-Driven) مبتنی بر Kafka.
- **کمبود تایم‌اوت‌های دفاعی**: پیاده‌سازی الگوی Circuit Breaker با کتابخانه‌های مقاوم و مش سرویس mTLS.""",
        "category": "معماری میکروسرویس",
        "read_time": "۸ دقیقه مطالعه",
        "topic": "الگوهای توزیع‌شده",
        "image": "/assets/articles/microservices.jpg",
        "date": "۲۸ مرداد ۱۴۰۵",
        "author": {
            "name": "آرش رادمنش",
            "role": "معمار ارشد سیستم",
            "avatar": "/images/home/contact-programming.jpg",
        },
        "tags": ["Microservices", "Resilience", "Circuit Breaker", "Kafka"],
        "product_title": "سامانه مدیریت یکپارچه کلاستر و میکروسرویس‌ها",
        "product_slug": "cluster-mesh-manager",
        "product_short_description": "پلتفرم جامع پایش وضعیت پادها، مسیربندی هوشمند و تاب‌آوری خودکار سامانه‌های سازمانی ابری.",
        "product_image_url": "/assets/articles/microservices.jpg",
    },
    {
        "id": 3,
        "title": "یکپارچه‌سازی ایمن مدل‌های زبانی بزرگ (LLM) با پایگاه‌داده‌های سازمانی",
        "slug": "enterprise-llm-rag-security",
        "excerpt": "راهنمای عملی پیاده‌سازی الگوهای RAG با حفظ محرمانگی داده‌ها و جلوگیری از درز اطلاعات حساس کاربران.",
        "content": """### RAG سازمانی بدون خطر درز داده
چگونه می‌توان از قدرت هوش مصنوعی مولد بر روی اسناد محرمانه سازمان استفاده کرد بدون اینکه داده‌ها به سرویس‌های ابری عمومی ارسال شوند؟

#### چارچوب معماری RAG ایمن:
۱. **ایزولاسیون کامل دیتابیس برداری**: استقرار Qdrant یا Milvus در شبکه خصوصی VPC.
۲. **مدل‌های بازمتن فشرده**: به‌کارگیری مدل‌های خانواده Llama و Mistral با کوانتیزاسیون ۴ بیتی روی سرورهای محلی GPU.
۳. **کنترل دسترسی مبتنی بر نقش (RBAC)**: فیلتر کردن وکتورهای بازیابی‌شده متناسب با سطح دسترسی کارمند پیش از ارسال به پرامپت نهایی.""",
        "category": "هوش مصنوعی",
        "read_time": "۶ دقیقه مطالعه",
        "topic": "RAG & داده سازمانی",
        "image": "/assets/articles/llm-rag.jpg",
        "date": "۱۰ مرداد ۱۴۰۵",
        "author": {
            "name": "دکتر سارا یزدانی",
            "role": "سرپرست هوش مصنوعی",
            "avatar": "/images/home/hero-corporate.jpg",
        },
        "tags": ["LLM", "RAG", "Vector DB", "Security"],
    },
    {
        "id": 4,
        "title": "معماری امنیت Zero-Trust: عبور از فایروال‌های سنتی به احراز هویت پیوسته",
        "slug": "zero-trust-architecture",
        "excerpt": "چرا مفهوم مرز شبکه (Perimeter) دیگر کارایی ندارد و چگونه هر درخواست را به عنوان یک تهدید بالقوه ایزوله و اعتبارسنجی کنیم.",
        "content": """### اصول سه‌گانه تفکر Zero-Trust
در محیط‌های ابری مدرن، شعار اصلی «هرگز اعتماد نکن، همیشه راستی‌آزمایی کن» است.

#### اجزای اساسی معماری:
- **احراز هویت پیوسته هویت و دستگاه**: استفاده از کلیدهای سخت‌افزاری FIDO2 و گواهی‌های کوتاه مدت X.509.
- **میکروسگمنتیشن شبکه**: ایزولاسیون کامل جریان ترافیک بین پادهای کوبرنتیز با استانداردهای Calico یا Cilium.
- **رمزنگاری در حال انتقال و سکون**: استفاده اجباری از mTLS 1.3 با پروتکل‌های سازمانی.""",
        "category": "امنیت ابری",
        "read_time": "۷ دقیقه مطالعه",
        "topic": "امنیت سازمانی",
        "image": "/images/home/contact-datacenter.jpg",
        "date": "۲۲ تیر ۱۴۰۵",
        "author": {
            "name": "نیما سهرابی",
            "role": "سرپرست زیرساخت ابری",
            "avatar": "/images/home/contact-datacenter.jpg",
        },
        "tags": ["Zero-Trust", "mTLS", "Kubernetes Security"],
    },
    {
        "id": 5,
        "title": "طراحی سیستم دیزاین سازمانی: پلی میان تیم محصول و تیم فرانت‌اند",
        "slug": "design-systems-enterprise",
        "excerpt": "بررسی راهکارهای توسعه کامپوننت‌های دسترسی‌پذیر، توکن‌های دیزاین مقیاس‌پذیر و اتوماسیون تست‌های بصری در Figma و Vue.",
        "content": """### خلق زبان مشترک میان طراحان و مهندسان
سیستم دیزاین فراتر از یک کیت رابط کاربری است؛ این یک دارایی نرم‌افزاری زنده و قابل نسخه‌بندی برای سازمان است.

#### رویکرد کهکشان هوشمند در سیستم‌های دیزاین:
- **دیزاین توکن‌های ساخت‌یافته**: تعریف متغیرهای معنایی (Semantic Tokens) برای رنگ، فاصله‌گذاری و تایپوگرافی.
- **دسترسی‌پذیری طبق WCAG 2.1 AA**: رعایت کنتراست رنگ و پشتیبانی کامل از صفحه‌خوان‌ها و ناوبری کیبورد.
- **مستندسازی خودکار Storybook**: همگام‌سازی کامپوننت‌های کد با کتابخانه‌های Figma.""",
        "category": "دیزاین سیستم",
        "read_time": "۵ دقیقه مطالعه",
        "topic": "طراحی محصول",
        "image": "/Modern 3D Tech Dashboard Illustration(1).png",
        "date": "۵ تیر ۱۴۰۵",
        "author": {
            "name": "مهرداد کیا",
            "role": "مدیر ارشد دیزاین",
            "avatar": "/Modern 3D Tech Dashboard Illustration(1).png",
        },
        "tags": ["Design System", "Design Tokens", "Accessibility"],
    },
    {
        "id": 6,
        "title": "مدیریت ترافیک‌های شدید میلیونی با کلاسترهای بهینه‌سازی‌شده Redis",
        "slug": "high-traffic-redis-clusters",
        "excerpt": "تکنیک‌های عملی شاردینگ، خط لوله درخواست‌ها (Pipelining) و جلوگیری از سناریوی وحشتناک Thundering Herd.",
        "content": """### پایداری حافظه در مواجهه با بار ناگهانی
هنگام برگزاری کمپین‌های بزرگ ملی، هزاران درخواست همزمان برای داده‌های یکسان ایجاد می‌شود.

#### استراتژی‌های جلوگیری از قفل شدن دیتابیس:
۱. **Distributed Mutex**: استفاده از قفل‌های توزیع‌شده Redlock برای جلوگیری از استعلام همزمان صدها درخواست به سمت بانک داده اصلی.
۲. **Probabilistic Early Expiration**: بازتولید داده‌های کش پیش از انقضای قطعی کلید به صورت تصادفی.
۳. **Read Replicas Cluster**: پخش درخواست‌های خواندن در چند نود مجزا با لتنسی زیر ۱ میلی‌ثانیه.""",
        "category": "معماری میکروسرویس",
        "read_time": "۹ دقیقه مطالعه",
        "topic": "کارایی دیتابیس",
        "image": "/images/home/hero-corporate.jpg",
        "date": "۱۸ خرداد ۱۴۰۵",
        "author": {
            "name": "آرش رادمنش",
            "role": "معمار ارشد سیستم",
            "avatar": "/images/home/contact-programming.jpg",
        },
        "tags": ["Redis", "Caching", "High Availability", "Performance"],
    },
]


def _slugify(val: Any) -> str:
    text_val = unicodedata.normalize("NFKD", str(val or "").lower())
    text_val = re.sub(r"[^a-z0-9]+", "-", text_val)
    text_val = re.sub(r"^-+|-+$", "", text_val)
    return text_val[:180] or f"article-{int(time.time() * 1000)}"


def _row_to_article(row: dict[str, Any]) -> dict[str, Any]:
    tags = []
    if row.get("tags"):
        try:
            tags = json.loads(row["tags"]) if isinstance(row["tags"], str) else list(row["tags"])
        except Exception:
            tags = [t.strip() for t in str(row["tags"]).split(",") if t.strip()]

    raw_img = row.get("image_url") or row.get("image")
    img_url = storage.public_url(raw_img) if raw_img else "/assets/articles/edge-computing.jpg"
    author_avatar_raw = row.get("author_image_url")
    author_avatar = storage.public_url(author_avatar_raw) if author_avatar_raw else "/Modern 3D Tech Dashboard Illustration(1).png"

    raw_prod_img = row.get("product_image_url")
    prod_img_url = storage.public_url(raw_prod_img) if raw_prod_img else None

    return {
        "id": row.get("id"),
        "title": row.get("title"),
        "slug": row.get("slug"),
        "summary": row.get("summary") or row.get("excerpt"),
        "excerpt": row.get("summary") or row.get("excerpt"),
        "content": row.get("content"),
        "category": row.get("category") or "رایانش ابری",
        "read_time": row.get("read_time") or "۵ دقیقه مطالعه",
        "readTime": row.get("read_time") or "۵ دقیقه مطالعه",
        "topic": row.get("topic") or "معماری سیستم",
        "image": img_url,
        "image_url": img_url,
        "date": str(row.get("created_at") or "۱۵ شهریور ۱۴۰۵")[:10],
        "created_at": row.get("created_at"),
        "updated_at": row.get("updated_at"),
        "author": {
            "name": row.get("author_name") or "معمار ارشد سیستم",
            "role": row.get("author_role") or "کهکشان هوشمند",
            "avatar": author_avatar,
        },
        "author_id": row.get("author_id"),
        "author_name": row.get("author_name") or "معمار ارشد سیستم",
        "author_role": row.get("author_role") or "کهکشان هوشمند",
        "author_image_url": author_avatar,
        "tags": tags,
        "related_product_id": row.get("related_product_id") or row.get("product_id"),
        "product_id": row.get("product_id") or row.get("related_product_id"),
        "product_title": row.get("product_title"),
        "product_slug": row.get("product_slug"),
        "product_image_url": prod_img_url,
        "product_short_description": row.get("product_short_description"),
        "source_title": row.get("source_title"),
        "source_url": row.get("source_url"),
        "is_active": row.get("is_active", True),
    }


@router.get("")
async def get_articles(request: Request):
    query = request.query_params
    cat = query.get("category")
    q = (query.get("search") or query.get("q") or "").strip().lower()
    page, limit, offset = page_limit(query.get("page"), query.get("limit"), 12, 100)

    try:
        where_clauses = ["a.is_active = true"]
        params: list[Any] = []

        if cat and cat != "همه":
            params.append(cat)
            where_clauses.append(f"a.category = ${len(params)}")

        if q:
            params.append(f"%{q}%")
            where_clauses.append(
                f"(LOWER(a.title) LIKE ${len(params)} OR LOWER(COALESCE(a.summary, '')) LIKE ${len(params)})"
            )

        where_sql = " WHERE " + " AND ".join(where_clauses)
        count_sql = f"SELECT COUNT(*) FROM solution_articles a {where_sql}"
        total = int(await db.fetchval(count_sql, *params) or 0)

        if total > 0:
            params.extend([limit, offset])
            sql = f"""
                SELECT a.*,
                       t.full_name as author_name, t.role as author_role, t.image_url as author_image_url,
                       p.id as product_id, p.title as product_title, p.slug as product_slug,
                       p.image_url as product_image_url, p.short_description as product_short_description
                FROM solution_articles a
                LEFT JOIN team_members t ON a.author_id = t.id
                LEFT JOIN products p ON COALESCE(a.related_product_id, a.product_id) = p.id
                {where_sql}
                ORDER BY a.sort_order ASC, a.created_at DESC, a.id DESC
                LIMIT ${len(params) - 1} OFFSET ${len(params)}
            """
            rows = await db.fetch(sql, *params)
            articles = [_row_to_article(dict(r)) for r in rows]
            return success(data=articles, pagination=pagination(page, limit, total))
    except Exception as exc:
        logger.warning("Query solution_articles failed or table empty (%s), returning defaults", exc)

    # Filter fallback data
    res = list(DEFAULT_ARTICLES_DATA)
    if cat and cat != "همه":
        res = [a for a in res if a["category"] == cat]
    if q:
        res = [a for a in res if q in a["title"].lower() or q in a["excerpt"].lower()]

    paginated = res[offset: offset + limit]
    return success(data=paginated, pagination=pagination(page, limit, len(res)))


@router.get("/{slug_or_id}")
async def get_article_by_slug_or_id(slug_or_id: str):
    try:
        is_id = slug_or_id.isdigit()
        condition = "a.id = $1" if is_id else "a.slug = $1"
        arg = int(slug_or_id) if is_id else slug_or_id

        row = await db.fetchrow(
            f"""
            SELECT a.*,
                   t.full_name as author_name, t.role as author_role, t.image_url as author_image_url,
                   p.id as product_id, p.title as product_title, p.slug as product_slug,
                   p.image_url as product_image_url, p.short_description as product_short_description
            FROM solution_articles a
            LEFT JOIN team_members t ON a.author_id = t.id
            LEFT JOIN products p ON COALESCE(a.related_product_id, a.product_id) = p.id
            WHERE {condition} AND a.is_active = true
            """,
            arg,
        )
        if row:
            return success(data=_row_to_article(dict(row)))
    except Exception as exc:
        logger.warning("Get article by slug warning: %s", exc)

    # Fallback to defaults
    for art in DEFAULT_ARTICLES_DATA:
        if str(art["id"]) == slug_or_id or art.get("slug") == slug_or_id:
            return success(data=art)

    return failure("Article not found", 404)


@router.put("/admin/sync")
async def sync_articles_from_master_editor(
    request: Request,
    _admin: AdminContext = Depends(require_admin),
):
    """Batch-sync articles from the frontend Master Editor."""
    try:
        body, _ = await read_body(request)
        items = body.get("items") or []
        if not items:
            return success(message="No items to sync")

        async with db.pool().acquire() as connection:
            async with connection.transaction():
                for idx, item in enumerate(items):
                    title = text(item.get("title"))
                    if not title:
                        continue
                    slug = _slugify(item.get("slug") or title)
                    summary = text(item.get("excerpt")) or text(item.get("summary"))
                    content = text(item.get("content"))
                    category = text(item.get("category")) or "رایانش ابری"
                    read_time = text(item.get("readTime")) or text(item.get("read_time")) or "۵ دقیقه مطالعه"
                    topic = text(item.get("topic")) or "معماری سیستم"
                    image_url = text(item.get("image")) or text(item.get("image_url"))
                    tags_str = json.dumps(item.get("tags") or [], ensure_ascii=False)

                    await connection.execute(
                        """
                        INSERT INTO solution_articles (title, slug, summary, content, category, read_time, topic, image_url, tags, sort_order, is_active)
                        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, true)
                        ON CONFLICT (slug) DO UPDATE SET
                            title = EXCLUDED.title,
                            summary = EXCLUDED.summary,
                            content = EXCLUDED.content,
                            category = EXCLUDED.category,
                            read_time = EXCLUDED.read_time,
                            topic = EXCLUDED.topic,
                            image_url = EXCLUDED.image_url,
                            tags = EXCLUDED.tags,
                            sort_order = EXCLUDED.sort_order,
                            updated_at = CURRENT_TIMESTAMP
                        """,
                        title,
                        slug,
                        summary,
                        content,
                        category,
                        read_time,
                        topic,
                        image_url,
                        tags_str,
                        idx,
                    )
        return success(message="Articles synced successfully")
    except Exception as exc:
        logger.exception("Sync articles error")
        return failure(f"Failed to sync articles: {exc}", 500)
