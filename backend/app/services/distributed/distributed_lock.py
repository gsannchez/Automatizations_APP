import asyncio
import logging
from typing import Optional
import uuid
import time

logger = logging.getLogger(__name__)

class DistributedLock:
    """
    Redis-backed distributed lock implementation.
    Prevents multiple nodes from running the same critical section.
    """
    def __init__(self, redis_client, lock_name: str, expire_seconds: int = 30):
        self.redis = redis_client
        self.lock_name = f"lock:{lock_name}"
        self.expire_seconds = expire_seconds
        self.lock_id = str(uuid.uuid4())
        self._acquired = False

    async def acquire(self) -> bool:
        """Attempt to acquire the lock without blocking."""
        result = await self.redis.set(self.lock_name, self.lock_id, nx=True, ex=self.expire_seconds)
        if result:
            self._acquired = True
            logger.debug(f"[DistributedLock] Acquired {self.lock_name}")
            return True
        return False

    async def release(self) -> None:
        """Release the lock if it was acquired by this instance."""
        if not self._acquired:
            return
            
        script = """
        if redis.call("get", KEYS[1]) == ARGV[1] then
            return redis.call("del", KEYS[1])
        else
            return 0
        end
        """
        await self.redis.eval(script, 1, self.lock_name, self.lock_id)
        self._acquired = False
        logger.debug(f"[DistributedLock] Released {self.lock_name}")

    async def __aenter__(self):
        # Blocking acquire with timeout for convenience
        start = time.time()
        while time.time() - start < self.expire_seconds:
            if await self.acquire():
                return self
            await asyncio.sleep(0.1)
        raise TimeoutError(f"Could not acquire lock {self.lock_name}")

    async def __aexit__(self, exc_type, exc, tb):
        await self.release()
