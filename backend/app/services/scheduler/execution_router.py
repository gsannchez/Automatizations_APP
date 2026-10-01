import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class ExecutionRouter:
    """
    Routes tasks to appropriate Celery queues based on TaskPredictor output.
    """
    VALID_QUEUES = [
        "realtime_queue",
        "gpu_heavy_queue",
        "gpu_light_queue",
        "cpu_queue",
        "upload_queue",
        "recovery_queue"
    ]

    def route_task(self, task_name: str, predictions: Dict[str, Any], is_recovery: bool = False) -> str:
        """Determine final queue name."""
        if is_recovery:
            return "recovery_queue"
            
        target_queue = predictions.get("queue_tier", "cpu_queue")
        
        # Fallback validation
        if target_queue not in self.VALID_QUEUES:
            logger.warning(f"[ExecutionRouter] Invalid queue {target_queue}, falling back to cpu_queue")
            target_queue = "cpu_queue"
            
        logger.debug(f"[ExecutionRouter] Task {task_name} routed to {target_queue}")
        return target_queue
