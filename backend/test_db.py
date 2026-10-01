import asyncio
from app.core.database import async_engine
from sqlalchemy import text

async def query():
    async with async_engine.connect() as conn:
        res = await conn.execute(text('SELECT email FROM "user"'))
        print([r[0] for r in res.fetchall()])

asyncio.run(query())
