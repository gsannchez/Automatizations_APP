import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class PriorityManager:
    """
    Manages task priorities based on tenant tiers and system load.
    Tiers: enterprise (1), pro (5), free (10)
    Lower number = higher priority
    """
    TENANT_BASE_PRIORITY = {
        "enterprise": 1,
        "pro": 5,
        "free": 10
    }

    def calculate_priority(self, tenant_tier: str, is_recovery: bool = False, time_in_queue: int = 0) -> int:
        """Calculate the absolute priority score for Celery routing."""
        base = self.TENANT_BASE_PRIORITY.get(tenant_tier, 10)
        
        # Recovery tasks jump the queue
        if is_recovery:
            base = max(0, base - 5)
            
        # Prevent starvation: decrease priority number (increase priority) 
        # if waiting too long (e.g. -1 for every 5 mins)
        starvation_bonus = time_in_queue // 300
        
        final_priority = max(0, base - starvation_bonus)
        return final_priority
