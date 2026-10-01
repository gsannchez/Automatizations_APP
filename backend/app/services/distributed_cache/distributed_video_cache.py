import logging
import hashlib
from typing import Optional
from .cache_index import CacheIndex
from ..storage.storage_router import StorageRouter

logger = logging.getLogger(__name__)

class DistributedVideoCache:
    """
    High-level interface for caching generated video clips, images,
    and embeddings across the cluster.
    """
    def __init__(self, redis_client, storage_router: StorageRouter):
        self.index = CacheIndex(redis_client)
        self.storage = storage_router.get_provider() # Can be overridden per request
        
    def _compute_hash(self, parameters: dict) -> str:
        """Deterministically hash generation parameters to use as cache key."""
        import json
        param_str = json.dumps(parameters, sort_keys=True)
        return hashlib.sha256(param_str.encode()).hexdigest()

    async def get_cached_asset(self, parameters: dict) -> Optional[str]:
        """
        Check if an asset with these exact parameters exists.
        Returns the storage URI if found and valid.
        """
        asset_hash = self._compute_hash(parameters)
        entry = await self.index.get_entry(asset_hash)
        
        if entry and await self._validate_corruption(entry["uri"]):
            logger.info(f"[DistributedCache] Cache hit for {asset_hash}")
            await self.index.touch(asset_hash) # Update LRU
            return entry["uri"]
            
        logger.debug(f"[DistributedCache] Cache miss for {asset_hash}")
        return None

    async def set_cached_asset(self, parameters: dict, local_path: str, asset_type: str = "video") -> str:
        """
        Upload local file to shared storage and register in distributed cache.
        """
        asset_hash = self._compute_hash(parameters)
        dest_key = f"cache/{asset_type}/{asset_hash}.mp4" # Simplify extension handling for now
        
        uri = await self.storage.upload_file(local_path, dest_key)
        await self.index.set_entry(asset_hash, uri, asset_type)
        
        logger.info(f"[DistributedCache] Cached new {asset_type} at {uri} (Hash: {asset_hash})")
        return uri

    async def _validate_corruption(self, uri: str) -> bool:
        """
        Hook to validate if the file at URI is corrupted or missing.
        For now, we assume true if it exists in index, but a real impl
        would check storage provider or file headers.
        """
        return True
