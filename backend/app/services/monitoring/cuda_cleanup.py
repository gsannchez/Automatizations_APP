import torch
import gc
import logging

logger = logging.getLogger(__name__)

class CUDACleanup:
    """
    Aggressive memory cleanup to avoid fragmentation and leaks.
    """
    @staticmethod
    def force_cleanup():
        """Runs gc and empties CUDA cache."""
        logger.info("🧹 Initiating forced CUDA cleanup...")
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.ipc_collect()
        logger.info("✅ CUDA cleanup complete.")
