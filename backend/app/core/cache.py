import redis.asyncio as redis
import json
import os
from typing import Optional, Any

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

class CacheService:
    def __init__(self):
        self.redis = redis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)

    async def get(self, key: str) -> Optional[Any]:
        val = await self.redis.get(key)
        if val:
            try:
                return json.loads(val)
            except:
                return val
        return None

    async def set(self, key: str, value: Any, expire: int = 3600):
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        await self.redis.set(key, value, ex=expire)

    async def delete(self, key: str):
        await self.redis.delete(key)

cache = CacheService()
