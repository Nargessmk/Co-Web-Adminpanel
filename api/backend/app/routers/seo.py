"""SEO: `robots.txt` and a sitemap generated from live content.

The frontend is a client-rendered SPA, so every page URL must be listed
explicitly for crawlers — there is no link graph to follow on the server. Both
files are produced here rather than as static files in the frontend image,
because the content is admin-managed in PostgreSQL: a hand-written sitemap
would go stale the moment a product is added or deactivated.

`robots.txt` and `sitemap.xml` are served from their real paths. Previously
neither file existed, and because the SPA history-mode fallback returns
`index.html` for any unmatched path, a request for `/robots.txt` was answered
with `200 text/html` — a crawler asking for a plain-text file was handed the
home page markup instead.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from urllib.parse import quote
from xml.sax.saxutils import escape

from fastapi import APIRouter
from fastapi.responses import PlainTextResponse, Response

from .. import config, db

logger = logging.getLogger("cloudland.seo")

router = APIRouter(tags=["SEO"])

# Public, indexable routes. `/admin*` and the catch-all are deliberately absent.
STATIC_ROUTES = (
    ("/", "1.0", "daily"),
    ("/products", "0.9", "daily"),
    ("/solutions", "0.8", "weekly"),
    ("/about", "0.6", "monthly"),
    ("/contact", "0.5", "monthly"),
)

# A sitemap entry may not exceed 50 000 URLs; the `sitemap:` index is split
# automatically by the protocol past that point.
_MAX_URLS = 50_000


def _site_origin() -> str:
    """Public origin used for absolute sitemap URLs."""
    return getattr(config, "SITE_URL", "") or getattr(config, "S3_PUBLIC_BASE", "")


@router.get("/robots.txt", include_in_schema=False)
async def robots_txt():
    origin = _site_origin()
    lines = [
        "User-agent: *",
        "Allow: /",
        # The admin panel should never be indexed, and it is not in the sitemap.
        "Disallow: /admin",
        "Disallow: /admin/",
    ]
    if origin:
        lines.append(f"Sitemap: {origin.rstrip('/')}/sitemap.xml")
    return PlainTextResponse(
        "\n".join(lines) + "\n",
        headers={"Cache-Control": "public, max-age=86400"},
    )


async def _rows_to_entries(origin: str) -> list[str]:
    """Build `<url>` entries for the static routes plus live content."""
    entries: list[str] = []
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    for path, priority, freq in STATIC_ROUTES:
        entries.append(
            "  <url>\n"
            f"    <loc>{escape(origin.rstrip('/') + path)}</loc>\n"
            f"    <lastmod>{now}</lastmod>\n"
            f"    <changefreq>{freq}</changefreq>\n"
            f"    <priority>{priority}</priority>\n"
            "  </url>"
        )

    # Products and solution articles are the indexable content. `updated_at` is
    # used as lastmod so crawlers do not re-crawl unchanged pages daily.
    try:
        products = await db.fetch(
            "SELECT slug, updated_at FROM products WHERE is_active = TRUE "
            "ORDER BY id ASC LIMIT $1",
            _MAX_URLS,
        )
        solutions = await db.fetch(
            "SELECT slug, updated_at FROM solution_articles WHERE is_active = TRUE "
            "ORDER BY id ASC LIMIT $1",
            _MAX_URLS,
        )
    except Exception:  # noqa: BLE001
        # A database hiccup must not take the sitemap down; the static routes
        # above are still useful, and the next request will try again.
        logger.exception("Sitemap content query failed")
        return entries

    for prefix, rows in (("/products/", products), ("/solutions/", solutions)):
        for row in rows:
            lastmod = row["updated_at"]
            if isinstance(lastmod, datetime):
                lastmod = lastmod.astimezone(timezone.utc).strftime("%Y-%m-%d")
            # Slugs come from the admin and are not guaranteed to be URL-safe —
            # real ones contain spaces and Persian text. An unencoded space makes
            # the <loc> an invalid URL, so the path is percent-encoded.
            slug = quote(row["slug"] or "", safe="")
            loc = escape(origin.rstrip("/") + prefix + slug)
            modified = f"    <lastmod>{lastmod}</lastmod>\n" if lastmod else ""
            entries.append(
                f"  <url>\n    <loc>{loc}</loc>\n{modified}    <priority>0.7</priority>\n  </url>"
            )

    return entries


@router.get("/sitemap.xml", include_in_schema=False)
async def sitemap_xml():
    origin = _site_origin()
    entries = await _rows_to_entries(origin)
    body = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(entries)
        + "\n</urlset>\n"
    )
    return Response(
        content=body,
        media_type="application/xml",
        headers={"Cache-Control": "public, max-age=3600"},
    )
