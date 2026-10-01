"""
app/services/distributed_cache/cache_replication.py

Tracks replication metadata for hot cache assets across storage regions.
Actual copying is delegated to an async Celery task to avoid blocking.
"""
import json
import logging
import time
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

REPLICATION_META_KEY = "cache_replication_meta"


class CacheReplication:
    """
    Maintains a Redis hash of asset_hash → replication state.
    When an asset becomes hot (hit_count > threshold), the replication
    engine schedules a copy to secondary storage.
    """

    def __init__(self, redis_client, celery_app=None, hot_threshold: int = 10):
        self.redis = redis_client
        self.celery = celery_app
        self.hot_threshold = hot_threshold

    async def record_hit(self, asset_hash: str) -> None:
        """Increment hit counter and trigger replication if threshold reached."""
        hit_key = f"cache_hits:{asset_hash}"
        count = await self.redis.incr(hit_key)
        await self.redis.expire(hit_key, 86400)  # Reset daily

        if count == self.hot_threshold:
            logger.info(
                f"[CacheReplication] Asset {asset_hash} is hot ({count} hits). "
                "Scheduling replication."
            )
            await self._schedule_replication(asset_hash)

    async def _schedule_replication(self, asset_hash: str) -> None:
        """Enqueue a background Celery task to replicate the asset."""
        meta = await self._get_replication_meta(asset_hash)
        if meta and meta.get("status") == "replicated":
            return  # Already replicated

        await self._set_replication_meta(
            asset_hash, {"status": "pending", "scheduled_at": time.time()}
        )

        if self.celery:
            self.celery.send_task(
                "app.tasks.cache.replicate_asset",
                kwargs={"asset_hash": asset_hash},
                queue="cpu_queue",
            )

    async def mark_replicated(
        self, asset_hash: str, target_region: str, target_uri: str
    ) -> None:
        await self._set_replication_meta(
            asset_hash,
            {
                "status": "replicated",
                "region": target_region,
                "uri": target_uri,
                "replicated_at": time.time(),
            },
        )
        logger.info(
            f"[CacheReplication] {asset_hash} replicated to {target_region}: {target_uri}"
        )

    async def get_replica_uri(
        self, asset_hash: str, region: str
    ) -> Optional[str]:
        meta = await self._get_replication_meta(asset_hash)
        if meta and meta.get("region") == region:
            return meta.get("uri")
        return None

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    async def _get_replication_meta(self, asset_hash: str) -> Optional[Dict]:
        raw = await self.redis.hget(REPLICATION_META_KEY, asset_hash)
        return json.loads(raw) if raw else None

    async def _set_replication_meta(
        self, asset_hash: str, data: Dict
    ) -> None:
        await self.redis.hset(REPLICATION_META_KEY, asset_hash, json.dumps(data))
