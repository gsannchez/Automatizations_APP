import psutil
import os
import logging

logger = logging.getLogger(__name__)

class MemoryGuard:
    """
    Monitors system RAM (not just VRAM) during heavy tasks.
    """
    @staticmethod
    def check_system_memory() -> bool:
        """Returns True if there is enough free system memory."""
        mem = psutil.virtual_memory()
        if mem.percent > 95.0:
            logger.critical(f"⚠️ SYSTEM RAM CRITICAL: {mem.percent}% used. May cause swap thrashing.")
            return False
        return True
