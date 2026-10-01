import logging
import json
import time
from typing import Optional, Dict

logger = logging.getLogger(__name__)

class CacheIndex:
    """
    Redis-backed metadata index for the distributed cache.
    Handles LRU updates and basic querying.
    """
    def __init__(self, redis_client):
        self.redis = redis_client
        self.prefix = "cache_index:"
        self.lru_zset = "cache_lru"

    async def get_entry(self, asset_hash: str) -> Optional[Dict]:
        data = await self.redis.get(f"{self.prefix}{asset_hash}")
        if data:
            return json.loads(data)
        return None

    async def set_entry(self, asset_hash: str, uri: str, asset_type: str):
        payload = {
            "uri": uri,
            "type": asset_type,
            "created_at": time.time()
        }
        await self.redis.set(f"{self.prefix}{asset_hash}", json.dumps(payload))
        await self.touch(asset_hash)

    async def touch(self, asset_hash: str):
        """Update LRU timestamp in Redis Sorted Set."""
        await self.redis.zadd(self.lru_zset, {asset_hash: time.time()})

    async def remove_entry(self, asset_hash: str):
        await self.redis.delete(f"{self.prefix}{asset_hash}")
        await self.redis.zrem(self.lru_zset, asset_hash)
