import os
import aiofiles
import logging
from typing import BinaryIO, Optional
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class StorageProvider(ABC):
    """Abstract interface for all shared storage backends."""
    
    @abstractmethod
    async def upload_file(self, source_path: str, destination_key: str) -> str:
        """Uploads a local file to storage. Returns the storage URI/key."""
        pass
        
    @abstractmethod
    async def download_file(self, source_key: str, destination_path: str) -> bool:
        """Downloads a file from storage to local disk."""
        pass

    @abstractmethod
    async def get_signed_url(self, key: str, expires_in: int = 3600) -> str:
        """Returns a signed URL for public/temporary access."""
        pass
        
    @abstractmethod
    async def delete_file(self, key: str) -> bool:
        """Deletes a file from storage."""
        pass

class LocalStorageProvider(StorageProvider):
    """Local disk implementation for backward compatibility and local testing."""
    
    def __init__(self, base_dir: str = "/tmp/auto_video_maker"):
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)

    async def upload_file(self, source_path: str, destination_key: str) -> str:
        dest_path = os.path.join(self.base_dir, destination_key)
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        
        async with aiofiles.open(source_path, 'rb') as src:
            async with aiofiles.open(dest_path, 'wb') as dst:
                await dst.write(await src.read())
        
        logger.debug(f"[LocalStorage] Copied {source_path} to {dest_path}")
        return f"local://{destination_key}"

    async def download_file(self, source_key: str, destination_path: str) -> bool:
        src_path = os.path.join(self.base_dir, source_key)
        if not os.path.exists(src_path):
            return False
            
        os.makedirs(os.path.dirname(destination_path), exist_ok=True)
        async with aiofiles.open(src_path, 'rb') as src:
            async with aiofiles.open(destination_path, 'wb') as dst:
                await dst.write(await src.read())
        return True

    async def get_signed_url(self, key: str, expires_in: int = 3600) -> str:
        # Local storage doesn't support signed URLs naturally without an HTTP server
        return f"file://{os.path.join(self.base_dir, key)}"

    async def delete_file(self, key: str) -> bool:
        target = os.path.join(self.base_dir, key)
        if os.path.exists(target):
            os.remove(target)
            return True
        return False
