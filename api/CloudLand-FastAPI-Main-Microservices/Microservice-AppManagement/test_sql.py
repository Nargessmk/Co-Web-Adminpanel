import asyncio
from sqlalchemy import text
from core.database import AsyncSessionLocal

async def test():
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            text(
                "SELECT * FROM dbo.GetConstantsRecursiveWithPermissions("
                ":root_id, :user_id, :role_ids, :group_ids, :app_id)"
            ),
            {
                "root_id": "f29cefed-da7b-4211-9860-2c4fd4bd4cad",
                "user_id": None,
                "role_ids": "683fa052-f315-40f2-a87a-9a39ecf5fbde",
                "group_ids": None,
                "app_id": "508068a3-040a-41cd-93a5-b5527ff7b52c"
            }
        )
        rows = result.mappings().all()
        print(f"Returned {len(rows)} rows")

if __name__ == "__main__":
    asyncio.run(test())
