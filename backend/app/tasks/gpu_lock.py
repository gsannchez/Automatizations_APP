import os
import redis
import logging
from contextlib import contextmanager

logger = logging.getLogger(__name__)

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Cliente redis síncrono para los workers
redis_client = redis.from_url(REDIS_URL)

class GPULockError(Exception):
    pass

@contextmanager
def acquire_gpu_lock(timeout: int = 600, blocking_timeout: int = 120):
    """
    Adquiere un bloqueo exclusivo para el uso de la GPU.
    Utiliza redis lock para garantizar que múltiples workers no saturen la VRAM.
    
    :param timeout: Tiempo máximo (en segundos) que se mantiene el lock antes de expirar por seguridad.
    :param blocking_timeout: Tiempo máximo que un worker esperará para adquirir el lock.
    """
    lock = redis_client.lock("global_gpu_lock", timeout=timeout, blocking_timeout=blocking_timeout)
    # Intentionally block only for a limited time (blocking_timeout)
    acquired = lock.acquire(blocking=True, blocking_timeout=blocking_timeout)

    if not acquired:
        logger.error("No se pudo adquirir el lock de la GPU en el tiempo especificado.")
        raise GPULockError("Timeout esperando el lock de la GPU")
        
    try:
        logger.info("🔒 GPU Lock adquirido")
        yield
    finally:
        try:
            lock.release()
            logger.info("🔓 GPU Lock liberado")
        except redis.exceptions.LockError:
            logger.warning("El lock de la GPU ya había expirado o fue liberado por otro proceso.")
