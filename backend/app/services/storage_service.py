import os
import shutil
from abc import ABC, abstractmethod

class StorageService(ABC):
    @abstractmethod
    async def upload_file(self, file_path: str, destination: str) -> str:
        pass

    @abstractmethod
    async def delete_file(self, file_path: str):
        pass

class LocalStorageService(StorageService):
    def __init__(self, base_dir: str = "storage"):
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)

    async def upload_file(self, source_path: str, destination: str) -> str:
        """
        Simula subida copiando a un directorio 'storage'.
        Devuelve la URL relativa.
        """
        dest_full_path = os.path.join(self.base_dir, destination)
        os.makedirs(os.path.dirname(dest_full_path), exist_ok=True)
        
        # Copia asíncrona (simulada, shutil es síncrono pero rápido en local)
        shutil.copy2(source_path, dest_full_path)
        
        return f"/static/{destination}"

    async def delete_file(self, file_path: str):
        full_path = os.path.join(self.base_dir, file_path)
        if os.path.exists(full_path):
            os.remove(full_path)

# Instancia global (fácil de cambiar por S3StorageService luego)
storage = LocalStorageService()
