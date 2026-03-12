import os
from .local import LocalStorage
from .s3 import S3Storage
from .base import BaseStorage

def get_storage() -> BaseStorage:
    storage_type = os.getenv("STORAGE_TYPE", "local").lower()
    
    if storage_type == "s3":
        return S3Storage()
    else:
        # Default local
        return LocalStorage()

# Singleton instance
storage = get_storage()
