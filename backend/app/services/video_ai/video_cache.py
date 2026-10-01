import hashlib
import os
import shutil
import logging

logger = logging.getLogger(__name__)

class VideoCache:
    """
    Caches expensive AI video generations based on prompt, seed, and style.
    Phase 6.5: Integrated with CacheIntegrity to auto-purge corrupt cached files.
    """
    
    def __init__(self, cache_dir: str = "media/cache/video"):
        self.cache_dir = cache_dir
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir, exist_ok=True)
            
    def _generate_hash(self, prompt: str, seed: int, style: str, duration: float) -> str:
        hash_input = f"{prompt}_{seed}_{style}_{duration}".encode("utf-8")
        return hashlib.md5(hash_input).hexdigest()
        
    def get_cached_video(self, prompt: str, seed: int, style: str, duration: float) -> str:
        """
        Returns the local path to the cached video if it exists AND passes integrity check.
        Automatically purges corrupt files and returns None to trigger regeneration.
        """
        from ..cache.cache_integrity import CacheIntegrity

        file_hash = self._generate_hash(prompt, seed, style, duration)
        cache_path = os.path.join(self.cache_dir, f"{file_hash}.mp4")
        
        if os.path.exists(cache_path):
            if CacheIntegrity.is_valid(cache_path):
                logger.info(f"[VideoCache] Cache HIT (valid): {cache_path}")
                return cache_path
            else:
                logger.warning(f"[VideoCache] Cache HIT but CORRUPT — purging: {cache_path}")
                os.remove(cache_path)
                return None

        return None
        
    def save_to_cache(self, source_path: str, prompt: str, seed: int, style: str, duration: float) -> str:
        """Saves a generated video to the cache. Validates before saving."""
        from ..cache.cache_integrity import CacheIntegrity

        if not CacheIntegrity.is_valid(source_path):
            logger.error(f"[VideoCache] Refusing to cache corrupt file: {source_path}")
            return source_path  # Return original path without caching

        file_hash = self._generate_hash(prompt, seed, style, duration)
        cache_path = os.path.join(self.cache_dir, f"{file_hash}.mp4")
        shutil.copy2(source_path, cache_path)
        logger.info(f"[VideoCache] Saved to cache: {cache_path}")
        return cache_path

