#!/usr/bin/env bash
# ============================================================
# CloudLand — Database & tables setup script
#
# Creates (idempotently — safe to re-run):
#   1. the app role           (default: cloudland_user)
#   2. the database           (default: cloudland)
#   3. an optional schema     (--schema cloudland, default: public)
#   4. all project tables     from init.sql (products, categories,
#                             catalogs, consultations + seed data)
#
# NOTE: to bring an ALREADY RUNNING database up to date after a `git pull`
#       that changed the schema, use ./migrate.sh instead. init.sql only runs
#       on the FIRST init of the postgres volume, so pulling new columns does
#       not reach an existing database.
#
# Usage — LOCAL (postgres in Docker, container cloudland-postgres):
#
#     ./setup_cloudland_db.sh --docker
#
# Usage — REMOTE / REAL SERVER (psql must be installed):
#
#     DB_HOST=db.example.com DB_PORT=5432 \
#     DB_ADMIN_USER=postgres DB_ADMIN_PASSWORD='admin-secret' \
#     APP_PASSWORD='app-secret' \
#     ./setup_cloudland_db.sh
#
#     (DB_ADMIN_* = server admin credentials, used ONLY to create
#      the role/database. APP_PASSWORD = password for the
#      cloudland_user application role. If omitted, a random one
#      is generated and printed once.)
#
# Optional flags:
#     --schema NAME   create tables inside schema NAME instead of
#                     public (e.g. --schema cloudland). The role's
#                     search_path is set automatically so the app
#                     needs no changes.
#     --skip-seed     skip the demo/seed data inserts
# ============================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INIT_SQL="$SCRIPT_DIR/init.sql"

# ---------- configuration (env vars override defaults) ----------
DB_NAME="${DB_NAME:-cloudland}"
DB_SCHEMA="${DB_SCHEMA:-public}"
DB_HOST="${DB_HOST:-127.0.0.1}"
DB_PORT="${DB_PORT:-5432}"
DB_ADMIN_USER="${DB_ADMIN_USER:-}"
DB_ADMIN_PASSWORD="${DB_ADMIN_PASSWORD:-}"
APP_USER="${APP_USER:-cloudland_user}"
APP_PASSWORD="${APP_PASSWORD:-}"
SKIP_SEED=0
DOCKER=0

# ---------- flags ----------
while [[ $# -gt 0 ]]; do
  case "$1" in
    --docker)    DOCKER=1 ;;
    --schema)    DB_SCHEMA="$2"; shift ;;
    --skip-seed) SKIP_SEED=1 ;;
    -h|--help)   grep '^#' "$0" | head -44; exit 0 ;;
    *) echo "Unknown option: $1 (see --help)"; exit 1 ;;
  esac
  shift
done

[[ -f "$INIT_SQL" ]] || { echo "ERROR: $INIT_SQL not found"; exit 1; }
[[ "$DB_SCHEMA" =~ ^[a-z_][a-z0-9_]*$ ]] || { echo "ERROR: invalid schema name '$DB_SCHEMA'"; exit 1; }

# ---------- psql helpers ----------
# Connect as admin creds (if given) for setup steps, else as the app user.
SETUP_USER="${DB_ADMIN_USER:-$APP_USER}"
SETUP_PASSWORD="${DB_ADMIN_PASSWORD:-$APP_PASSWORD}"
PGOPTIONS_DEFAULT="-c search_path=${DB_SCHEMA},public"

psql_as() {  # psql_as <user> <password> <database> [psql args...]
  local user="$1" pass="$2" db="$3"; shift 3
  if [[ $DOCKER -eq 1 ]]; then
    docker exec -i -e PGPASSWORD="$pass" -e PGOPTIONS="$PGOPTIONS_DEFAULT" \
      cloudland-postgres psql -U "$user" -d "$db" -v ON_ERROR_STOP=1 "$@"
  else
    PGPASSWORD="$pass" PGOPTIONS="$PGOPTIONS_DEFAULT" \
      psql -h "$DB_HOST" -p "$DB_PORT" -U "$user" -d "$db" -v ON_ERROR_STOP=1 "$@"
  fi
}

sql_scalar() {  # run a query, return a single scalar value
  psql_as "$SETUP_USER" "$SETUP_PASSWORD" "$1" -qAt -c "$2"
}

# Safe SQL quoting (psql does NOT interpolate :variables inside -c strings)
qident() { local s="${1//\"/\"\"}"; printf '"%s"' "$s"; }   # identifier
qlit()  { local s="${1//\'/\'\'}"; printf "'%s'" "$s"; }    # string literal

echo "=============================================="
echo " CloudLand DB setup"
echo "   host/container : $([[ $DOCKER -eq 1 ]] && echo 'docker:cloudland-postgres' || echo "$DB_HOST:$DB_PORT")"
echo "   database       : $DB_NAME"
echo "   schema         : $DB_SCHEMA"
echo "   app user       : $APP_USER"
echo "=============================================="

# ---------- 0. connectivity check ----------
if ! sql_scalar postgres "SELECT 1" >/dev/null 2>&1; then
  echo "ERROR: cannot connect to PostgreSQL (check host/port/credentials)"
  exit 1
fi
echo "[1/6] PostgreSQL connection: OK"

# ---------- 1. app role ----------
if [[ $DOCKER -eq 0 && -z "$APP_PASSWORD" ]]; then
  APP_PASSWORD="$(openssl rand -hex 16)"
  echo "      (generated APP_PASSWORD: $APP_PASSWORD)"
  echo "       -> save it! It goes into DB_PASSWORD in the project .env"
