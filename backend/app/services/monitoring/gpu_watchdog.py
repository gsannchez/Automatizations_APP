import torch
import subprocess
import logging

logger = logging.getLogger(__name__)

class GPUWatchdog:
    """
    Monitors VRAM usage and warns/blocks new tasks if heavily fragmented.
    """
    
    @staticmethod
    def get_vram_usage() -> dict:
        """Returns VRAM usage stats."""
        if not torch.cuda.is_available():
            return {"status": "no_gpu"}
            
        try:
            device = torch.device('cuda')
            total = torch.cuda.get_device_properties(device).total_memory
            reserved = torch.cuda.memory_reserved(device)
            allocated = torch.cuda.memory_allocated(device)
            free = total - reserved
            
            return {
                "status": "ok",
                "total_gb": total / (1024**3),
                "reserved_gb": reserved / (1024**3),
                "allocated_gb": allocated / (1024**3),
                "free_gb": free / (1024**3),
                "usage_percent": (reserved / total) * 100
            }
        except Exception as e:
            logger.error(f"Error checking VRAM: {e}")
            return {"status": "error"}

    @staticmethod
    def is_safe_to_start() -> bool:
        """Returns True if VRAM is < 90% full."""
        stats = GPUWatchdog.get_vram_usage()
        if stats.get("status") != "ok":
            return True # Fallback if error or no gpu
            
        if stats.get("usage_percent", 0) > 90.0:
            logger.warning(f"⚠️ VRAM CRITICAL: {stats['usage_percent']}% used. Blocking task.")
            return False
            
        return True
