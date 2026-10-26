"""Runtime configuration.

Reads every setting from the environment, and also supports a local ``.env``
file next to the backend root (the same file Docker Compose loads through
``env_file``). Values already present in the environment always win.
"""

from __future__ import annotations

import os
from pathlib import Path

# api/backend/  (the package lives in api/backend/app/)
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"
UPLOADS_DIR = BASE_DIR / "uploads"


def _load_dotenv() -> None:
    """Minimal ``python-dotenv`` replacement: KEY=VALUE lines, ``#`` comments."""
    if not ENV_FILE.is_file():
        return

    try:
        raw = ENV_FILE.read_text(encoding="utf-8")
    except OSError:
        return

    for line in raw.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.lower().startswith("export "):
            line = line[7:].strip()
        if "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            continue

        # Keep surrounding quotes, drop them, exactly like dotenv does.
        if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
            value = value[1:-1]

        # Never overwrite a real environment variable (Docker Compose wins).
        os.environ.setdefault(key, value)


_load_dotenv()


def _env(name: str, default: str | None = None) -> str | None:
    value = os.environ.get(name)
    return default if value is None or value == "" else value


def _env_int(name: str, default: int) -> int:
    try:
        return int(float(_env(name, str(default))))
    except (TypeError, ValueError):
        return default


# ---------------------------------------------------------------- server ----
PORT = _env_int("PORT", 3000)
NODE_ENV = _env("NODE_ENV", "development")

# -------------------------------------------------------------- database ----
DB_HOST = _env("DB_HOST", "localhost")
DB_PORT = _env_int("DB_PORT", 5432)
DB_NAME = _env("DB_NAME", "cloudland")
DB_USER = _env("DB_USER", "cloudland_user")
DB_PASSWORD = _env("DB_PASSWORD", "")
DB_POOL_MIN_SIZE = _env_int("DB_POOL_MIN_SIZE", 1)
DB_POOL_MAX_SIZE = _env_int("DB_POOL_MAX_SIZE", 10)

# --------------------------------------------- FastAPI auth microservice ----
MICROSERVICE_AUTH_URL = (_env("MICROSERVICE_AUTH_URL", "http://localhost:4001") or "").rstrip("/")
MICROSERVICE_JWT_SECRET = _env("MICROSERVICE_JWT_SECRET", "")
MICROSERVICE_JWT_ALGORITHM = _env("MICROSERVICE_JWT_ALGORITHM", "HS256")
# Issuer/audience the authentication microservice puts into every token
# (iss: APM_jwt, aud: ailand.ai). PyJWT refuses tokens that carry an `aud`
# claim unless the expected audience is passed to jwt.decode(), so these are
# part of verification, not decoration.
MICROSERVICE_JWT_ISSUER = _env("MICROSERVICE_JWT_ISSUER", "")
MICROSERVICE_JWT_AUDIENCE = _env("MICROSERVICE_JWT_AUDIENCE", "")
# Admin access tokens live 30 minutes. The authentication service issues them
# with this lifetime; the backend re-enforces it here so a longer-lived token
# signed with the same secret is still rejected.
ACCESS_TOKEN_MAX_AGE_MINUTES = _env_int("ACCESS_TOKEN_MAX_AGE_MINUTES", 30)

# ---------------------------------------------------------- FusionAuth ------
FUSIONAUTH_APPLICATION_ID = _env("FUSIONAUTH_APPLICATION_ID")
# Kept for backwards compatibility with the previous FUSIONAUTH_APP_ID typo.
FUSIONAUTH_APP_ID = _env("FUSIONAUTH_APP_ID")
# Local admin fallback credentials for development or standalone mode
ADMIN_USERNAME = _env("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = _env("ADMIN_PASSWORD", "admin")

# ---------------------------------------- Storage microservice (MinIO) ------
STORAGE_SERVICE_URL = (_env("STORAGE_SERVICE_URL", "http://storage:4003") or "").rstrip("/")
STORAGE_BACKEND = (_env("STORAGE_BACKEND", "minio") or "minio").lower()
STORAGE_FALLBACK_LOCAL = (_env("STORAGE_FALLBACK_LOCAL", "true") or "true").lower() == "true"
STORAGE_UPLOAD_TIMEOUT_MS = _env_int("STORAGE_UPLOAD_TIMEOUT_MS", 30000)
S3_PUBLIC_BASE = (_env("S3_PUBLIC_BASE", "https://s3.ailand.ai") or "").rstrip("/")
S3_BUCKET = _env("S3_BUCKET", "cloudland")

# ---------------------------------------------------------- public site URL --
# Absolute origin of the public site. Used for canonical links, OpenGraph URLs
# and the absolute <loc> entries in sitemap.xml — a sitemap must not contain
# relative URLs. Falls back to nothing if unset; the sitemap then emits the
# paths as given, so this should be filled in for production.
SITE_URL = (_env("SITE_URL", "") or "").rstrip("/")

# Uploads are capped per route (megabytes) — mirrors the old multer setup.
MAX_UPLOAD_MB = 50
MAX_SOLUTION_IMAGE_MB = 10
MAX_SITE_IMAGE_MB = 10
MAX_PRODUCT_VIDEO_MB = 100
SIZE_LIMIT_MESSAGE = "حجم تصویر نباید بیشتر از ۱۰ مگابایت باشد"
