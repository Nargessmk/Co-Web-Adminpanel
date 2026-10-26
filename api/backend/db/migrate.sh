#!/usr/bin/env bash
# ============================================================
# CloudLand — schema migration for an EXISTING database
#
# init.sql is mounted into /docker-entrypoint-initdb.d/, so PostgreSQL only
# runs it when the data directory is empty — i.e. on the very first init. Every
# later `git pull` that adds columns or tables therefore does NOT reach a
# running database, and the app fails at runtime with errors such as:
#
#     column "header_buttons_order" does not exist
#
# This script applies the current schema to a database that is already running.
# It is idempotent: CREATE TABLE / CREATE INDEX / ADD COLUMN all use IF NOT
# EXISTS, and seed data is never touched (the data on a live site is real).
#
# Usage — LOCAL (postgres in Docker, container cloudland-postgres):
#
#     ./migrate.sh
#
# Usage — REMOTE / REAL SERVER:
#
#     DB_HOST=db.example.com DB_PORT=5432 \
#     DB_USER=cloudland_user DB_PASSWORD='secret' DB_NAME=cloudland \
#     ./migrate.sh
#
# Options:
#     --dry-run   print the SQL that would be applied and exit (no changes)
#     --check     report which migrations are missing, apply nothing
# ============================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INIT_SQL="$SCRIPT_DIR/init.sql"

DB_NAME="${DB_NAME:-cloudland}"
DB_HOST="${DB_HOST:-127.0.0.1}"
DB_PORT="${DB_PORT:-5432}"
DB_USER="${DB_USER:-cloudland_user}"
DB_PASSWORD="${DB_PASSWORD:-}"
DB_SCHEMA="${DB_SCHEMA:-public}"
DRY_RUN=0
CHECK_ONLY=0
DOCKER=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) DRY_RUN=1 ;;
    --check)   CHECK_ONLY=1 ;;
    --docker)  DOCKER=1 ;;
    -h|--help) grep '^#' "$0" | head -26; exit 0 ;;
    *) echo "Unknown option: $1 (see --help)"; exit 1 ;;
  esac
  shift
done

[[ -f "$INIT_SQL" ]] || { echo "ERROR: $INIT_SQL not found"; exit 1; }

# Runs SQL against the target database. Reads stdin.
run_sql() {
  if [[ $DOCKER -eq 1 ]]; then
    docker exec -i -e PGPASSWORD="$DB_PASSWORD" \
      -e PGOPTIONS="-c search_path=${DB_SCHEMA},public" \
      cloudland-postgres psql -U "$DB_USER" -d "$DB_NAME" -v ON_ERROR_STOP=1 -q "$@"
  else
    PGPASSWORD="$DB_PASSWORD" PGOPTIONS="-c search_path=${DB_SCHEMA},public" \
      psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" \
           -v ON_ERROR_STOP=1 -q "$@"
  fi
}

query() { run_sql -t -A -c "$1"; }

# Only INSERT ... ; blocks are removed: the file interleaves schema and seed
# data, so cutting at a comment would discard real migrations.
schema_only() {
  awk '
    BEGIN { in_insert = 0 }
    /^[ \t]*INSERT[ \t]+INTO/ { in_insert = 1 }
    {
      if (in_insert) {
        if ($0 ~ /;[ \t]*$/) in_insert = 0
        next
      }
      print
    }
  ' "$INIT_SQL"
}

echo "=============================================="
echo " CloudLand schema migration"
echo "   target : $([[ $DOCKER -eq 1 ]] && echo 'docker:cloudland-postgres' || echo "$DB_HOST:$DB_PORT")/$DB_NAME"
echo "   source : $INIT_SQL"
echo "=============================================="

# ---------- report what is missing ----------
# One query returns every existing table/column, and the comparison happens
# locally. The previous version ran a separate `docker exec` per object, which
# meant ~32 round trips and made the check slow enough to look like a hang.
EXISTING="$(query "SELECT table_name || '|' || column_name FROM information_schema.columns WHERE table_schema = '${DB_SCHEMA}'")"

PENDING=""
while IFS='|' read -r table column; do
  if [[ -z "$table" ]]; then
    # `if` rather than `[[ ... ]] && continue`: under `set -e` a failing `&&`
    # list aborts the whole script.
    continue
  fi
  if [[ -n "$column" ]]; then
    label="${table}.${column}"
    # A column exists only if the exact "table|column" pair is present.
    present=0
    printf '%s\n' "$EXISTING" | grep -qxF "${table}|${column}" && present=1
  else
    label="table ${table}"
    # Every table has at least one column, so a table exists when some row in the
    # inventory starts with its name. An exact match would always fail here,
    # because the inventory lists "table|column", never a bare "table|".
    present=0
    printf '%s\n' "$EXISTING" | grep -q "^${table}|" && present=1
  fi
  if [[ "$present" -eq 0 ]]; then
    PENDING+="${label}"$'\n'
  fi
done < <(awk '
  # Table name from: CREATE TABLE IF NOT EXISTS <name> (
  /^[ \t]*CREATE[ \t]+TABLE[ \t]+IF[ \t]+NOT[ \t]+EXISTS[ \t]+[a-zA-Z0-9_]+/ {
    line = $0
    sub(/^.*CREATE[ \t]+TABLE[ \t]+IF[ \t]+NOT[ \t]+EXISTS[ \t]+/, "", line)
    sub(/[^a-zA-Z0-9_].*$/, "", line)
    if (line != "") print line "|"
  }
  # Remember the table of the current ALTER, because the ADD COLUMN often sits
  # on the following line and has to be paired with it.
  /^[ \t]*ALTER[ \t]+TABLE[ \t]+[a-zA-Z0-9_]+/ {
    line = $0
    sub(/^.*ALTER[ \t]+TABLE[ \t]+/, "", line)
    gsub(/[^a-zA-Z0-9_].*$/, "", line)
    if (line != "") alter_table = line
  }
  /ADD[ \t]+COLUMN[ \t]+IF[ \t]+NOT[ \t]+EXISTS[ \t]+[a-zA-Z0-9_]+/ {
    line = $0
    sub(/^.*ADD[ \t]+COLUMN[ \t]+IF[ \t]+NOT[ \t]+EXISTS[ \t]+/, "", line)
    sub(/[^a-zA-Z0-9_].*$/, "", line)
    if (alter_table != "" && line != "") print alter_table "|" line
  }
' "$INIT_SQL" | sort -u)

if [[ -z "${PENDING//[$'\n' ]/}" ]]; then
  echo "[OK] Database schema is already up to date. Nothing to apply."
  exit 0
fi

echo "Pending migrations:"
printf '%s' "$PENDING" | sed '/^$/d' | sed 's/^/  - /'

if [[ $CHECK_ONLY -eq 1 ]]; then
  echo
  echo "--check: no changes were made."
  exit 1
fi

if [[ $DRY_RUN -eq 1 ]]; then
  echo
  echo "--dry-run: SQL that would be applied:"
  echo "----------------------------------------------"
  schema_only
  echo "----------------------------------------------"
  exit 0
fi

# ---------- apply ----------
echo
echo "Applying schema (idempotent)..."
if schema_only | run_sql -f -; then
  echo "[OK] Schema applied. Seed data was not touched."
else
  echo "[ERROR] Migration failed — see the SQL error above." >&2
  exit 1
fi
