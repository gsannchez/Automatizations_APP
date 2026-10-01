"""
app/services/storage/asset_registry.py

Redis-backed registry mapping asset IDs to their storage URIs and metadata.
Provides cache invalidation and existence checks without touching actual storage.
"""
import json
import logging
import time
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

PREFIX = "asset_registry:"
TTL_DEFAULT = 86400 * 7  # 7 days


class AssetRegistry:
    """
    Tracks where each asset lives (local, S3, etc.) and its associated
    metadata (size, type, created_at, tenant_id).
    """

    def __init__(self, redis_client):
        self.redis = redis_client

    async def register(
        self,
        asset_id: str,
        storage_uri: str,
        asset_type: str,
        tenant_id: str = "default",
        extra: Optional[Dict] = None,
    ) -> None:
        payload = {
            "uri": storage_uri,
            "type": asset_type,
            "tenant_id": tenant_id,
            "created_at": time.time(),
            **(extra or {}),
        }
        await self.redis.set(
            f"{PREFIX}{asset_id}",
            json.dumps(payload),
            ex=TTL_DEFAULT,
        )
        logger.debug(f"[AssetRegistry] Registered {asset_id} → {storage_uri}")

    async def resolve(self, asset_id: str) -> Optional[Dict]:
        """Return full asset metadata dict or None if not found."""
        raw = await self.redis.get(f"{PREFIX}{asset_id}")
        return json.loads(raw) if raw else None

    async def get_uri(self, asset_id: str) -> Optional[str]:
        meta = await self.resolve(asset_id)
        return meta["uri"] if meta else None

    async def invalidate(self, asset_id: str) -> None:
        await self.redis.delete(f"{PREFIX}{asset_id}")
        logger.info(f"[AssetRegistry] Invalidated {asset_id}")

    async def exists(self, asset_id: str) -> bool:
        return bool(await self.redis.exists(f"{PREFIX}{asset_id}"))

    async def list_by_tenant(self, tenant_id: str) -> List[Dict]:
        """Scan registry for all assets belonging to a tenant (expensive — use sparingly)."""
        keys = await self.redis.keys(f"{PREFIX}*")
        results = []
        for key in keys:
            raw = await self.redis.get(key)
            if raw:
                data = json.loads(raw)
                if data.get("tenant_id") == tenant_id:
                    asset_id = key.decode().replace(PREFIX, "") if isinstance(key, bytes) else key.replace(PREFIX, "")
                    results.append({"asset_id": asset_id, **data})
        return results
