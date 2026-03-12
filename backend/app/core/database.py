"""Database configuration with dual engine support.

FastAPI uses async engine (asyncpg) for non-blocking operations.
Celery uses sync engine (psycopg2) to avoid event loop conflicts.
"""
from sqlmodel import SQLModel, create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker, Session
from contextlib import asynccontextmanager, contextmanager
from .config import settings


# Async engine for FastAPI (uses asyncpg driver)
async_database_url = settings.DATABASE_URL
if "postgresql://" in async_database_url:
    async_database_url = async_database_url.replace("postgresql://", "postgresql+asyncpg://")

async_engine = create_async_engine(
    async_database_url,
    echo=True,
    future=True
)

# Sync engine for Celery (uses psycopg2 driver)
sync_database_url = settings.DATABASE_URL
if "postgresql://" in sync_database_url:
    sync_database_url = sync_database_url.replace("postgresql://", "postgresql+psycopg2://")

sync_engine = create_engine(
    sync_database_url,
    echo=True,
    future=True
)


async def init_db():
    """Initialize database tables using async engine."""
    from app.models.user import User
    from app.models.channel import Channel
    from app.models.template import Template
    from app.models.generated_video import GeneratedVideo
    from app.models.video_job import VideoJob
    from app.models.asset import Asset
    
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_async_session() -> AsyncSession:
    """Async session factory for FastAPI endpoints.
    
    Usage:
        @app.get("/videos")
        async def list_videos(session: AsyncSession = Depends(get_async_session)):
            ...
    """
    async_session = async_sessionmaker(
        async_engine, 
        class_=AsyncSession, 
        expire_on_commit=False
    )
    async with async_session() as session:
        yield session


@contextmanager
def get_sync_session():
    """Sync session context manager for Celery tasks.
    
    Usage:
        @celery_app.task
        def process_video(video_id):
            with get_sync_session() as session:
                video = session.get(Video, video_id)
                ...
    """
    SessionLocal = sessionmaker(
        bind=sync_engine,
        class_=Session,
        expire_on_commit=False
    )
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
