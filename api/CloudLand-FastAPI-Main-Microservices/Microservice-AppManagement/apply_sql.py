import asyncio
from core.db import async_session_maker
from sqlalchemy import text

async def apply():
    with open('Structure/sql/functions.sql', 'r') as f:
        sql = f.read()
    
    # Split by GO because SQLAlchemy doesn't like GO
    parts = sql.split('\nGO\n')
    
    async with async_session_maker() as session:
        for part in parts:
            if part.strip():
                await session.execute(text(part))
        await session.commit()
    print("SQL Applied Successfully!")

asyncio.run(apply())
