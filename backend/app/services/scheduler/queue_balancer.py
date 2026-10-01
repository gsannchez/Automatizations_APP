import logging
from typing import List

logger = logging.getLogger(__name__)

class QueueBalancer:
    """
    Monitors queue depths and redistributes tasks if a specific queue
    is deadlocked or overwhelmed.
    """
    def __init__(self, redis_client):
        self.redis = redis_client

    async def get_queue_depth(self, queue_name: str) -> int:
        """Fetch the length of a Celery queue from Redis."""
        # Celery stores list queues in redis by name by default
        return await self.redis.llen(queue_name)

    async def rebalance_if_needed(self, threshold: int = 100):
        """
        Check if any queue is overwhelmed. If so, potentially trigger
        autoscaling hints or downgrade logic.
        """
        heavy_depth = await self.get_queue_depth("gpu_heavy_queue")
        light_depth = await self.get_queue_depth("gpu_light_queue")

        if heavy_depth > threshold and light_depth < (threshold // 4):
            logger.warning(f"[QueueBalancer] Heavy queue overwhelmed ({heavy_depth}). Suggesting downgrade for new tasks.")
            return True # Suggest downgrade
            
        return False
