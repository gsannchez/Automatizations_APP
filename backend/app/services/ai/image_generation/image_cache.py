"""
app/services/ai/image_generation/image_cache.py

Phase SDXL
Caches images based on prompt/seed combinations to avoid redundant generation.
"""
import os
import hashlib
import logging
from typing import Optional

from .generation_config import config

logger = logging.getLogger(__name__)

class ImageCache:
    def __init__(self):
        self.cache_dir = config.CACHE_DIR
        os.makedirs(self.cache_dir, exist_ok=True)

    def _generate_hash(self, prompt: str, style: str, seed: Optional[int]) -> str:
        """Generates a stable hash for the generation parameters."""
        data = f"{prompt}_{style}_{seed}".encode("utf-8")
        return hashlib.md5(data).hexdigest()

    def get_cached_image(self, prompt: str, style: str, seed: Optional[int]) -> Optional[str]:
        """Returns the absolute path to a cached image if it exists and is valid."""
        img_hash = self._generate_hash(prompt, style, seed)
        path = os.path.join(self.cache_dir, f"{img_hash}.png")
        
        if os.path.exists(path):
            if os.path.getsize(path) > 1024:  # Basic integrity check > 1KB
                logger.info(f"Cache hit for hash {img_hash}")
                return os.path.abspath(path)
            else:
                logger.warning(f"Corrupt cached image detected at {path}. Removing.")
                os.remove(path)
                
        return None

    def get_cache_path(self, prompt: str, style: str, seed: Optional[int]) -> str:
        """Gets the intended path for a new generation."""
        img_hash = self._generate_hash(prompt, style, seed)
        return os.path.abspath(os.path.join(self.cache_dir, f"{img_hash}.png"))
