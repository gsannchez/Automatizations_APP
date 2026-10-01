"""
app/services/ai/image_generation/gpu_image_guard.py

Phase SDXL
Guards GPU memory, blocks inference if VRAM > 90%.
"""
import torch
import logging
import time

logger = logging.getLogger(__name__)

class GPUImageGuard:
    def __init__(self, threshold_percent: float = 90.0):
        self.threshold_percent = threshold_percent

    def get_vram_usage_percent(self) -> float:
        if not torch.cuda.is_available():
            return 0.0
            
        allocated = torch.cuda.memory_allocated()
        total = torch.cuda.get_device_properties(0).total_memory
        
        if total == 0:
            return 0.0
            
        return (allocated / total) * 100.0

    def wait_for_vram(self, timeout_seconds: int = 60, check_interval: int = 2) -> bool:
        """Blocks until VRAM is below threshold or timeout is reached."""
        if not torch.cuda.is_available():
            return True
            
        start_time = time.time()
        while time.time() - start_time < timeout_seconds:
            usage = self.get_vram_usage_percent()
            if usage < self.threshold_percent:
                return True
            logger.warning(f"VRAM usage high ({usage:.1f}%). Waiting...")
            time.sleep(check_interval)
            
        logger.error("VRAM wait timeout exceeded.")
        return False
