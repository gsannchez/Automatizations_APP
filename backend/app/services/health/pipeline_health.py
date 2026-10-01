import logging
from ..monitoring.gpu_watchdog import GPUWatchdog
from ..adaptive.quality_manager import QualityManager
from .celery_health import get_celery_worker_status

logger = logging.getLogger(__name__)

class PipelineHealth:
    """
    Aggregates health signals from all subsystems.
    """
    @staticmethod
    def get_status() -> dict:
        """Returns a full snapshot of the pipeline's health."""
        vram = GPUWatchdog.get_vram_usage()
        quality_tier = QualityManager.get_tier().value
        safe_to_start = GPUWatchdog.is_safe_to_start()
        celery = get_celery_worker_status()

        status = "healthy"
        if not celery["available"]:
            status = "degraded"
        if not safe_to_start:
            status = "degraded"
        if vram.get("usage_percent", 0) > 95:
            status = "critical"

        return {
            "status": status,
            "quality_tier": quality_tier,
            "gpu": vram,
            "safe_to_start_new_task": safe_to_start and celery["available"],
            "celery": celery,
        }