fi
ROLE_EXISTS="$(sql_scalar postgres "SELECT 1 FROM pg_roles WHERE rolname='$APP_USER'")"
if [[ "$ROLE_EXISTS" == "1" ]]; then
  echo "[2/6] Role '$APP_USER' already exists"
else
  psql_as "$SETUP_USER" "$SETUP_PASSWORD" postgres \
    -qAt -c "CREATE ROLE $(qident "$APP_USER") LOGIN PASSWORD $(qlit "$APP_PASSWORD");"
  echo "[2/6] Role '$APP_USER' created"
fi

# ---------- 2. database ----------
DB_EXISTS="$(sql_scalar postgres "SELECT 1 FROM pg_database WHERE datname='$DB_NAME'")"
if [[ "$DB_EXISTS" == "1" ]]; then
  echo "[3/6] Database '$DB_NAME' already exists"
else
  psql_as "$SETUP_USER" "$SETUP_PASSWORD" postgres \
    -qAt -c "CREATE DATABASE $(qident "$DB_NAME") OWNER $(qident "$APP_USER");"
  echo "[3/6] Database '$DB_NAME' created (owner: $APP_USER)"
fi

# ---------- 3. schema (if not public) ----------
if [[ "$DB_SCHEMA" != "public" ]]; then
  psql_as "$SETUP_USER" "$SETUP_PASSWORD" "$DB_NAME" \
    -qAt -c "CREATE SCHEMA IF NOT EXISTS $(qident "$DB_SCHEMA") AUTHORIZATION $(qident "$APP_USER");" \
    -c "ALTER ROLE $APP_USER IN DATABASE $DB_NAME SET search_path TO $DB_SCHEMA, public;"
  echo "[4/6] Schema '$DB_SCHEMA' created; search_path set for '$APP_USER'"
else
  echo "[4/6] Using default 'public' schema (what the backend expects)"
fi

# ---------- 4. tables ----------
echo "[5/6] Applying schema from init.sql (idempotent, existing objects are skipped)..."

# Split init.sql into schema and seed by STATEMENT, not by line position.
#
# The previous implementation was `sed '/-- Seed data/,$d'`, which assumed
# everything after the first "-- Seed data" comment was seed data. That is not
# the case: the file interleaves DDL and seed data (the site_settings and
# home_settings ALTER TABLE ... ADD COLUMN statements sit well after that
# comment), so the truncation silently dropped 19 of 26 CREATE TABLEs, 8 of 17
# indexes and 2 of 6 column migrations. Re-running setup on an existing database
# therefore never applied those changes.
#
# `strip_seed_sql` removes only INSERT ... ; blocks, so every CREATE TABLE,
# CREATE INDEX and ALTER TABLE is kept and applied idempotently.
strip_seed_sql() {
  awk '
    BEGIN { in_insert = 0 }
    /^[ \t]*INSERT[ \t]+INTO/ { in_insert = 1 }
    {
      if (in_insert) {
        # A multi-line VALUES list ends at the first line closing the statement.
        if ($0 ~ /;[ \t]*$/) in_insert = 0
        next
      }
      print
    }
  ' "$1"
}

strip_seed_sql "$INIT_SQL" | psql_as "$APP_USER" "$APP_PASSWORD" "$DB_NAME" -q -f -
echo "      Schema applied."
if [[ "$SKIP_SEED" -eq 1 ]]; then
  echo "      Seed data SKIPPED (--skip-seed)."
else
  # Seed inserts are best-effort: on an existing DB the live data may
  # legitimately differ from the seed (e.g. categories edited/deleted in
  # the app), so errors here are reported, not fatal.
  SEED_OUT="$(awk '
    BEGIN { in_insert = 0; printing = 0 }
    /^[ \t]*INSERT[ \t]+INTO/ { in_insert = 1; printing = 1 }
    {
      if (printing) print
      if (in_insert && $0 ~ /;[ \t]*$/) { in_insert = 0; printing = 0 }
    }
  ' "$INIT_SQL" | psql_as "$APP_USER" "$APP_PASSWORD" "$DB_NAME" -q -f - 2>&1 || true)"
  if [[ -n "$SEED_OUT" ]]; then
    echo "      NOTE: some seed rows were not inserted (existing data differs):"
    echo "$SEED_OUT" | sed 's/^/        /'
  else
    echo "      Seed data applied."
  fi
fi

# ---------- 5. verification ----------
echo "[6/6] Verification — tables in schema '$DB_SCHEMA':"
psql_as "$APP_USER" "$APP_PASSWORD" "$DB_NAME" -c \
  "SELECT table_name FROM information_schema.tables
   WHERE table_schema='$DB_SCHEMA' AND table_type='BASE TABLE'
   ORDER BY table_name;"
PRODUCTS_COUNT="$(psql_as "$APP_USER" "$APP_PASSWORD" "$DB_NAME" -qAt \
  -c "SELECT count(*) FROM products;")"
echo "Seed check: products table has $PRODUCTS_COUNT rows."
echo "=============================================="
echo " DONE — database '$DB_NAME' is ready."
echo " Put these in the project .env to connect:"
echo "   DB_HOST=...  DB_PORT=...  DB_NAME=$DB_NAME"
echo "   DB_USER=$APP_USER  DB_PASSWORD=<the app password>"
echo "=============================================="