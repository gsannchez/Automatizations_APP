import os
import shutil
from pathlib import Path
from typing import BinaryIO, Union
from .base import BaseStorage

class LocalStorage(BaseStorage):
    def __init__(self, base_path: str = "media"):
        # Asegurar que base_path es absoluto
        if not os.path.isabs(base_path):
            # Asumimos que es relativo a la raíz del proyecto backend/
            # Ajustar según la estructura real: backend/app/services/storage/local.py -> ../../../
            current_dir = Path(__file__).parent
            project_root = current_dir.parent.parent.parent # backend/app/services/storage -> backend/app/services -> backend/app -> backend
            self.base_path = project_root / base_path
        else:
            self.base_path = Path(base_path)
        
        self.base_path.mkdir(parents=True, exist_ok=True)

    def save(self, file_obj: Union[BinaryIO, bytes], path: str) -> str:
        full_path = self.base_path / path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        if isinstance(file_obj, bytes):
            with open(full_path, "wb") as f:
                f.write(file_obj)
        else:
            # Asumimos que es un objeto tipo archivo puntero al inicio
            with open(full_path, "wb") as f:
                shutil.copyfileobj(file_obj, f)
        
        # En local devolvemos el path relativo como identificador
        return path

    def get_url(self, path: str) -> str:
        # En desarrollo local, serviríamos esto a través de un endpoint de archivos estáticos o nginx
        # Retornamos una URL relativa que la aplicación pueda resolver
        return f"/media/{path}"

    def get_local_path(self, path: str) -> str:
        full_path = self.base_path / path
        if not full_path.exists():
            raise FileNotFoundError(f"File not found: {full_path}")
        return str(full_path)

    def delete(self, path: str) -> bool:
        full_path = self.base_path / path
        if full_path.exists():
            os.remove(full_path)
            return True
        return False
