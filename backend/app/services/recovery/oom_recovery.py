import logging
from ..monitoring.cuda_cleanup import CUDACleanup
from .emergency_fallback import EmergencyFallback

logger = logging.getLogger(__name__)

class OOMRecovery:
    """
    Catches Out-Of-Memory errors and tries to recover gracefully.
    """
    @staticmethod
    def execute_with_recovery(func, *args, **kwargs):
        """
        Executes a function. If it hits CUDA OOM, cleans up and falls back.
        """
        try:
            return func(*args, **kwargs)
        except RuntimeError as e:
            if "out of memory" in str(e).lower():
                logger.error("🚨 CUDA OOM Detected! Attempting recovery...")
                CUDACleanup.force_cleanup()
                logger.warning("Falling back to emergency static render.")
                return EmergencyFallback.get_fallback_video(*args, **kwargs)
            else:
                raise e
