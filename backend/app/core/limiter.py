"""Centralised SlowAPI rate-limiter instance.

Uses Redis as the storage backend so counters persist across worker restarts.
Wire into FastAPI in ``app/main.py``:

    from app.core.limiter import limiter
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
"""
from slowapi import Limiter
from slowapi.util import get_remote_address

from .config import settings

limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=settings.REDIS_URL,
)
