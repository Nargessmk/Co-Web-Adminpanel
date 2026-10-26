import os
from pathlib import Path


def get_database_url() -> str:
    env_path = Path(__file__).resolve().parent.parent.parent / "Microservice-AppManagement" / ".env"
    if env_path.exists():
        from dotenv import load_dotenv
        load_dotenv(env_path)
    url = os.getenv("DATABASE_URL", "sqlite:///./app_management.db")
    url = url.replace("+aiosqlite", "").replace("+asyncpg", "").replace("+psycopg", "").replace("+aioodbc", "")
    return url
