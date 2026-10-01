import logging
from ..distributed.workload_estimator import WorkloadEstimator

logger = logging.getLogger(__name__)

class TaskPredictor:
    """
    Predicts task characteristics for the scheduler.
    Wraps the workload estimator to provide scheduling-specific signals.
    """
    
    def analyze_task(self, task_type: str, payload: dict) -> dict:
        """Return a dict of predictions for the given task payload."""
        quality = payload.get("quality_tier", "high")
        duration_units = payload.get("duration_seconds", 60.0) / 60.0 # scale base unit
        
        vram = WorkloadEstimator.estimate_vram(task_type, quality)
        exec_time = WorkloadEstimator.estimate_duration(task_type, duration_units)
        
        requires_ai_video = payload.get("use_ai_video", False) or task_type == "ai_video_generation"
        
        return {
            "vram_mb": vram,
            "estimated_seconds": exec_time,
            "requires_ai_video": requires_ai_video,
            "queue_tier": self._determine_queue(task_type, vram, exec_time)
        }

    def _determine_queue(self, task_type: str, vram: int, exec_time: float) -> str:
        if vram > 10000 or task_type == "ai_video_generation":
            return "gpu_heavy_queue"
        elif vram > 0:
            return "gpu_light_queue"
        elif task_type in ["upload", "download"]:
            return "upload_queue"
        elif exec_time < 5.0:
            return "realtime_queue"
        else:
            return "cpu_queue"
