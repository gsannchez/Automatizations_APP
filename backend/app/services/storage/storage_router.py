import logging
from typing import Dict, Optional
from .storage_provider import StorageProvider
from .local_storage import LocalStorageProvider
from .s3_storage import S3StorageProvider

logger = logging.getLogger(__name__)

class StorageRouter:
    """
    Routes storage requests to the appropriate backend based on configuration
    or tenant routing rules.
    """
    def __init__(self, default_provider: str = "local"):
        self.providers: Dict[str, StorageProvider] = {
            "local": LocalStorageProvider(),
            "s3": S3StorageProvider(bucket_name="auto-video-maker-assets") 
            # In production, S3 config should be injected via env vars
        }
        self.default_provider = default_provider

    def get_provider(self, scheme_or_tenant: Optional[str] = None) -> StorageProvider:
        """Resolve the provider."""
        if scheme_or_tenant and scheme_or_tenant in self.providers:
            return self.providers[scheme_or_tenant]
        return self.providers[self.default_provider]


class AssetRegistry:
    """
    Tracks metadata and location of assets across distributed storage.
    """
    def __init__(self, redis_client):
        self.redis = redis_client
        self.prefix = "asset:"

    async def register_asset(self, asset_id: str, storage_uri: str, metadata: dict):
        """Save asset location and metadata."""
        payload = {
            "uri": storage_uri,
            "metadata": metadata
        }
        import json
        await self.redis.set(f"{self.prefix}{asset_id}", json.dumps(payload))
        logger.debug(f"[AssetRegistry] Registered asset {asset_id} at {storage_uri}")

    async def resolve_asset(self, asset_id: str) -> Optional[dict]:
        """Get asset URI and metadata."""
        import json
        data = await self.redis.get(f"{self.prefix}{asset_id}")
        if data:
            return json.loads(data)
        return None
        
    async def invalidate_asset(self, asset_id: str):
        """Remove asset from registry."""
        await self.redis.delete(f"{self.prefix}{asset_id}")
