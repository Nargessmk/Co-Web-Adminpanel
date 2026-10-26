"""Standalone check: verifies Microservice-Storage can connect to PostgreSQL.

Run from the Microservice-Storage directory:
    python3 scripts/check_db_connection.py
"""

import asyncio
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import text  # noqa: E402

from core.config import get_settings  # noqa: E402
from core.db import init_db, check_db_connection, close_db  # noqa: E402


async def main() -> int:
    settings = get_settings()
    url = settings.database_url
    if not url:
        print("FAIL: database_url is not set (check Microservice-Storage/.env or env vars)")
        return 1

    # Never print the password
    safe_url = url.split("@")[-1]
    print(f"Connecting to: {safe_url}")

    engine = init_db(url)
    if engine is None:
        print("FAIL: engine could not be initialized")
        return 1

    ok = await check_db_connection()
    if not ok:
        print("FAIL: could not execute SELECT 1")
        await close_db()
        return 1

    # Show what we are actually connected to
    from core.db import get_session_factory

    factory = get_session_factory()
    async with factory() as session:
        row = (await session.execute(text(
            "SELECT current_database(), current_user, version()"
        ))).one()
    print("SUCCESS: PostgreSQL connection OK")
    print(f"  database : {row[0]}")
    print(f"  user     : {row[1]}")
    print(f"  version  : {row[2]}")

    await close_db()
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))