from abc import ABC, abstractmethod
from typing import BinaryIO, Union

class BaseStorage(ABC):
    @abstractmethod
    def save(self, file_obj: Union[BinaryIO, bytes], path: str) -> str:
        """
        Guarda un archivo en el storage.
        :param file_obj: Objeto tipo archivo o bytes.
        :param path: Ruta relativa dentro del bucket/directorio.
        :return: Ruta o URL del archivo guardado.
        """
        pass

    @abstractmethod
    def get_url(self, path: str) -> str:
        """
        Obtiene la URL pública o firmada para acceder al archivo.
        """
        pass

    @abstractmethod
    def get_local_path(self, path: str) -> str:
        """
        Obtiene la ruta local absoluta (solo si es LocalStorage) o descarga temporalmente.
        Útil para procesamiento con FFmpeg.
        """
        pass

    @abstractmethod
    def delete(self, path: str) -> bool:
        """
        Elimina el archivo.
        """
        pass
