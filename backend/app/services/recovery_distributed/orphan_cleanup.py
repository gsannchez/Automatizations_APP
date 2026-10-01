"""
app/services/recovery_distributed/orphan_cleanup.py

Removes stale Redis keys and expired GPU node registrations
left behind by crashed workers.
"""
import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class OrphanCleanup:
    """
    Periodically cleans up stale entries in Redis:
    - Expired GPU node heartbeats (auto-expire handles most, this handles edge cases)
    - Stale distributed lock keys held by dead processes
    - Orphaned tenant concurrency counters
    """

    def __init__(self, redis_client):
        self.redis = redis_client

    async def run(self) -> Dict[str, Any]:
        node_cleaned = await self._cleanup_stale_nodes()
        locks_cleaned = await self._cleanup_stale_locks()
        concurrency_cleaned = await self._cleanup_orphan_concurrency()

        result = {
            "stale_nodes_removed": node_cleaned,
            "stale_locks_removed": locks_cleaned,
            "concurrency_keys_reset": concurrency_cleaned,
        }
        logger.info(f"[OrphanCleanup] Complete: {result}")
        return result

    async def _cleanup_stale_nodes(self) -> int:
        """
        GPU nodes have Redis TTL expiry, but scan for any without TTL.
        """
        keys = await self.redis.keys("gpu_node:*")
        removed = 0
        for key in keys:
            ttl = await self.redis.ttl(key)
            if ttl == -1:  # Key exists but has no expiry — defensive cleanup
                await self.redis.expire(key, 120)
                logger.warning(f"[OrphanCleanup] Set missing TTL on {key}")
        return removed

    async def _cleanup_stale_locks(self) -> int:
        """
        Find lock keys that have survived past their expected TTL window.
        Re-set TTL if missing; delete if value is empty.
        """
        keys = await self.redis.keys("lock:*")
        cleaned = 0
        for key in keys:
            value = await self.redis.get(key)
            ttl = await self.redis.ttl(key)
            if not value:
                await self.redis.delete(key)
                cleaned += 1
                logger.info(f"[OrphanCleanup] Removed empty lock {key}")
            elif ttl == -1:
                # Reset with safety TTL
                await self.redis.expire(key, 60)
        return cleaned

    async def _cleanup_orphan_concurrency(self) -> int:
        """
        Tenant concurrency counters can get stuck > 0 if workers crash
        mid-execution. Cap them at 0 if the value is negative.
        """
        keys = await self.redis.keys("tenant_concurrency:*")
        reset = 0
        for key in keys:
            val = await self.redis.get(key)
            if val and int(val) < 0:
                await self.redis.set(key, 0)
                reset += 1
                logger.warning(f"[OrphanCleanup] Reset negative concurrency counter: {key}")
        return reset
