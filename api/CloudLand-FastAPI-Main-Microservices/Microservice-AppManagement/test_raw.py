import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from core.config import get_settings
from sqlalchemy import text

async def main():
    settings = get_settings()
    engine = create_async_engine(settings.database_url)
    async with engine.connect() as conn:
        result = await conn.execute(text("""
            SELECT * FROM dbo.GetConstantsRecursiveWithPermissions(
                'f29cefed-da7b-4211-9860-2c4fd4bd4cad',
                NULL,
                '683fa052-f315-40f2-a87a-9a39ecf5fbde',
                NULL,
                '508068a3-040a-41cd-93a5-b5527ff7b52c'
            )
        """))
        rows = result.fetchall()
        print(f"Got {len(rows)} rows for the role directly from SQL Server!")
        
        result2 = await conn.execute(text(
            "SELECT * FROM tblUserConstantPermission WHERE role_id = '683fa052-f315-40f2-a87a-9a39ecf5fbde'"
        ))
        rows2 = result2.fetchall()
        print(f"Records in tblUserConstantPermission for this role: {len(rows2)}")

if __name__ == "__main__":
    asyncio.run(main())
