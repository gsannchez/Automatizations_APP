from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from .config import settings

# Usar sqlite+aiosqlite para soporte asíncrono
# Si settings.DATABASE_URL es "sqlite:///database.db", hay que cambiarlo a "sqlite+aiosqlite:///database.db"
DATABASE_URL = settings.DATABASE_URL.replace("sqlite://", "sqlite+aiosqlite://")

engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    future=True
)

async def init_db():
    async with engine.begin() as conn:
        # await conn.run_sync(SQLModel.metadata.drop_all) # Solo si queremos resetear
        await conn.run_sync(SQLModel.metadata.create_all)

async def get_session() -> AsyncSession:
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session
