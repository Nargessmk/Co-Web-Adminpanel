import asyncio
from sqlalchemy import text
from middleware.uow_middleware import get_current_uow
import os
import sys

# add parent directory of 'Models' to path
sys.path.append(os.path.abspath('..'))
from DB.database import AsyncSessionLocal

async def test():
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            text("SELECT * FROM tblUserConstantPermission WHERE role_id = '683fa052-f315-40f2-a87a-9a39ecf5fbde'")
        )
        rows = result.mappings().all()
        print(f"Role has {len(rows)} constant permissions:")
        for r in rows:
            print(r)
            
if __name__ == "__main__":
    asyncio.run(test())
