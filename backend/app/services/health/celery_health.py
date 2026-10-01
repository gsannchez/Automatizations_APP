"""Celery worker availability checks."""
import logging
from typing import Any

import redis

from app.core.celery_app import WORKER_HEARTBEAT_KEY, celery_app
from app.core.config import settings

logger = logging.getLogger(__name__)


def _check_redis_heartbeat() -> dict[str, Any] | None:
    try:
        client = redis.from_url(settings.REDIS_URL, decode_responses=True)
        value = client.get(WORKER_HEARTBEAT_KEY)
        if value:
            return {
                "available": True,
                "mode": "heartbeat",
                "workers": [value] if value != "1" else ["celery-worker"],
            }
    except Exception as exc:
        logger.warning("Redis heartbeat check failed: %s", exc)
    return None


def get_celery_worker_status(timeout: float = 3.0) -> dict[str, Any]:
    """Return whether at least one Celery worker is reachable."""
    if settings.CELERY_TASK_ALWAYS_EAGER:
        return {
            "available": True,
            "mode": "eager",
            "workers": ["in-process"],
        }

    heartbeat = _check_redis_heartbeat()
    if heartbeat:
        return heartbeat

    # Fallback: inspect (suele fallar en Windows aunque el worker esté activo)
    try:
        inspect = celery_app.control.inspect(timeout=timeout)
        ping = inspect.ping() if inspect else None
        if ping:
            return {
                "available": True,
                "mode": "inspect",
                "workers": list(ping.keys()),
            }
    except Exception as exc:
        logger.warning("Celery inspect failed: %s", exc)

    return {
        "available": False,
        "mode": "broker",
        "workers": [],
        "error": (
            "No hay worker de Celery en ejecución. "
            "Abre PowerShell en la carpeta backend y ejecuta: .\\run_celery.ps1 "
            "(deja esa ventana abierta)."
        ),
    }


def require_celery_worker(timeout: float = 3.0) -> None:
    """Raise RuntimeError if no worker is available (unless eager mode)."""
    status = get_celery_worker_status(timeout=timeout)
    if not status["available"]:
        raise RuntimeError(status.get("error", "Celery worker unavailable"))
