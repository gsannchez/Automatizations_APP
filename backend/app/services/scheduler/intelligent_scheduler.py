import logging
from typing import Dict, Any

from .task_predictor import TaskPredictor
from .execution_router import ExecutionRouter
from .priority_manager import PriorityManager
from .queue_balancer import QueueBalancer
from ..distributed.node_selector import NodeSelector

logger = logging.getLogger(__name__)

class IntelligentScheduler:
    """
    The main entry point for the Smart Scheduler layer.
    Coordinates prediction, routing, priority, and node selection.
    """
    def __init__(self, redis_client, node_registry):
        self.predictor = TaskPredictor()
        self.router = ExecutionRouter()
        self.priority_mgr = PriorityManager()
        self.balancer = QueueBalancer(redis_client)
        self.node_selector = NodeSelector(node_registry)

    async def schedule_task(self, task_name: str, payload: Dict[str, Any], tenant_tier: str = "free", is_recovery: bool = False) -> Dict[str, Any]:
        """
        Calculates all routing and priority parameters for a task.
        """
        # 1. Predict footprint
        predictions = self.predictor.analyze_task(task_name, payload)
        
        # 2. Check for overwhelming queues
        should_downgrade = await self.balancer.rebalance_if_needed()
        if should_downgrade and predictions["vram_mb"] > 0:
            logger.info(f"[Scheduler] Downgrading {task_name} quality due to queue load.")
            # Recalculate with lower quality
            payload["quality_tier"] = "medium"
            predictions = self.predictor.analyze_task(task_name, payload)

        # 3. Select node (for direct execution hints)
        capability = "ai_video" if predictions["requires_ai_video"] else None
        target_node = await self.node_selector.select_best_node(predictions["vram_mb"], capability)

        # 4. Determine final queue & priority
        queue_name = self.router.route_task(task_name, predictions, is_recovery)
        priority = self.priority_mgr.calculate_priority(tenant_tier, is_recovery)

        schedule_plan = {
            "task_name": task_name,
            "target_queue": queue_name,
            "priority": priority,
            "predicted_vram": predictions["vram_mb"],
            "predicted_duration": predictions["estimated_seconds"],
            "target_node_id": target_node.node_id if target_node else None
        }
        
        logger.info(f"[Scheduler] Scheduled {task_name} -> {queue_name} (Priority {priority})")
        return schedule_plan
