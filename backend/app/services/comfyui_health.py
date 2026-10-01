"""ComfyUI availability and configuration."""
import logging
import os

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


def is_comfyui_enabled() -> bool:
    from app.core.config import use_comfyui

    return use_comfyui()


def is_comfyui_available(timeout: float = 3.0) -> bool:
    if not is_comfyui_enabled():
        return False
    base = settings.COMFYUI_URL.rstrip("/")
    url = f"{base}/system_stats"
    try:
        response = httpx.get(url, timeout=timeout)
        return response.status_code == 200
    except Exception as exc:
        logger.warning("ComfyUI not reachable at %s: %s", url, exc)
        return False


def get_comfyui_status() -> dict:
    enabled = is_comfyui_enabled()
    available = is_comfyui_available() if enabled else False
    return {
        "enabled": enabled,
        "available": available,
        "url": settings.COMFYUI_URL,
        "checkpoint": settings.COMFYUI_CHECKPOINT,
    }
