import pytest
import os
import sys
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import NullPool

# Ensure we can import from backend
sys.path.append(os.path.join(os.getcwd(), 'backend'))

import app.core.database
from app.core.config import settings

os.environ["TESTING"] = "1"

@pytest.fixture(scope="session", autouse=True)
def override_engine():
    """Override the global async_engine with one that uses NullPool.
    This prevents 'another operation is in progress' errors caused by 
    connections being shared across different event loops in pytest-asyncio.
    """
    async_url = settings.DATABASE_URL
    if "postgresql://" in async_url:
        async_url = async_url.replace("postgresql://", "postgresql+asyncpg://")
    
    engine = create_async_engine(
        async_url,
        echo=False,
        future=True,
        poolclass=NullPool
    )
    app.core.database.async_engine = engine
    return engine
